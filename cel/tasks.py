from sqlalchemy.orm import Session
from cel.celery_app import celery_app
from app.db.database import get_db
from app.db.models.loan_applications import LoanApplications
from app.db.models.products import Product
from app.db.models.customers import Customers
from sqlalchemy.orm import aliased
from sqlalchemy import func, or_, and_, not_
from app.ml import predict_list_lite
from datetime import datetime
import json
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from app.core.config import settings

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sqlalchemy.dialects.postgresql import JSONB
from celery.utils.log import get_task_logger

import requests

logger = get_task_logger(__name__)



class LoanApplicationResponse(BaseModel):
    id: int
    status_of_existing_checking_account: str
    credit_history: str
    savings_account_bonds: str
    present_employment_since: str
    installment_rate_in_percentage_of_disposable_income: int
    other_debtors_guarantors: str
    present_residence_since: int
    property: str
    other_installment_plans: str
    housing: str
    number_of_existing_credits_at_this_bank: int
    job: str
    number_of_people_being_liable_to_provide_maintenance_for: int
    customer: Optional[dict] = None
    nc_info: Optional[dict] = None
    repayment_proba: float

    class Config:
        orm_mode = True

# Recursive filter builder
def build_filter_query(filter_obj, model, customer_alias, nc_info_column):
    if 'attribute' in filter_obj:
        attribute = filter_obj['attribute']
        operation = filter_obj['operation']
        operand = filter_obj['operand']

        # Check where the attribute resides: LoanApplications, nc_info (JSONB), or Customers
        if hasattr(model, attribute):
            column = getattr(model, attribute)  # Attribute is in LoanApplications
        elif hasattr(customer_alias, attribute):
            column = getattr(customer_alias, attribute)  # Attribute is in Customers
        elif isinstance(nc_info_column, JSONB):
            column = nc_info_column[attribute]  # Attribute is in nc_info JSONB
        else:
            raise AttributeError(f"Attribute '{attribute}' not found in any table")

        # Build SQLAlchemy filter conditions for each operation
        if operation == 'eq':
            return column == operand
        elif operation == 'lt':
            return column < operand
        elif operation == 'lte':
            return column <= operand
        elif operation == 'gt':
            return column > operand
        elif operation == 'gte':
            return column >= operand
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    # Handle logical operators ('and', 'or', 'not')
    elif 'and' in filter_obj:
        return and_(*[build_filter_query(f, model, customer_alias, nc_info_column) for f in filter_obj['and']])
    elif 'or' in filter_obj:
        return or_(*[build_filter_query(f, model, customer_alias, nc_info_column) for f in filter_obj['or']])
    elif 'not' in filter_obj:
        return not_(build_filter_query(filter_obj['not'][0], model, customer_alias, nc_info_column))
    
    raise ValueError("Invalid filter structure")

