from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum
from uuid import UUID

class UserRole(str, Enum):
    FONOAUDIOLOGIA = "fonoaudiólogia"
    INVESTIGADOR = "investigador"
    ESTUDIANTE = "estudiante"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: UserRole
    
class UserModel(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    role: UserRole
    created_at: datetime
    

