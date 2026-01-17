from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import json
import math

from .database import get_db, User, Class, Attendance, Enrollment
from .auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from .face_recognition_utils import face_system

app = FastAPI(title="Smart Attendance System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: str = "student"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool

class ClassCreate(BaseModel):
    name: str
    description: str
    schedule: str
    location: str
    latitude: float
    longitude: float
    radius: float = 100.0

class AttendanceCreate(BaseModel):
    class_id: int
    method: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    face_image: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth's radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

@app.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active
        )
    }

@app.post("/upload-face")
async def upload_face_encoding(face_image: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    face_encoding = face_system.encode_face_from_base64(face_image)
    if not face_encoding:
        raise HTTPException(status_code=400, detail="No face detected in image")
    
    current_user.face_encoding = json.dumps(face_encoding)
    db.commit()
    return {"message": "Face encoding uploaded successfully"}

@app.post("/classes")
async def create_class(class_data: ClassCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized to create classes")
    
    db_class = Class(
        name=class_data.name,
        description=class_data.description,
        teacher_id=current_user.id,
        schedule=class_data.schedule,
        location=class_data.location,
        latitude=class_data.latitude,
        longitude=class_data.longitude,
        radius=class_data.radius
    )
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

@app.get("/classes")
async def get_classes(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role == "admin":
        return db.query(Class).all()
    elif current_user.role == "teacher":
        return db.query(Class).filter(Class.teacher_id == current_user.id).all()
    else:
        enrollments = db.query(Enrollment).filter(Enrollment.user_id == current_user.id).all()
        return [enrollment.class_obj for enrollment in enrollments]

@app.post("/enroll/{class_id}")
async def enroll_in_class(class_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.class_id == class_id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Already enrolled in this class")
    
    enrollment = Enrollment(user_id=current_user.id, class_id=class_id)
    db.add(enrollment)
    db.commit()
    return {"message": "Enrolled successfully"}

@app.post("/attendance")
async def mark_attendance(attendance_data: AttendanceCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    class_obj = db.query(Class).filter(Class.id == attendance_data.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Check if user is enrolled
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.class_id == attendance_data.class_id
    ).first()
    
    if not enrollment and current_user.role == "student":
        raise HTTPException(status_code=403, detail="Not enrolled in this class")
    
    # Check location if provided
    if attendance_data.latitude and attendance_data.longitude:
        distance = calculate_distance(
            class_obj.latitude, class_obj.longitude,
            attendance_data.latitude, attendance_data.longitude
        )
        if distance > class_obj.radius:
            raise HTTPException(status_code=400, detail="Not within class location")
    
    confidence = 1.0
    is_valid = True
    
    # Face recognition verification
    if attendance_data.method == "face" and attendance_data.face_image:
        if not current_user.face_encoding:
            raise HTTPException(status_code=400, detail="No face encoding registered")
        
        face_encoding = face_system.encode_face_from_base64(attendance_data.face_image)
        if not face_encoding:
            raise HTTPException(status_code=400, detail="No face detected")
        
        match, confidence = face_system.compare_faces(current_user.face_encoding, face_encoding)
        if not match:
            raise HTTPException(status_code=400, detail="Face verification failed")
    
    # Check for duplicate attendance (within 1 hour)
    recent_attendance = db.query(Attendance).filter(
        Attendance.user_id == current_user.id,
        Attendance.class_id == attendance_data.class_id,
        Attendance.timestamp > datetime.utcnow() - timedelta(hours=1)
    ).first()
    
    if recent_attendance:
        raise HTTPException(status_code=400, detail="Attendance already marked recently")
    
    attendance = Attendance(
        user_id=current_user.id,
        class_id=attendance_data.class_id,
        method=attendance_data.method,
        latitude=attendance_data.latitude,
        longitude=attendance_data.longitude,
        confidence=confidence,
        is_valid=is_valid
    )
    
    db.add(attendance)
    db.commit()
    return {"message": "Attendance marked successfully", "confidence": confidence}

@app.get("/attendance/{class_id}")
async def get_attendance(class_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    if current_user.role == "student":
        attendances = db.query(Attendance).filter(
            Attendance.user_id == current_user.id,
            Attendance.class_id == class_id
        ).all()
    else:
        attendances = db.query(Attendance).filter(Attendance.class_id == class_id).all()
    
    return attendances

@app.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role == "admin":
        total_users = db.query(User).count()
        total_classes = db.query(Class).count()
        total_attendances = db.query(Attendance).count()
        return {
            "total_users": total_users,
            "total_classes": total_classes,
            "total_attendances": total_attendances
        }
    elif current_user.role == "teacher":
        my_classes = db.query(Class).filter(Class.teacher_id == current_user.id).count()
        total_attendances = db.query(Attendance).join(Class).filter(Class.teacher_id == current_user.id).count()
        return {
            "my_classes": my_classes,
            "total_attendances": total_attendances
        }
    else:
        my_enrollments = db.query(Enrollment).filter(Enrollment.user_id == current_user.id).count()
        my_attendances = db.query(Attendance).filter(Attendance.user_id == current_user.id).count()
        return {
            "enrolled_classes": my_enrollments,
            "my_attendances": my_attendances
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)