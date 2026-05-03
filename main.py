from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from db import init_db, get_db, Employee, Ticket, ChatMessage
from auth import verify_password, create_access_token, get_current_user, require_hr_admin, hash_password
from schemas import LoginRequest, ChatRequest, ChatResponse, TicketUpdate, EmployeeCreate
from agents.router_agent import classify_case, priority_for
from agents.resolution_agent import resolve_case

init_db()
app = FastAPI(title='HR Case Resolution Agent', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.mount('/static', StaticFiles(directory='static'), name='static')

@app.get('/')
def web_app():
    return FileResponse('static/index.html')

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/auth/login')
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Employee).filter(Employee.employee_id == body.employee_id).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid employee ID or password')
    token = create_access_token({'sub': user.employee_id, 'role': user.role})
    return {'access_token': token, 'token_type': 'bearer', 'employee': {'employee_id': user.employee_id, 'name': user.name, 'role': user.role, 'department': user.department}}

@app.get('/me')
def me(user: Employee = Depends(get_current_user)):
    return {'employee_id': user.employee_id, 'name': user.name, 'department': user.department, 'role': user.role, 'leave_balance': user.leave_balance}

@app.post('/chat', response_model=ChatResponse)
def chat(body: ChatRequest, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    category = classify_case(body.message)
    answer, confident = resolve_case(category, body.message, user)
    ticket_id = None
    status = 'resolved' if confident and category != 'employee_relations' else 'escalated'
    if status == 'escalated':
        ticket = Ticket(employee_id=user.employee_id, category=category, issue=body.message, priority=priority_for(body.message, category), status='open')
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        ticket_id = ticket.id
        answer = answer + f"\n\nI created HR ticket #{ticket_id} for follow-up."
    chat_row = ChatMessage(employee_id=user.employee_id, user_message=body.message, category=category, answer=answer, status=status, ticket_id=ticket_id)
    db.add(chat_row)
    db.commit()
    return ChatResponse(category=category, answer=answer, status=status, ticket_id=ticket_id)

@app.get('/tickets')
def list_my_tickets(user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Ticket)
    if user.role != 'hr_admin':
        q = q.filter(Ticket.employee_id == user.employee_id)
    return q.order_by(Ticket.id.desc()).all()

@app.patch('/tickets/{ticket_id}')
def update_ticket(ticket_id: int, body: TicketUpdate, admin: Employee = Depends(require_hr_admin), db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail='Ticket not found')
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(ticket, field, value)
    db.commit()
    db.refresh(ticket)
    return ticket

@app.get('/employees')
def list_employees(admin: Employee = Depends(require_hr_admin), db: Session = Depends(get_db)):
    return db.query(Employee).order_by(Employee.employee_id).all()

@app.post('/employees')
def create_employee(body: EmployeeCreate, admin: Employee = Depends(require_hr_admin), db: Session = Depends(get_db)):
    if db.query(Employee).filter(Employee.employee_id == body.employee_id).first():
        raise HTTPException(status_code=400, detail='Employee ID already exists')
    employee = Employee(employee_id=body.employee_id, name=body.name, department=body.department, role=body.role, leave_balance=body.leave_balance, password_hash=hash_password(body.password))
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

@app.get('/chat/history')
def chat_history(user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(ChatMessage)
    if user.role != 'hr_admin':
        q = q.filter(ChatMessage.employee_id == user.employee_id)
    return q.order_by(ChatMessage.id.desc()).limit(50).all()
