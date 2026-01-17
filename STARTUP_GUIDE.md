# 🚀 Smart Attendance System - Quick Start Guide

## 📋 Prerequisites
- Python 3.7+ installed
- Node.js 14+ installed
- Git (optional)

## 🔧 Setup Instructions

### 1. Backend Setup (Terminal 1)
```bash
# Navigate to project directory
cd SAS

# Install Python dependencies
cd backend
pip install fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt] python-multipart python-dotenv pydantic email-validator

# Create sample data
python seed_data.py

# Start backend server
python -c "import uvicorn; from app.simple_main import app; uvicorn.run(app, host='127.0.0.1', port=8001)"
```

### 2. Frontend Setup (Terminal 2)
```bash
# Navigate to frontend directory
cd SAS/frontend

# Install dependencies (if not done)
npm install

# Start frontend server
npm start
```

## 🌐 Access the Application

1. **Frontend**: http://localhost:3000
2. **Backend API**: http://localhost:8001

## 🔐 Default Login Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`

### Teacher Account
- **Username**: `teacher1`
- **Password**: `teacher123`

### Student Accounts
- **Username**: `student1` | **Password**: `student123`
- **Username**: `student2` | **Password**: `student123`

## 📱 How to Use

### For New Users (Registration)
1. Go to http://localhost:3000
2. Click "Sign up" on login page
3. Fill registration form:
   - Full Name
   - Username (unique)
   - Email
   - Role (Student/Teacher/Admin)
   - Password
4. Click "Create Account"
5. Login with new credentials

### For Students
1. Login with student credentials
2. Go to "Classes" → Enroll in available classes
3. Go to "Attendance" → Select class → Mark attendance
4. View dashboard for statistics

### For Teachers
1. Login with teacher credentials
2. Go to "Classes" → Create new classes
3. Set location coordinates for geofencing
4. View attendance reports for your classes

### For Admins
1. Login with admin credentials
2. Access all system features
3. View comprehensive analytics
4. Manage all users and classes

## 🛠️ Features Available

✅ **User Registration & Login**
✅ **Role-based Access Control**
✅ **Class Management**
✅ **Student Enrollment**
✅ **Manual Attendance Marking**
✅ **Geolocation Support**
✅ **Real-time Dashboard**
✅ **Responsive Design**

## 🔧 Troubleshooting

### Backend Issues
- **Port 8001 in use**: Change port in `start_backend.py`
- **Database errors**: Delete `attendance.db` and run `seed_data.py` again
- **Import errors**: Ensure all dependencies are installed

### Frontend Issues
- **Port 3000 in use**: React will prompt to use different port
- **API connection**: Ensure backend is running on port 8001
- **Build errors**: Delete `node_modules` and run `npm install` again

### Common Solutions
1. **Clear browser cache** if login issues persist
2. **Check console logs** for detailed error messages
3. **Restart both servers** if experiencing connection issues

## 📞 Support
- Check browser console for errors
- Verify both servers are running
- Ensure correct ports (3000 for frontend, 8001 for backend)

## 🎯 Next Steps
1. Test registration with different roles
2. Create classes as teacher/admin
3. Enroll students in classes
4. Mark attendance and view reports
5. Explore dashboard analytics

**Happy Learning! 🎓**