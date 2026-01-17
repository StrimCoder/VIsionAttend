from fastapi import FastAPI, HTTPException, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import json
import os
from datetime import datetime

app = FastAPI(title="Smart Attendance System", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File-based user storage
USERS_FILE = "users.json"
MESSAGES_FILE = "messages.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            data = json.load(f)
            return data.get('users', {}), data.get('counter', 4)
    return {
        "admin": {"id": 1, "username": "admin", "password": "admin123", "email": "admin@test.com", "full_name": "Admin User", "role": "admin", "is_active": True},
        "jay123": {"id": 2, "username": "jay123", "password": "jay123", "email": "jay@test.com", "full_name": "Jay Student", "role": "student", "is_active": True},
        "teacher1": {"id": 3, "username": "teacher1", "password": "teacher123", "email": "teacher@test.com", "full_name": "Teacher One", "role": "teacher", "is_active": True}
    }, 4

def save_users():
    with open(USERS_FILE, 'w') as f:
        json.dump({'users': users, 'counter': user_counter}, f, indent=2)

def load_messages():
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_messages(messages):
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=2)

users, user_counter = load_users()
messages = load_messages()

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

class StudentMessage(BaseModel):
    subject: str
    message: str
    recipient: str

class MessageResponse(BaseModel):
    id: int
    subject: str
    message: str
    recipient: str
    student_name: str
    student_id: str
    timestamp: str
    status: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

@app.get("/")
def root():
    return {"message": "Smart Attendance System Backend is running!", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy", "version": "2.0.0"}

@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate):
    global user_counter
    if user.username in users:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if this is the first user (admin)
    is_first_user = len(users) == 0
    
    # Prevent direct admin registration unless it's the first user
    if user.role == "admin" and not is_first_user:
        raise HTTPException(status_code=400, detail="Admin accounts can only be created by existing admins")
    
    # Set role to admin for first user, otherwise default to student/teacher only
    if is_first_user:
        user.role = "admin"
    elif user.role not in ["student", "teacher"]:
        user.role = "student"  # Default to student if invalid role
    
    new_user = {
        "id": user_counter,
        "username": user.username,
        "password": user.password,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": True
    }
    users[user.username] = new_user
    user_counter += 1
    save_users()
    
    return UserResponse(
        id=new_user["id"],
        username=new_user["username"],
        email=new_user["email"],
        full_name=new_user["full_name"],
        role=new_user["role"],
        is_active=new_user["is_active"]
    )

@app.post("/admin/create-user", response_model=UserResponse)
def admin_create_user(user: UserCreate, authorization: Optional[str] = Header(None)):
    # Check if current user is admin
    if not authorization or not authorization.startswith("Bearer fake-token-"):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    username = authorization.replace("Bearer fake-token-", "")
    if username not in users or users[username]["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    global user_counter
    if user.username in users:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = {
        "id": user_counter,
        "username": user.username,
        "password": user.password,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": True
    }
    users[user.username] = new_user
    user_counter += 1
    save_users()
    
    return UserResponse(
        id=new_user["id"],
        username=new_user["username"],
        email=new_user["email"],
        full_name=new_user["full_name"],
        role=new_user["role"],
        is_active=new_user["is_active"]
    )

@app.post("/token", response_model=Token)
def login_for_access_token(username: str = Form(), password: str = Form()):
    print(f"Login attempt: username='{username}', password='{password}'")
    print(f"Available users: {list(users.keys())}")
    
    username = username.strip()
    
    # Find user case-insensitively
    found_user = None
    actual_username = None
    for user_key, user_data in users.items():
        if user_key.lower() == username.lower():
            found_user = user_data
            actual_username = user_key
            break
    
    if not found_user:
        print(f"Username '{username}' not found in users")
        raise HTTPException(status_code=401, detail="Username not found")
    
    stored_password = found_user["password"]
    print(f"Stored password: '{stored_password}', Provided password: '{password}'")
    
    if stored_password != password:
        print(f"Password mismatch for user '{username}'")
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    print(f"Login successful for user '{username}'")
    username = actual_username
    
    user = users[username]
    return Token(
        access_token="fake-token-" + username,
        token_type="bearer",
        user=UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            is_active=user["is_active"]
        )
    )

