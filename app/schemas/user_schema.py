from pydantic import BaseModel

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str

class UserLoginRequest(BaseModel):
    email: str
    password: str