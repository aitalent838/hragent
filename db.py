import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./hr_system.db')
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    role = Column(String, nullable=False)  # employee or hr_admin
    leave_balance = Column(Integer, default=14)
    password_hash = Column(String, nullable=False)

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, index=True, nullable=False)
    category = Column(String, nullable=False)
    issue = Column(Text, nullable=False)
    priority = Column(String, default='medium')
    status = Column(String, default='open')
    assigned_to = Column(String, nullable=True)
    resolution_note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, index=True, nullable=False)
    user_message = Column(Text, nullable=False)
    category = Column(String)
    answer = Column(Text)
    status = Column(String)
    ticket_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
