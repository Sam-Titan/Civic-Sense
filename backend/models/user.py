from pydantic import BaseModel
from typing import Literal

class UserRegister(BaseModel):
    name: str
    address: str
    locality: str
    role: Literal["resident", "rwa_admin"] = "resident"
