from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    employee_id: str
    password: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    category: str
    answer: str
    status: str
    ticket_id: Optional[int] = None

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_note: Optional[str] = None

class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    department: str
    role: str = 'employee'
    leave_balance: int = 14
    password: str
