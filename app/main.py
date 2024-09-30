import random
import shutil
from typing import Optional
from app.ml import predict, predict_lite
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator, root_validator
from typing import List
from app.constants import marital_status_sex_encoder

from fastapi import FastAPI
from app.routes import gapplicant, loanee, product, loans, loan_applications, fx
import json

def load_json_as_dict(json_file_path: str) -> dict:
    """
    Loads a JSON file and returns its contents as a Python dictionary.

    :param json_file_path: Path to the JSON file.
    :return: A dictionary containing the JSON data.
    """
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data

# Example usage
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestBody(BaseModel):
    person_id: str
    id: Optional[int] = None
    status_of_existing_checking_account: str
    duration: int
    credit_history: str
    purpose: str
    credit_amount: float
    savings_account_bonds: str
    present_employment_since: str
    installment_rate_in_percentage_of_disposable_income: float
    personal_status_and_sex: Optional[str] = None 
    marital_status: Optional[str] = None 
    sex: Optional[str] = None 
    other_debtors_guarantors: str
    present_residence_since: int
    property: str
    age: int
    other_installment_plans: str
    housing: str
    number_of_existing_credits_at_this_bank: int
    job: str
    number_of_people_being_liable_to_provide_maintenance_for: int
    telephone: str
    foreign_worker: str

    @validator("person_id")
    def validate_person_id(cls, value):
        if len(value) != 6:
            raise ValueError("Invalid person_id: must be exactly 6 characters long")
        return value
    
    @root_validator(pre=True)
    def create_personal_status_and_sex(cls, values):
        marital_status = values.get('marital_status')
        sex = values.get('sex')
        personal_status_and_sex = values.get('personal_status_and_sex')
        if not personal_status_and_sex and marital_status and sex:
            values['personal_status_and_sex'] = marital_status_sex_encoder(marital_status=marital_status, sex=sex)
        return values


# Include the routers
app.include_router(gapplicant.router, prefix="/gapplicants", tags=["GApplicants"])
app.include_router(loanee.router, prefix="/loanees", tags=["Loanees"])
app.include_router(loans.router, prefix="/loans", tags=["Loans"])
app.include_router(loan_applications.router, prefix="/loan-applications", tags=["Loan Applications"])
app.include_router(product.router, prefix="/products", tags=["Products"])
app.include_router(fx.router, prefix="/fx", tags=["Functions"])

@app.get("/")
async def root():
    return {"message": "Successful"}

@app.get("/graph-data")
def get_graph_data():
    data = load_json_as_dict('data.json')
    return data

@app.post("/predict/")
def make_prediction(input: RequestBody):
    try:
        input_dict = {k: [v] for k, v in input.dict().items()}
        prediction = predict(input_dict)
        return prediction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/predict-many/")
def make_prediction(input: List[RequestBody]):
    try:
        # Initialize an empty dictionary to accumulate input data
        input_dict = {}
        
        # Loop through each dictionary in the input list
        for input_item in input:
            for k, v in input_item.dict().items():
                # Accumulate values into lists for each key
                if k not in input_dict:
                    input_dict[k] = []
                input_dict[k].append(v)

        # Pass the accumulated dictionary to the predict function
        prediction = predict_lite(input_dict)
        
        return prediction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
