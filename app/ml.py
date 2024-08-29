
from sklearn.preprocessing import MinMaxScaler
from app.constants import convert_to_description
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