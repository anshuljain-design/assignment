from pydantic import BaseModel, EmailStr, Field

class LoginModel(BaseModel):
    email: str
    password: str

class SignupModel(BaseModel):
    email: str
    name: str
    password: str
