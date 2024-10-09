from decimal import Decimal
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, or_, and_, not_
from app.db.database import get_db
from app.db.models.loan_applications import LoanApplications
from app.db.models.products import Product
from app.db.models.customers import Customers
from app.schemas.product import ProductResponse
from typing import List, Optional, Dict, Any
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import BaseModel
from datetime import datetime
from app.ml import predict_list_lite

from cel.tasks import process_eligible_customers
from fastapi.responses import StreamingResponse
from celery.result import AsyncResult
import time

router = APIRouter()

# Response schema with customer as a nested dictionary
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


@router.get("/get-eligible/{product_id}", response_model=Dict[str, Any])
async def get_eligible(
    product_id: int,
    type: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    # Trigger the Celery task
    filters = db.query(Product).filter(Product.id == product_id).first().filters
    task = process_eligible_customers.apply_async(args=[product_id, filters, type, limit])
    return {"status": "processing", "task_id": task.id}

from cel.celery_app import celery_app
from fastapi.responses import StreamingResponse
import time
import json

@router.get("/task-status/{task_id}")
async def task_status(task_id: str):
    def event_stream():
        while True:
            task_result = celery_app.AsyncResult(task_id)
            
            # Fetch the state of the task
            task_state = task_result.state
            task_info = task_result.info  # May contain result or exception information
            
            print(f"Task Info: {task_info}, State: {task_state}")  # Debug print
            
            # Prepare the event in SSE format
            if task_state == 'SUCCESS':
                yield f"data: {json.dumps({'task_id': task_id, 'status': 'SUCCESS', 'message': f'Task {task_id} completed successfully.', 'result': task_info})}\n\n"
                break
            elif task_state == 'FAILURE':
                yield f"data: {json.dumps({'task_id': task_id, 'status': 'FAILURE', 'message': f'Task {task_id} failed.', 'result': str(task_info)})}\n\n"
                break
            else:
                # For 'PENDING', 'RETRY', or other states, keep checking
                yield f"data: {json.dumps({'task_id': task_id, 'status': task_state, 'message': f'Task {task_id} is {task_state}.'})}\n\n"
                time.sleep(5)  # Pause between each poll

    return StreamingResponse(event_stream(), media_type="text/event-stream")

# @router.get("/task-status/{task_id}")
# async def task_status(task_id: str):
#     def event_stream():
#         while True:
#             task_result = AsyncResult(task_id)
#             if task_result.state == 'SUCCESS':
#                 yield f"{json.dumps({'task_id': task_id, 'status': 'SUCCESS', 'message': f'Task {task_id} completed successfully.'})}\n\n"
#                 break
#             elif task_result.state == 'FAILURE':
#                 yield f"{json.dumps({'task_id': task_id, 'status': 'FAILURE', 'message': f'Task {task_id} failed.'})}\n\n"
#                 break
#             else:
#                 yield f"{json.dumps({'task_id': task_id, 'status': task_result.state, 'message': f'Task {task_id} is {task_result.state}'})}\n\n"
#             time.sleep(5)

#     return StreamingResponse(event_stream(), media_type="text/event-stream")

# @router.get("/get-eligible/{product_id}", response_model=ProductResponse)
# def get_eligible(
#     product_id: int,  # Product ID from the frontend
#     type: Optional[str] = Query(None, description="The type of people to consider"),  # Optional type query param
#     limit: Optional[int] = Query(None, description="Limit the number of results"),  # Optional limit query param
#     db: Session = Depends(get_db),
# ):
#     # Step 1: Retrieve the product and its associated filters
#     product = db.query(Product).filter(Product.id == product_id).first()

#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")

#     filters = product.filters  # Filters may be null, handle that below
#     print(f"Retrieved filters: {filters}")

#     # Step 2: Subquery to get the latest loan application for each customer
#     subquery = db.query(
#         LoanApplications.customer_id,
#         func.max(LoanApplications.date_created).label('latest_application_date')
#     ).group_by(LoanApplications.customer_id).subquery()

#     # Step 3: Query for loan applications with customer_id, filtering by the latest application per customer
#     query = db.query(LoanApplications).outerjoin(
#         subquery,
#         and_(
#             LoanApplications.customer_id == subquery.c.customer_id,
#             LoanApplications.date_created == subquery.c.latest_application_date
#         )
#     )

#     # Step 4: Add all loan applications without a customer_id if type is not "customer"
#     if not type == "customer":
#         query = query.union_all(
#             db.query(LoanApplications).filter(LoanApplications.customer_id == None)
#         )

#     customer_alias = aliased(Customers)

#     # Step 5: Apply filters only if they exist
#     if filters:
#         print("Applying filters...")
#         try:
#             query = query.outerjoin(customer_alias, LoanApplications.customer_id == customer_alias.id)
#             query = query.filter(build_filter_query(filters, LoanApplications, customer_alias, LoanApplications.nc_info))
#         except Exception as e:
#             print(f"Error applying filters: {e}")
#             raise e

#     # Step 6: Execute query and fetch the results
#     try:
#         loan_applications = query.all()
#     except Exception as e:
#         print(f"Error executing query: {e}")
#         raise e

#     print(f"Fetched {len(loan_applications)} loan applications")

#     if not loan_applications:
#         return []

#     # Step 7: Prepare data for the ML model
#     input_data = []
#     for application in loan_applications:
#         customer = application.customer

#         # Prepare the input data for the ML model based on RequestBody schema
#         input_data.append({
#             'person_id': "123456",  # If no customer_id, use a non-customer identifier
#             'id': application.id,
#             'status_of_existing_checking_account': application.status_of_existing_checking_account,
#             'duration': product.duration,
#             'credit_history': application.credit_history,
#             'purpose': product.purpose,
#             'credit_amount': product.credit_amount,
#             'savings_account_bonds': application.savings_account_bonds,
#             'present_employment_since': application.present_employment_since,
#             'installment_rate_in_percentage_of_disposable_income': application.installment_rate_in_percentage_of_disposable_income,
#             'personal_status_and_sex': None,  # We are assuming this is not available
#             'marital_status': customer.marital_status if customer else application.nc_info.get('marital_status'),
#             'sex': customer.sex if customer else application.nc_info.get('sex'),
#             'other_debtors_guarantors': application.other_debtors_guarantors,
#             'present_residence_since': application.present_residence_since,
#             'property': application.property,
#             'age': customer.age if customer else application.nc_info.get('age'),
#             'other_installment_plans': application.other_installment_plans,
#             'housing': application.housing,
#             'number_of_existing_credits_at_this_bank': application.number_of_existing_credits_at_this_bank,
#             'job': application.job,
#             'number_of_people_being_liable_to_provide_maintenance_for': application.number_of_people_being_liable_to_provide_maintenance_for,
#             'telephone': customer.telephone if customer else application.nc_info.get('telephone'),
#             'foreign_worker': customer.foreign_worker if customer else application.nc_info.get('foreign_worker')
#         })

#     print(f"Prepared input data for {len(input_data)} records")

#     # Step 8: Get predictions from the ML model
#     try:
#         predictions = predict_list_lite(input_data)
#     except Exception as e:
#         print(f"Error in ML model prediction: {e}")
#         raise e

#     # Step 9: Combine predictions with the original data
#     for i, application in enumerate(loan_applications):
#         application.repayment_proba = predictions[i]['repayment_proba']

#     # Step 10: Sort by repayment probability in descending order
#     sorted_applications = sorted(loan_applications, key=lambda x: x.repayment_proba, reverse=True)

#     # Step 11: Apply the limit if provided
#     if limit:
#         sorted_applications = sorted_applications[:limit]

#     # Step 12: Format the response
#     response_data = []
#     for application in sorted_applications:
#         customer = application.customer

#         # Populate customer or nc_info as a nested dictionary
#         customer_data = {
#             "id": customer.id,
#             "full_name": customer.full_name,
#             "sex": customer.sex,
#             "age": customer.age,
#             "marital_status": customer.marital_status,
#             "telephone": customer.telephone,
#             "foreign_worker": customer.foreign_worker,
#             "income": customer.income,
#         } if customer else None

#         # Append the loan application data to the response
#         rsp = LoanApplicationResponse(
#             id=application.id,
#             status_of_existing_checking_account=application.status_of_existing_checking_account,
#             credit_history=application.credit_history,
#             savings_account_bonds=application.savings_account_bonds,
#             present_employment_since=application.present_employment_since,
#             installment_rate_in_percentage_of_disposable_income=application.installment_rate_in_percentage_of_disposable_income,
#             other_debtors_guarantors=application.other_debtors_guarantors,
#             present_residence_since=application.present_residence_since,
#             property=application.property,
#             other_installment_plans=application.other_installment_plans,
#             housing=application.housing,
#             number_of_existing_credits_at_this_bank=application.number_of_existing_credits_at_this_bank,
#             job=application.job,
#             number_of_people_being_liable_to_provide_maintenance_for=application.number_of_people_being_liable_to_provide_maintenance_for,
#             customer=customer_data,  # Populate customer field as a dictionary
#             nc_info=application.nc_info if not customer else None,  # Populate nc_info if customer doesn't exist
#             repayment_proba=application.repayment_proba  # ML Model Prediction
#         )
#         response_data.append(rsp)

#     print(f"Prepared response data for {len(response_data)} loan applications")

#     def json_serializable(obj):
#         if isinstance(obj, datetime):
#             return obj.isoformat()  # Convert datetime to ISO 8601 string format
#         elif isinstance(obj, Decimal):
#             return float(obj)  # Convert Decimal to float
#         raise TypeError(f"Type {type(obj)} not serializable")
    
#     # Step 13: Store the response_data in the product's eligible_customers field
#     try:
#         # Before storing, serialize the response_data to handle datetime and Decimal
#         serialized_data = json.dumps([rsp.dict() for rsp in response_data], default=json_serializable)
#         product.eligible_customers = json.loads(serialized_data)
#         db.commit()
#         print(f"Updated eligible_customers for product ID {product_id}")
#     except Exception as e:
#         print(f"Error saving eligible customers: {e}")
#         raise e

#     return product
