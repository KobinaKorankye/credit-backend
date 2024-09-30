from fastapi import APIRouter, HTTPException, Depends, Request, Response
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models.loanee import Loanee
from app.db.models.products import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.loanee import LoaneeResponse

router = APIRouter()

# Route to get all Products
@router.get("/", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

# Route to create a new Product
@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(**product_data.dict())
    db.add(new_product)
    db.commit()
        
    return new_product


# Route to update an existing Product
@router.put("/", response_model=ProductResponse)
def update_product(product_data: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_data.id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.name = product_data.name
    product.duration = product_data.duration
    product.purpose = product_data.purpose
    product.credit_amount = product_data.credit_amount
    product.filters = product_data.filters  # Handle optional field
    product.eligible_customers = product_data.eligible_customers 
    
    db.commit()
    
    return product

@router.delete("/{product_id}", response_model=ProductResponse)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()

