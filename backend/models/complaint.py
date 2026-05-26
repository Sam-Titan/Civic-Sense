from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ComplaintCreate(BaseModel):
    description: str

class ComplaintAcknowledge(BaseModel):
    eta: datetime

class ComplaintRemark(BaseModel):
    remarks: str