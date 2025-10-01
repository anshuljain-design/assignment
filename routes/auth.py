from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import smtplib
import string
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from baseModels.auth_model import SignupModel, LoginModel
from db_models import database, user
from passlib.context import CryptContext
from validators.auth_validators import *
from pydantic import BaseModel

router = APIRouter()

# Password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# DB session dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions (truncate passwords to 72 bytes for bcrypt)
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password[:72])  # truncate to 72 bytes

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain[:72], hashed)  # truncate to 72 bytes

# ----------------- Routes -----------------

@router.post("/signup")
def signup(user_data: SignupModel, db: Session = Depends(get_db)):
    email = user_data.email.strip().lower()
    name = user_data.name.strip().title()
    password = user_data.password.strip()

    # Validate inputs
    validate_email(email)
    validate_name(name)
    validate_password(password)

    # Check if user exists
    if db.query(user.User).filter(user.User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed_pw = get_password_hash(password)
    new_user = user.User(email=email, name=name, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"detail": "User registered successfully", "user_id": new_user.id, "name": new_user.name}


@router.post("/login")
def login(login_data: LoginModel, db: Session = Depends(get_db)):
    email = login_data.email.strip().lower()
    password = login_data.password.strip()

    # Validate inputs
    validate_email(email)
    validate_password(password)

    db_user = db.query(user.User).filter(user.User.email == email).first()
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"detail": "Login Successful", "user_id": db_user.id, "name": db_user.name}


@router.get("/search")
def find_user(searched: str = "", user_id: int = 0, db: Session = Depends(get_db)):
    User = user.User

    if searched.strip() == "":
        results = db.query(User).filter(User.id != user_id).all()
    else:
        results = db.query(User).filter(
            or_(
                User.name.ilike(f"%{searched}%"),
                User.email.ilike(f"%{searched}%")
            ),
            User.id != user_id
        ).all()

    if not results:
        raise HTTPException(status_code=404, detail="No user found")

    return [{"id": u.id, "name": u.name, "email": u.email, "p":u.hashed_password} for u in results]


def generate_random_password():
    # length between 8 and 16
    length = random.randint(8, 16)
    letters = string.ascii_letters
    digits = string.digits
    specials = "@#%"
    all_chars = letters + digits + specials

    # Ensure at least one of each type
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(digits),
        random.choice(specials),
    ]
    password += random.choices(all_chars, k=length - 4)
    random.shuffle(password)
    return "".join(password)

@router.get("/forget/{email}")
def forget(email: str, db: Session = Depends(get_db)):
    # Find user
    res = db.query(user.User).filter(user.User.email == email).first()
    if not res:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate new plain text password
    new_password = generate_random_password()

    # Save plain password directly (⚠️ not secure)
    res.hashed_password = new_password
    db.commit()
    db.refresh(res)

    # Send password to email (pseudo)
    send_email(
        to=email,
        subject="Your new password",
        body=f"Hello {res.name},\n\nYour new password is: {new_password}\n\nPlease change it after login."
    )

    return {"status": 200, "message": "New password sent to your email"}



# configure your SMTP settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "anshuljain8110@gmail.com"
SENDER_PASSWORD = "umytwvcwrurtzvot"   # ⚠️ use App Password, not raw Gmail password

def send_email(to: str, subject: str, body: str):
    try:
        # Create the email
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        # Connect to the server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # secure connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # Send the email
        server.sendmail(SENDER_EMAIL, to, msg.as_string())
        server.quit()

        print(f"✅ Email sent to {to}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False







class ResetPasswordRequest(BaseModel):
    user_id: int
    old_password: str
    new_password: str

@router.post("/reset")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    # Fetch user
    res = db.query(user.User).filter(user.User.id == data.user_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify old password
    if res.hashed_password != data.old_password:
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    # Update with new password
    res.hashed_password = data.new_password
    db.commit()
    db.refresh(res)

    return {"status": 200, "message": "Password updated successfully"}
