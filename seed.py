from db import init_db, SessionLocal, Employee
from auth import hash_password

init_db()
db = SessionLocal()
try:
    demo = [
        ('EMP001', 'Phenix Chan', 'Operations', 'employee', 12),
        ('EMP002', 'Aina Lee', 'Sales', 'employee', 8),
        ('HR001', 'HR Admin', 'Human Resources', 'hr_admin', 14),
    ]
    for employee_id, name, dept, role, leave_balance in demo:
        existing = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not existing:
            db.add(Employee(employee_id=employee_id, name=name, department=dept, role=role, leave_balance=leave_balance, password_hash=hash_password('password123')))
    db.commit()
    print('Database seeded. Demo password: password123')
finally:
    db.close()
