import random

def marital_status_sex_decoder(code):
    result = {}

    if code == 'A91':
        result['sex'] = 'male'
        result['marital_status'] = random.choice(['divorced', 'separated'])
    elif code == 'A92':
        result['sex'] = 'female'
        result['marital_status'] = random.choice(['divorced', 'separated', 'married'])
    elif code == 'A93':
        result['sex'] = 'male'
        result['marital_status'] = 'single'
    elif code == 'A94':
        result['sex'] = 'male'
        result['marital_status'] = random.choice(['married', 'widowed'])
    elif code == 'A95':
        result['sex'] = 'female'
        result['marital_status'] = 'single'
    else:
        raise ValueError(f"Unknown code: {code}")
    
    return result

mapping = {
    "A11": "Less than 0 GHS",
    "A12": "Between 0 and 200 GHS",
    "A13": "200 or more GHS",
    "A14": "No account",
    "A30": "No credits all paid",
    "A31": "All credits paid here",
    "A32": "Credits paid till now",
    "A33": "Delay in past",
    "A34": "Critical other credits",
    "A40": "Car new",
    "A41": "Car used",
    "A42": "Furniture/equipment",
    "A43": "Radio/TV",
    "A44": "Domestic appliances",
    "A45": "Repairs",
    "A46": "Education",
    "A47": "Vacation",
    "A48": "Retraining",
    "A49": "Business",
    "A410": "Others",
    "A61": "Less than 100 GHS",
    "A62": "Between 100 and 500 GHS",
    "A63": "Between 500 and 1000 GHS",
    "A64": "1000 or more GHS",
    "A65": "Unknown/no savings",
    "A71": "Unemployed",
    "A72": "Less than 1 year",
    "A73": "Between 1 and 4 years",
    "A74": "Between 4 and 7 years",
    "A75": "7 or more years",
    "A91": "male : divorced/separated",
    "A92": "female : divorced/separated/married",
    "A93": "male : single",
    "A94": "male : married/widowed",
    "A95": "female : single",
    "A101": "None",
    "A102": "Co-applicant",
    "A103": "Guarantor",
    "A121": "Real estate",
    "A122": "Building/savings life insurance",
    "A123": "Car/other",
    "A124": "Unknown/no property",
    "A141": "Bank",
    "A142": "Stores",
    "A143": "None",
    "A151": "Rent",
    "A152": "Own",
    "A153": "For free",
    "A171": "Unemployed/unskilled non-resident",
    "A172": "Unskilled resident",
    "A173": "Skilled employee/official",
    "A174": "Management/self-employed/high qualified",
    "A191": "None",
    "A192": "Yes, registered",
    "A201": "Yes",
    "A202": "No",
}

def marital_status_sex_encoder(marital_status, sex):
    sex = sex.strip().lower()
    marital_status = marital_status.strip().lower()
    if sex == 'male':
        if marital_status == 'divorced' or marital_status == 'separated':
            return 'A91'
        elif marital_status == 'single':
            return 'A93'
        elif marital_status == 'married' or marital_status == 'widowed':
            return 'A94'
    elif sex == 'female':
        if marital_status == 'divorced' or marital_status == 'separated' or marital_status == 'married':
            return 'A92'
        elif marital_status == 'single':
            return 'A95'


def convert_to_description(feature_name):
    splits = feature_name.split('_')
    if len(splits)<2:
        return feature_name

    if mapping.get(splits[-1], 'invalid') != 'invalid':
        return f"{'_'.join(splits[:-1])} [{mapping[splits[-1]]}]"
    else:
        return feature_name

attribute_mapping = {
    "status_of_existing_checking_account": {
        "less_than_0_ghs": "A11",
        "between_0_and_200k_ghs": "A12",
        "200k_or_more_ghs": "A13",
        "no_account": "A14"
    },
    "duration_in_month": "numerical",
    "credit_history": {
        "no_credits_all_paid": "A30",
        "all_credits_paid_here": "A31",
        "credits_paid_till_now": "A32",
        "delay_in_past": "A33",
        "critical_other_credits": "A34"
    },
    "purpose": {
        "car_new": "A40",
        "car_used": "A41",
        "furniture_equipment": "A42",
        "radio_tv": "A43",
        "domestic_appliances": "A44",
        "repairs": "A45",
        "education": "A46",
        "vacation": "A47",
        "retraining": "A48",
        "business": "A49",
        "others": "A410"
    },
    "credit_amount": "numerical",
    "savings_account_bonds": {
        "less_than_100_dm": "A61",
        "between_100_and_500_dm": "A62",
        "between_500_and_1000_dm": "A63",
        "1000_or_more_dm": "A64",
        "unknown_no_savings": "A65"
    },
    "present_employment_since": {
        "unemployed": "A71",
        "less_than_1_year": "A72",
        "between_1_and_4_years": "A73",
        "between_4_and_7_years": "A74",
        "7_or_more_years": "A75"
    },
    "installment_rate_in_percentage_of_disposable_income": "numerical",
    "personal_status_and_sex": {
        "male_divorced_separated": "A91",
        "female_divorced_separated_married": "A92",
        "male_single": "A93",
        "male_married_widowed": "A94",
        "female_single": "A95"
    },
    "other_debtors_guarantors": {
        "none": "A101",
        "co_applicant": "A102",
        "guarantor": "A103"
    },
    "present_residence_since": "numerical",
    "property": {
        "real_estate": "A121",
        "building_savings_life_insurance": "A122",
        "car_other": "A123",
        "unknown_no_property": "A124"
    },
    "age_in_years": "numerical",
    "other_installment_plans": {
        "bank": "A141",
        "stores": "A142",
        "none": "A143"
    },
    "housing": {
        "rent": "A151",
        "own": "A152",
        "for_free": "A153"
    },
    "number_of_existing_credits_at_this_bank": "numerical",
    "job": {
        "unemployed_unskilled_non_resident": "A171",
        "unskilled_resident": "A172",
        "skilled_employee_official": "A173",
        "management_self_employed_high_qualified": "A174"
    },
    "number_of_people_being_liable_to_provide_maintenance_for": "numerical",
    "telephone": {
        "none": "A191",
        "yes_registered": "A192"
    },
    "foreign_worker": {
        "yes": "A201",
        "no": "A202"
    }
}