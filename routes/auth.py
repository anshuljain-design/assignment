from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from baseModels.auth_model import SignupModel, LoginModel
from db_models import database, user
from passlib.context import CryptContext
from validators.auth_validators import *

router = APIRouter()

# Set up password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)




@router.post("/signup")
def signup(user_data: SignupModel, db: Session = Depends(get_db)):
    # Make email lowercase
    email = user_data.email.strip().lower()
    name = user_data.name.strip().title()
    password = user_data.password.strip()

    # Validate
    validate_email(email)
    validate_name(name)
    validate_password(password)

    # Check if email already exists
    existing_user = db.query(user.User).filter(user.User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Save new user
    hashed_pw = get_password_hash(password)
    new_user = user.User(
        email=email,
        name=name,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "detail": "User registered successfully",
        "user_id": new_user.id,
        "name": new_user.name
    }



@router.post("/login")
def login(login_data: LoginModel, db: Session = Depends(get_db)):
    # Normalize inputs
    email = login_data.email.strip().lower()
    password = login_data.password.strip()

    # Validate
    validate_email(email)
    validate_password(password)

    # Check user in DB
    db_user = db.query(user.User).filter(user.User.email == email).first()
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "detail": "Login Successful",
        "user_id": db_user.id,
        "name":db_user.name
    }





@router.get("/search")
def find_user(
    searched: str = "",
    user_id: int = 0,
    db: Session = Depends(get_db)
):
    User = user.User
    
    if searched.strip() == "":
        results = db.query(User).filter(User.id != user_id).all()
    else:
        results = db.query(User).filter(
            or_(
                User.name.ilike(f"%{searched}%"),
                User.email.ilike(f"%{searched}%")
            ),
            User.id != user_id   # 👈 exclude own profile
        ).all()

    if not results:
        raise HTTPException(status_code=404, detail="No user found")

    return [
        {"id": u.id, "name": u.name, "email": u.email}
        for u in results
    ]