@app.get("/users/me", response_model=UserResponse)
def get_current_user(authorization: Optional[str] = Header(None)):
    print(f"GET /users/me called with authorization: {authorization}")
    
    # Extract username from fake token
    if authorization and authorization.startswith("Bearer fake-token-"):
        username = authorization.replace("Bearer fake-token-", "")
        print(f"Extracted username from token: {username}")
        if username in users:
            user = users[username]
            print(f"Returning user data for: {username}")
            return UserResponse(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                full_name=user["full_name"],
                role=user["role"],
                is_active=user["is_active"]
            )
    
    # Default to admin if no valid token
    print("No valid token, returning admin user")
    admin_user = users["admin"]
    return UserResponse(
        id=admin_user["id"],
        username=admin_user["username"],
        email=admin_user["email"],
        full_name=admin_user["full_name"],
        role=admin_user["role"],
        is_active=admin_user["is_active"]
    )

@app.get("/classes")
def get_classes():
    return []

@app.get("/users")
def get_all_users():
    print("GET /users called")
    user_list = [UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        is_active=user["is_active"]
    ) for user in users.values()]
    print(f"Returning {len(user_list)} users")
    return user_list

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    print(f"DELETE /users/{user_id} called")
    
    # Find user by ID
    user_to_delete = None
    username_to_delete = None
    for username, user_data in users.items():
        if user_data["id"] == user_id:
            user_to_delete = user_data
            username_to_delete = username
            break
    
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete the user
    del users[username_to_delete]
    save_users()
    print(f"User {username_to_delete} deleted successfully")
    
    return {"message": "User deleted successfully"}

@app.post("/student/send-message")
def send_student_message(message_data: StudentMessage, authorization: Optional[str] = Header(None)):
    # Check if current user is authenticated
    if not authorization or not authorization.startswith("Bearer fake-token-"):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    username = authorization.replace("Bearer fake-token-", "")
    if username not in users:
        raise HTTPException(status_code=401, detail="Invalid user")
    
    user = users[username]
    
    # Create new message
    new_message = {
        "id": len(messages) + 1,
        "subject": message_data.subject,
        "message": message_data.message,
        "recipient": message_data.recipient,
        "student_name": user["full_name"],
        "student_id": user["username"],
        "timestamp": datetime.now().isoformat(),
        "status": "sent"
    }
    
    messages.append(new_message)
    save_messages(messages)
    
    return MessageResponse(**new_message)

@app.get("/student/messages", response_model=List[MessageResponse])
def get_student_messages(authorization: Optional[str] = Header(None)):
    # Check if current user is authenticated
    if not authorization or not authorization.startswith("Bearer fake-token-"):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    username = authorization.replace("Bearer fake-token-", "")
    if username not in users:
        raise HTTPException(status_code=401, detail="Invalid user")
    
    # Return messages for this student
    student_messages = [msg for msg in messages if msg["student_id"] == username]
    return [MessageResponse(**msg) for msg in student_messages]

@app.get("/messages", response_model=List[MessageResponse])
def get_all_messages(authorization: Optional[str] = Header(None)):
    # Check if current user is admin or teacher
    if not authorization or not authorization.startswith("Bearer fake-token-"):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    username = authorization.replace("Bearer fake-token-", "")
    if username not in users or users[username]["role"] not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Admin or Teacher access required")
    
    return [MessageResponse(**msg) for msg in messages]

@app.get("/dashboard/stats")
def get_dashboard_stats():
    print("GET /dashboard/stats called")
    stats = {
        "total_users": len(users), 
        "total_classes": 0, 
        "total_attendances": 0,
        "total_messages": len(messages)
    }
    print(f"Returning stats: {stats}")
    return stats

if __name__ == "__main__":
    print("Starting Smart Attendance System Backend...")
    print("Server will be available at: http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)