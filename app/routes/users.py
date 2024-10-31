from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Users
from app.schemas.user import UserCreate, UserLogin, ShowUser
from app.utils.pwd import hash_password, verify_password

router = APIRouter()

# Create a new user (register)
@router.post("/register", response_model=ShowUser)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    user_in_db = db.query(Users).filter(Users.email == user.email).first()
    if user_in_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user with hashed password
    hashed_password = hash_password(user.password)
    new_user = Users(email=user.email, password=hashed_password, role=user.role)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# User login (authentication)
@router.post("/login", response_model=ShowUser)
def login(user: UserLogin, db: Session = Depends(get_db)):
    user_in_db = db.query(Users).filter(Users.email == user.email).first()

    if not user_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not verify_password(user.password, user_in_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return user_in_db
