
from sklearn.preprocessing import MinMaxScaler
from app.constants import convert_to_description, marital_status_sex_encoder
from joblib import load
import numpy as np
import pandas as pd
import random
import hashlib
import shap 

def generate_name_from_id(id_str):
    # Ensure the input is a 6-character string
    if len(id_str) != 6:
        raise ValueError("ID must be a 6-character string")
    
    # Use a hashing algorithm to create a unique, reproducible seed
    hash_object = hashlib.sha256(id_str.encode())
    hex_dig = hash_object.hexdigest()
    
    # Use the hash to seed the random number generator
    seed = int(hex_dig[:8], 16)
    random.seed(seed)
    
    # Generate a unique name based on the seed
    first_names = ["Alex", "Jamie", "Chris", "Taylor", "Jordan", "Morgan", "Robin", "Casey", "Avery", "Skyler"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)

    return f"{first_name} {last_name}"

log_reg = load('./dumps/log_reg.joblib')

pl_prod = load('./dumps/pl_prod.joblib')

explainer = load('./dumps/explainer.joblib')


def predict(input):

    person_id = input['person_id']

    del input['person_id']

    input_df = pd.DataFrame(input)

    transformed_input = pl_prod.transform(input_df)

    prediction = log_reg.predict_proba(transformed_input)

    feature_names = [ f_name.split('__')[1] for f_name in pl_prod.get_feature_names_out()]

    feature_names = [convert_to_description(f_name) for f_name in feature_names]

    # Correct way to get predictions
    # pred = log_reg.predict(transformed_input)

    # Create DMatrix for SHAP TreeExplainer
    # Xd = DMatrix(transformed_input, label=pred)
    
    # Generate SHAP explanation
    # explainer = shap.TreeExplainer(log_reg)
    # explanation = explainer(Xd)

    explanation = explainer(np.array(transformed_input))

    prediction = [{
        'customer_id': person_id[0],
        'customer_name': generate_name_from_id(person_id[0]),
        'proba': float(pred[np.argmax(pred)]),
        # 'prediction': "Possible Non Defaulter" if int(np.argmax(pred)) == 0 else "Possible Defaulter",
        'prediction': "Possible Defaulter" if int(np.argmax(pred)) == 0 else "Possible Non Defaulter",
        # 'model_decision': f"{generate_name_from_id(person_id[0])} is {'not likely to default' if np.argmax(pred) == 0 else 'likely to default'} with {(float(pred[np.argmax(pred)])*100):.4f}% probability",
        'model_decision': f"{generate_name_from_id(person_id[0])} is {'likely to default' if np.argmax(pred) == 0 else 'not likely to default'} with {(float(pred[np.argmax(pred)])*100):.4f}% probability",
        'shap_explanation': dict(zip(feature_names ,[float(val) for val in explanation.values[0]])),
        'base_value': float(explanation.base_values[0]),
        # 'global_importances': dict(zip(feature_names ,[float(val) for val in global_importances]))
        'global_importances': dict(zip(feature_names ,[float(val) for val in log_reg.coef_[0]])),
        # 'global_importances': dict(zip(feature_names ,[val for k,val in log_reg.get_booster().get_score(importance_type='weight').items()]))
    } for pred in prediction]

    return prediction