@celery_app.task
def process_eligible_customers(product_id, filters, type, limit):
    # Create a new session for the task
    db = next(get_db())

    # Step 1: Retrieve the product and set its processing status to True
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise Exception("Product not found")

    # Set the processing flag to True and commit
    product.processing = True
    db.commit()

    try:
        # Step 2: Subquery to get the latest loan application for each customer
        subquery = db.query(
            LoanApplications.customer_id,
            func.max(LoanApplications.date_created).label('latest_application_date')
        ).group_by(LoanApplications.customer_id).subquery()

        # Step 3: Query for loan applications with customer_id, filtering by the latest application per customer
        query = db.query(LoanApplications).outerjoin(
            subquery,
            and_(
                LoanApplications.customer_id == subquery.c.customer_id,
                LoanApplications.date_created == subquery.c.latest_application_date
            )
        )

        # Step 4: Add all loan applications without a customer_id if type is not "customer"
        if not type == "customer":
            query = query.union_all(
                db.query(LoanApplications).filter(LoanApplications.customer_id == None)
            )

        # Step 5: Apply filters only if they exist
        customer_alias = aliased(Customers)
        if filters:
            query = query.outerjoin(customer_alias, LoanApplications.customer_id == customer_alias.id)
            query = query.filter(build_filter_query(filters, LoanApplications, customer_alias, LoanApplications.nc_info))

        # Step 6: Execute query and fetch the results
        loan_applications = query.all()

        if not loan_applications:
            return []

        # Step 7: Prepare data for the ML model
        input_data = []
        for application in loan_applications:
            customer = application.customer
            input_data.append({
                'person_id': "123456",
                'id': application.id,
                'status_of_existing_checking_account': application.status_of_existing_checking_account,
                'duration': product.duration,
                'credit_history': application.credit_history,
                'purpose': product.purpose,
                'credit_amount': product.credit_amount,
                'savings_account_bonds': application.savings_account_bonds,
                'present_employment_since': application.present_employment_since,
                'installment_rate_in_percentage_of_disposable_income': application.installment_rate_in_percentage_of_disposable_income,
                'marital_status': customer.marital_status if customer else application.nc_info.get('marital_status'),
                'sex': customer.sex if customer else application.nc_info.get('sex'),
                'other_debtors_guarantors': application.other_debtors_guarantors,
                'present_residence_since': application.present_residence_since,
                'property': application.property,
                'age': customer.age if customer else application.nc_info.get('age'),
                'other_installment_plans': application.other_installment_plans,
                'housing': application.housing,
                'number_of_existing_credits_at_this_bank': application.number_of_existing_credits_at_this_bank,
                'job': application.job,
                'number_of_people_being_liable_to_provide_maintenance_for': application.number_of_people_being_liable_to_provide_maintenance_for,
                'telephone': customer.telephone if customer else application.nc_info.get('telephone'),
                'foreign_worker': customer.foreign_worker if customer else application.nc_info.get('foreign_worker')
            })

        # Step 8: Get predictions from the ML model
        predictions = predict_list_lite(input_data)

        # Step 9: Combine predictions with the original data
        for i, application in enumerate(loan_applications):
            application.repayment_proba = predictions[i]['repayment_proba']

        # Step 10: Sort and limit results
        sorted_applications = sorted(loan_applications, key=lambda x: x.repayment_proba, reverse=True)
        if limit:
            sorted_applications = sorted_applications[:limit]

        response_data = []
        for application in sorted_applications:
            customer = application.customer

            # Populate customer or nc_info as a nested dictionary
            customer_data = {
                "id": customer.id,
                "full_name": customer.full_name,
                "sex": customer.sex,
                "age": customer.age,
                "email": customer.email,
                "mobile": customer.mobile,
                "marital_status": customer.marital_status,
                "telephone": customer.telephone,
                "foreign_worker": customer.foreign_worker,
                "income": customer.income,
            } if customer else None

            # Append the loan application data to the response
            rsp = LoanApplicationResponse(
                id=application.id,
                status_of_existing_checking_account=application.status_of_existing_checking_account,
                credit_history=application.credit_history,
                savings_account_bonds=application.savings_account_bonds,
                present_employment_since=application.present_employment_since,
                installment_rate_in_percentage_of_disposable_income=application.installment_rate_in_percentage_of_disposable_income,
                other_debtors_guarantors=application.other_debtors_guarantors,
                present_residence_since=application.present_residence_since,
                property=application.property,
                other_installment_plans=application.other_installment_plans,
                housing=application.housing,
                number_of_existing_credits_at_this_bank=application.number_of_existing_credits_at_this_bank,
                job=application.job,
                number_of_people_being_liable_to_provide_maintenance_for=application.number_of_people_being_liable_to_provide_maintenance_for,
                customer=customer_data,  # Populate customer field as a dictionary
                nc_info=application.nc_info if not customer else None,  # Populate nc_info if customer doesn't exist
                repayment_proba=application.repayment_proba  # ML Model Prediction
            )
            response_data.append(rsp)

        print(f"Prepared response data for {len(response_data)} loan applications")

        def json_serializable(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()  # Convert datetime to ISO 8601 string format
            elif isinstance(obj, Decimal):
                return float(obj)  # Convert Decimal to float
            raise TypeError(f"Type {type(obj)} not serializable")

        # Step 13: Store the response_data in the product's eligible_customers field
        try:
            # Before storing, serialize the response_data to handle datetime and Decimal
            serialized_data = json.dumps([rsp.dict() for rsp in response_data], default=json_serializable)
            product.eligible_customers = json.loads(serialized_data)
            db.commit()
        except Exception as e:
            return {"status": "failed", "message": f"Error saving eligible customers: {e}", "product_id": product_id}

    finally:
        # Set the processing status to False after completion or failure
        product.processing = False
        db.commit()

    return {"status": "completed", "product_id": product_id}


# Create a Celery app instance (assuming it's already configured in your celery_app.py)
@celery_app.task
def contact_eligible_customers(product_id):
    # Create a new session for the task
    db = next(get_db())

    # Step 1: Retrieve the product and check if it exists
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise Exception("Product not found")

    # Retrieve eligible customers from the product
    eligible_customers = product.eligible_customers

    if not eligible_customers or len(eligible_customers) == 0:
        raise Exception("No eligible customers found for this product")

    # Define email sender details
    smtp_host = "smtp.gmail.com"  # For example, Gmail's SMTP server
    smtp_port = 587
    sender_email = "kkorankye@itconsortiumgh.com"  # Replace with your email
    sender_password = settings.EMAIL_APP_PASS  # Replace with your email password

    # Set up the SMTP server
    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Step 2: Loop through eligible customers and send emails
        for customer_data in eligible_customers:
            customer = customer_data.get('customer', customer_data.get('nc_info'))
            print(customer_data)
            recipient_email = customer.get('email')
            if recipient_email:
                # Create the email content
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient_email
                msg['Subject'] = f"Exclusive Offer for {product.name}"

                # Email body (you can customize this as needed)
                body = f"Dear {customer.get('full_name', 'Customer')},\n\n"
                body += f"You are eligible for an exclusive offer for our product: {product.name}.\n"
                body += "Please contact us for more information.\n\nBest regards,\nITC Credit"
                msg.attach(MIMEText(body, 'plain'))

                # Send the email
                server.send_message(msg)
                print(f"Email sent to {recipient_email}")

                url = "http://52.89.222.13/tfsg/public/api/send"
                json_data = {"api_key": "ebow:baby",
                            "merchant_id": 1,
                            "message": body,
                            "recipients": [customer.get('mobile')]}
                response = requests.post(url, json=json_data)
                print(response)

    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
        raise Exception(f"Error sending emails: {e}")
    
    except Exception as e:
        print(e)

    finally:
        # Close the server connection
        print('Done')
        server.quit()

    return {"status": "completed", "product_id": product_id}

