from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class Balance(BaseModel):
    amount: float
    currency_code: str

class GroupMember(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    email: str
    registration_status: Optional[str] = None
    balance: Optional[List[Balance]] = []

class GroupInfo(BaseModel):
    id: int
    name: str
    members: List[GroupMember]

class GetGroupInformationRequest(BaseModel):
    group_name_filter: str = Field("at&t", description="Substring to find the group")

class AddExpenseRequest(BaseModel):
    total_amount: float = Field(..., description="The total cost")
    description: str = Field(..., description="Description of the expense")
    group_name_filter: str = Field("at&t", description="Substring to find the group")
    splits: Optional[Dict[str, float]] = Field(None, description="Dictionary of {Email: Amount}. If provided, splits are assigned explicitly.")

class AddExpenseResponse(BaseModel):
    success: bool
    expense_id: Optional[int] = None
    message: str