# Reverse mappings dictionary for encoding
reversedMappings = {
  "Less than 0 GHS": "A11",
  "Between 0 and 200 GHS": "A12",
  "200 or more GHS": "A13",
  "No account": "A14",
  "No credits all paid": "A30",
  "All credits paid here": "A31",
  "Credits paid till now": "A32",
  "Delay in past": "A33",
  "Critical other credits": "A34",
  "Car new": "A40",
  "Car used": "A41",
  "Furniture/equipment": "A42",
  "Radio/TV": "A43",
  "Domestic appliances": "A44",
  "Repairs": "A45",
  "Education": "A46",
  "Vacation": "A47",
  "Retraining": "A48",
  "Business": "A49",
  "Others": "A410",
  "Less than 100 GHS": "A61",
  "Between 100 and 500 GHS": "A62",
  "Between 500 and 1000 GHS": "A63",
  "1000 or more GHS": "A64",
  "Unknown/no savings": "A65",
  "Unemployed": "A71",
  "Less than 1 year": "A72",
  "Between 1 and 4 years": "A73",
  "Between 4 and 7 years": "A74",
  "7 or more years": "A75",
  "None": "A101",
  "Co-applicant": "A102",
  "Guarantor": "A103",
  "Real estate": "A121",
  "Building/savings life insurance": "A122",
  "Car/other": "A123",
  "Unknown/no property": "A124",
  "Bank": "A141",
  "Stores": "A142",
  "Rent": "A151",
  "Own": "A152",
  "For free": "A153",
  "Unemployed/unskilled non-resident": "A171",
  "Unskilled resident": "A172",
  "Skilled employee/official": "A173",
  "Management/self-employed/high qualified": "A174",
  "Yes, registered": "A192",
  "Yes": "A201",
  "No": "A202"
}


def transform_input_data(input_item):
    return {
        'status_of_existing_checking_account': reversedMappings.get(input_item.get('status_of_existing_checking_account')),
        'duration': input_item.get('duration'),
        'credit_history': reversedMappings.get(input_item.get('credit_history')),
        'purpose': reversedMappings.get(input_item.get('purpose')),
        'credit_amount': input_item.get('credit_amount'),
        'savings_account_bonds': reversedMappings.get(input_item.get('savings_account_bonds')),
        'present_employment_since': reversedMappings.get(input_item.get('present_employment_since')),
        'installment_rate_in_percentage_of_disposable_income': input_item.get('installment_rate_in_percentage_of_disposable_income'),
        'personal_status_and_sex': marital_status_sex_encoder(input_item.get('marital_status'), input_item.get('sex')),
        'other_debtors_guarantors': reversedMappings.get(input_item.get('other_debtors_guarantors')),
        'present_residence_since': input_item.get('present_residence_since'),
        'property': reversedMappings.get(input_item.get('property')),
        'age': input_item.get('age'),
        'other_installment_plans': reversedMappings.get(input_item.get('other_installment_plans')),
        'housing': reversedMappings.get(input_item.get('housing')),
        'number_of_existing_credits_at_this_bank': input_item.get('number_of_existing_credits_at_this_bank'),
        'job': reversedMappings.get(input_item.get('job')),
        'number_of_people_being_liable_to_provide_maintenance_for': input_item.get('number_of_people_being_liable_to_provide_maintenance_for'),
        'telephone': reversedMappings.get(input_item.get('telephone')),
        'foreign_worker': reversedMappings.get(input_item.get('foreign_worker'))
    }

def predict_list_lite(input):
    '''
    This function supports db data and does the encoding and transformation here
    '''
    transformed_data = []
    
    # Transform each input record using the reversedMappings
    for input_item in input:
        
        # Transform the input data using the reverse mappings
        transformed_data.append(transform_input_data(input_item))
    
    # print('\n\nINPUT:')
    # print(input[0])
    # print('\n\nTRANSFORMED:')
    # print(transformed_data[0])

    input_dict = {}

    # Accumulate transformed data into lists for each key
    for transformed_item in transformed_data:
        for k, v in transformed_item.items():
            if k not in input_dict:
                input_dict[k] = []
            input_dict[k].append(v)
    

    # Convert the dictionary to a DataFrame
    input_df = pd.DataFrame(input_dict)

    # Apply the transformations (as per your original flow)
    transformed_input = pl_prod.transform(input_df)

    # Predict the probabilities
    prediction = log_reg.predict_proba(transformed_input)

    # Format the prediction response
    prediction = [{
        'repayment_proba': float(pred[1]),
        'default_proba': float(pred[0]),
    } for pred in prediction]

    return prediction


def predict_lite(input):

    person_id = input['person_id']

    del input['person_id']

    input_df = pd.DataFrame(input)

    transformed_input = pl_prod.transform(input_df)

    prediction = log_reg.predict_proba(transformed_input)

    prediction = [{
        'repayment_proba': float(pred[1]),
        'default_proba': float(pred[0]),
    } for pred in prediction]

    return prediction