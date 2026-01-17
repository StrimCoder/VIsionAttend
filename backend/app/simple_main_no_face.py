from fastapi import FastAPI, Depends, HTTPException, status
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
try:
    from .notification_service import NotificationService
except ImportError:
    NotificationService = None

# Basic AI features without phone camera
AI_ENABLED = False

app = FastAPI(title="Smart Attendance System", version="2.0.0 AI Enhanced")

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
    face_image: Optional[str] = None
    phone_number: Optional[str] = None
    parent_phone: Optional[str] = None
    emergency_contact: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool

class ClassCreate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    days: Optional[List[str]] = []

class AttendanceCreate(BaseModel):
    class_id: int
    method: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class NotificationPreferences(BaseModel):
    preferences: List[str]

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email exists
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate input fields
    if len(user.username.strip()) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    if not user.email or '@' not in user.email:
        raise HTTPException(status_code=400, detail="Valid email is required")
    
    if not user.full_name.strip():
        raise HTTPException(status_code=400, detail="Full name is required")
    
    if user.role not in ['admin', 'teacher', 'student']:
        raise HTTPException(status_code=400, detail="Invalid role. Must be admin, teacher, or student")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username.lower().strip(),
        email=user.email.lower().strip(),
        full_name=user.full_name.strip(),
        hashed_password=hashed_password,
        role=user.role,
        face_image=user.face_image,
        phone_number=user.phone_number,
        parent_phone=user.parent_phone,
        emergency_contact=user.emergency_contact,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/admin/create-user", response_model=UserResponse)
async def admin_create_user(user: UserCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if username exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email exists
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate input fields
    if len(user.username.strip()) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    if not user.email or '@' not in user.email:
        raise HTTPException(status_code=400, detail="Valid email is required")
    
    if not user.full_name.strip():
        raise HTTPException(status_code=400, detail="Full name is required")
    
    if user.role not in ['admin', 'teacher', 'student']:
        raise HTTPException(status_code=400, detail="Invalid role. Must be admin, teacher, or student")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username.lower().strip(),
        email=user.email.lower().strip(),
        full_name=user.full_name.strip(),
        hashed_password=hashed_password,
        role=user.role,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Normalize username
    username = form_data.username.lower().strip()
    
    user = authenticate_user(db, username, form_data.password)
    if not user:
        # Check if user exists but password is wrong
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            if not existing_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is deactivated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username not found",
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

@app.post("/login", response_model=Token)
async def login_alternative(login_data: LoginRequest, db: Session = Depends(get_db)):
    username = login_data.username.lower().strip()
    
    user = authenticate_user(db, username, login_data.password)
    if not user:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            if not existing_user.is_active:
                raise HTTPException(status_code=401, detail="Account is deactivated")
            else:
                raise HTTPException(status_code=401, detail="Incorrect password")
        else:
            raise HTTPException(status_code=401, detail="Username not found")
    
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

@app.post("/classes")
async def create_class(class_data: ClassCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized to create classes")
    
    # Set defaults for missing fields
    name = class_data.name or "New Class"
    description = class_data.description or "Class Description"
    location = class_data.location or "TBD"
    start_time = class_data.start_time or "09:00"
    end_time = class_data.end_time or "10:00"
    days = class_data.days or ["Monday"]
    
    # Create schedule string
    schedule = f"{', '.join(days)} {start_time}-{end_time}"
    
    db_class = Class(
        name=name,
        description=description,
        teacher_id=current_user.id,
        schedule=schedule,
        location=location,
        latitude=0.0,
        longitude=0.0,
        radius=100.0
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
        confidence=1.0,
        is_valid=True
    )
    
    db.add(attendance)
    db.commit()
    
    # Send notifications if service is available
    if NotificationService:
        notification_service = NotificationService(db)
        # Check if this is a late arrival (more than 15 minutes after class start)
        from datetime import time
        class_start = datetime.combine(datetime.utcnow().date(), time(9, 0))
        if attendance.timestamp > class_start + timedelta(minutes=15):
            notification_service.notify_late_arrival(current_user.id, attendance_data.class_id, attendance.timestamp)
    
    return {"message": "Attendance marked successfully", "confidence": 1.0}

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

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active
    )

@app.get("/users", response_model=List[UserResponse])
async def get_all_users(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = db.query(User).all()
    return [UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active
    ) for user in users]

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.username = user_data.username or user.username
    user.email = user_data.email or user.email
    user.full_name = user_data.full_name or user.full_name
    user.role = user_data.role or user.role
    
    if user_data.password:
        user.hashed_password = get_password_hash(user_data.password)
    
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active
    )

@app.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role == "admin":
        total_users = db.query(User).count()
        total_classes = db.query(Class).count()
        total_attendances = db.query(Attendance).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        return {
            "total_users": total_users,
            "total_classes": total_classes,
            "total_attendances": total_attendances,
            "active_users": active_users
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

@app.get("/analytics/attendance-trends")
async def get_attendance_trends(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get attendance data for the last 7 days
    from datetime import datetime, timedelta
    from sqlalchemy import func, and_
    
    trends = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        attendance_count = db.query(Attendance).filter(
            and_(Attendance.timestamp >= start_date, Attendance.timestamp <= end_date)
        ).count()
        
        trends.append({
            "date": date.strftime("%Y-%m-%d"),
            "day": date.strftime("%a"),
            "count": attendance_count
        })
    
    return {"trends": trends[::-1]}  # Reverse to show oldest first

@app.get("/analytics/user-roles")
async def get_user_role_distribution(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from sqlalchemy import func
    
    role_counts = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    
    return {
        "roles": [{
            "role": role,
            "count": count
        } for role, count in role_counts]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "ai_enabled": AI_ENABLED,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/notifications/preferences")
async def get_notification_preferences(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not NotificationService:
        return {"preferences": ["email", "sms"]}
    notification_service = NotificationService(db)
    preferences = notification_service.get_notification_preferences(current_user.id)
    return {"preferences": preferences}

@app.put("/notifications/preferences")
async def update_notification_preferences(preferences: NotificationPreferences, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not NotificationService:
        return {"message": "Notification service not available"}
    notification_service = NotificationService(db)
    success = notification_service.update_notification_preferences(current_user.id, preferences.preferences)
    if success:
        return {"message": "Notification preferences updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to update preferences")

@app.post("/notifications/test")
async def send_test_notification(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not NotificationService:
        return {"message": "Notification service not available"}
    notification_service = NotificationService(db)
    notification_service.send_notification(current_user.id, "This is a test notification from VisionAttend!", "TEST")
    return {"message": "Test notification sent"}

@app.post("/notifications/daily-summary")
async def send_daily_summary(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not NotificationService:
        return {"message": "Notification service not available"}
    notification_service = NotificationService(db)
    notification_service.send_daily_summary(current_user.id)
    return {"message": "Daily summary sent"}

@app.post("/notifications/meeting-reminder/{class_id}")
async def send_meeting_reminder(class_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not NotificationService:
        return {"message": "Notification service not available"}
    notification_service = NotificationService(db)
    notification_service.send_meeting_reminder(class_id)
    return {"message": "Meeting reminder sent"}

@app.get("/")
async def root():
    return {
        "message": "Smart Attendance System API with Instant Notifications",
        "version": "2.0.0",
        "ai_features": AI_ENABLED,
        "notification_features": True,
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    print(f"Starting Smart Attendance System v2.0.0")
    print(f"AI Features: {'Enabled' if AI_ENABLED else 'Disabled'}")
    print(f"Server will be available at: http://localhost:8000")
    print(f"API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8001)