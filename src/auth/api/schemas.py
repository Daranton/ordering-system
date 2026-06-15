from datetime import datetime

from pydantic import BaseModel

# Placeholders for Monday's scaffold. Tuesday upgrades these to use
# EmailStr and password length constraints (Field(min_length=8, max_length=72)).


class UserRegister(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime
