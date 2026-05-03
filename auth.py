import os
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from db import get_db, Employee

load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET', 'change-this-secret')
ALGORITHM = 'HS256'
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash

def create_access_token(data: dict, expires_minutes: int = 480):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        employee_id = payload.get('sub')
        if not employee_id:
            raise HTTPException(status_code=401, detail='Invalid token')
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid token')
    user = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    return user

def require_hr_admin(user: Employee = Depends(get_current_user)):
    if user.role != 'hr_admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='HR admin only')
    return user
