from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./attendance.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="student")  # admin, teacher, student
    is_active = Column(Boolean, default=True)
    face_encoding = Column(Text)
    face_image = Column(Text)  # Base64 encoded face image
    phone_number = Column(String)  # User's phone number
    parent_phone = Column(String)  # Parent's phone number (for students)
    emergency_contact = Column(String)  # Emergency contact number
    notification_preferences = Column(String, default="email,sms")  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    attendances = relationship("Attendance", back_populates="user")
    taught_classes = relationship("Class", back_populates="teacher")

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    schedule = Column(String)  # JSON string for schedule
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    radius = Column(Float, default=100.0)  # meters
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    teacher = relationship("User", back_populates="taught_classes")
    attendances = relationship("Attendance", back_populates="class_obj")
    enrollments = relationship("Enrollment", back_populates="class_obj")

class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    class_obj = relationship("Class", back_populates="enrollments")

class Attendance(Base):
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    method = Column(String)  # face, manual, qr
    latitude = Column(Float)
    longitude = Column(Float)
    confidence = Column(Float)
    is_valid = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="attendances")
    class_obj = relationship("Class", back_populates="attendances")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)