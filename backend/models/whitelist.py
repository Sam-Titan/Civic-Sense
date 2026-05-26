from pydantic import BaseModel

class WhitelistAdd(BaseModel):
    phone_number: str
    added_by: str