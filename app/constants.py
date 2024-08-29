def convert_to_description(feature_name):
    splits = feature_name.split('_')
    if len(splits)<2:
        return feature_name
        
    mapping = {
        'A11': '< 0 DM',
        'A12': '0 <= ... < 200 DM',
        'A13': '... >= 200 DM / salary assignments for at least 1 year',
        'A14': 'no checking account',
        'A30': 'no credits taken/ all credits paid back duly',
        'A31': 'all credits at this bank paid back duly',
        'A32': 'existing credits paid back duly till now',
        'A33': 'delay in paying off in the past',
        'A34': 'critical account/ other credits existing (not at this bank)',
        'A40': 'car (new)',
        'A41': 'car (used)',
        'A42': 'furniture/equipment',
        'A43': 'radio/television',
        'A44': 'domestic appliances',
        'A45': 'repairs',
        'A46': 'education',
        'A47': 'vacation',
        'A48': 'retraining',
        'A49': 'business',
        'A410': 'others',
        'A61': '< 100 DM',
        'A62': '100 <= ... < 500 DM',
        'A63': '500 <= ... < 1000 DM',
        'A64': '... >= 1000 DM',
        'A65': 'unknown/ no savings account',
        'A71': 'unemployed',
        'A72': '< 1 year',
        'A73': '1 <= ... < 4 years',
        'A74': '4 <= ... < 7 years',
        'A75': '... >= 7 years',
        'A91': 'male : divorced/separated',
        'A92': 'female : divorced/separated/married',
        'A93': 'male : single',
        'A94': 'male : married/widowed',
        'A95': 'female : single',
        'A101': 'none',
        'A102': 'co-applicant',
        'A103': 'guarantor',
        'A121': 'real estate',
        'A122': 'building society savings agreement/ life insurance',
        'A123': 'car or other, not in attribute 6',
        'A124': 'unknown / no property',
        'A141': 'bank',
        'A142': 'stores',
        'A143': 'none',
        'A151': 'rent',
        'A152': 'own',
        'A153': 'for free',
        'A171': 'unemployed/ unskilled - non-resident',
        'A172': 'unskilled - resident',
        'A173': 'skilled employee / official',
        'A174': 'management/ self-employed/ highly qualified employee/ officer',
        'A191': 'none',
        'A192': 'yes, registered under the customer\'s name',
        'A201': 'yes',
        'A202': 'no'
    }


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