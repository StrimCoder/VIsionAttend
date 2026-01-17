# VisionAttend

A comprehensive attendance management system with advanced features including face recognition, geolocation verification, and real-time analytics.

## Features

### Core Features
- **Face Recognition**: Advanced facial recognition for secure attendance marking
- **Geolocation Verification**: Location-based attendance validation
- **Role-Based Access**: Admin, Teacher, and Student roles with different permissions
- **Real-time Dashboard**: Live statistics and analytics
- **Multi-method Attendance**: Face recognition, manual check-in, and QR code support

### Advanced Features
- **JWT Authentication**: Secure token-based authentication
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Notifications**: Instant feedback and alerts
- **Attendance Analytics**: Comprehensive reporting and insights
- **Class Management**: Create and manage classes with schedules
- **Enrollment System**: Student enrollment in classes
- **Location Radius**: Configurable attendance radius for classes

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **SQLite**: Lightweight database
- **OpenCV**: Computer vision library
- **face_recognition**: Face recognition library
- **JWT**: JSON Web Tokens for authentication

### Frontend
- **React**: Modern JavaScript library
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **React Webcam**: Camera integration
- **Recharts**: Data visualization

## Installation & Setup

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend server:
```bash
python -m app.main
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## User Management & Access Controll

### Registration Rules
- **First User**: The first person to register automatically becomes an admin (regardless of selected role)
- **Subsequent Users**: Can only register as Student or Teacher through public registration
- **Admin Role**: Cannot be selected during public registration for security

### Admin Creation
- Only existing admins can create new admin accounts
- Admins can create users with any role (Student, Teacher, Admin) through the Users management page
- Admins can delete any user account including other admin accounts

### Teacher Features

**Enhanced Teacher Dashboard:**
- Beautiful gradient header with real-time statistics
- Quick access to class creation, data export, analytics, and notifications
- Overview of teacher's classes, total attendance, and active students

**Class Management:**
- Create new classes with scheduling (time, location, days)
- View and manage all assigned classes
- Real-time class statistics and enrollment data

**Attendance Monitoring:**
- Real-time attendance tracking per class
- View recent attendance records with validation status
- Monitor student participation and engagement

**Data Export & Analytics:**
- Export attendance data as CSV files for analysis
- Download class-specific attendance reports
- Access to comprehensive attendance analytics

**Special Teacher Capabilities:**
- Create and configure classes with custom schedules
- Monitor real-time student attendance across all classes
- Export attendance reports for administrative purposes
- Access to teacher-specific analytics and insights
- Quick actions panel for common teaching tasks

### Role Hierarchy
- **Admin**: Full system access, user management, create/delete any accounts
- **Teacher**: Create classes, manage enrollments, view class analytics
- **Student**: Mark attendance, view personal history, enroll in classes

## Usage

### Initial Setup

1. Start both backend and frontend servers
2. Open `http://localhost:3000` in your browser
3. Register a new account (first user can be admin)
4. Upload your face encoding in settings
5. Create classes (admin/teacher) or enroll in classes (student)

### Marking Attendance

1. Go to Attendance page
2. Select a class
3. Choose attendance method (Face Recognition or Manual)
4. For face recognition: Capture your face using webcam
5. Click "Mark Attendance"

### Admin Features

- Create and manage users
- View all classes and attendance records
- Access comprehensive analytics
- Manage system settings

### Teacher Features

- Create and manage classes
- View attendance for their classes
- Access class-specific analytics
- Manage student enrollments

### Student Features

- Mark attendance using face recognition
- View personal attendance history
- Enroll in available classes
- Update profile and face encoding

## API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /token` - Login and get access token

### User Management
- `POST /upload-face` - Upload face encoding
- `GET /users/me` - Get current user info

### Class Management
- `POST /classes` - Create new class
- `GET /classes` - Get user's classes
- `POST /enroll/{class_id}` - Enroll in class

### Attendance
- `POST /attendance` - Mark attendance
- `GET /attendance/{class_id}` - Get attendance records

### Dashboard
- `GET /dashboard/stats` - Get dashboard statistics

## Security Features

- JWT token authentication
- Password hashing with bcrypt
- Face encoding encryption
- Location verification
- Role-based access control
- Input validation and sanitization

## Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./attendance.db
CORS_ORIGINS=http://localhost:3000
```

### Face Recognition Settings
- Tolerance: 0.6 (adjustable in face_recognition_utils.py)
- Image format: JPEG
- Minimum confidence: 60%

### Location Settings
- Default radius: 100 meters
- GPS accuracy: High accuracy mode
- Fallback: Manual location entry

## Troubleshooting

### Common Issues

1. **Camera not working**: Ensure browser permissions for camera access
2. **Face not detected**: Ensure good lighting and face is clearly visible
3. **Location not found**: Enable location services in browser
4. **Backend connection error**: Check if backend server is running on port 8000

### Performance Optimization

- Face encodings are cached for faster recognition
- Database queries are optimized with proper indexing
- Images are compressed before processing
- Real-time updates use efficient WebSocket connections

### ScreenShots
---

<img width="1916" height="1030" alt="Screenshot 2026-01-17 131859" src="https://github.com/user-attachments/assets/5fdb5b6f-96fd-4b1c-99be-688ef9aef01c" />

<img width="1914" height="1029" alt="Screenshot 2026-01-17 131915" src="https://github.com/user-attachments/assets/10d7da1c-4b8f-431f-859a-e356fcf86ba2" />

<img width="1915" height="1029" alt="Screenshot 2026-01-17 131928" src="https://github.com/user-attachments/assets/c9c66388-2d18-4160-a0cb-bdc3042112d0" />

<img width="1912" height="1035" alt="Screenshot 2026-01-17 131939" src="https://github.com/user-attachments/assets/5d6f528f-ff45-489a-8644-433052a6d179" />

<img width="1917" height="1027" alt="Screenshot 2026-01-17 131950" src="https://github.com/user-attachments/assets/b5381164-c46f-498c-89cc-3e433b312466" />

<img width="1913" height="1026" alt="Screenshot 2026-01-17 132015" src="https://github.com/user-attachments/assets/970fa72c-7996-48f8-905b-fda2a638da9d" />

<img width="1908" height="1030" alt="Screenshot 2026-01-17 132032" src="https://github.com/user-attachments/assets/b72fa949-a226-4ce6-a51e-eeb1dfa1b25a" />

<img width="1919" height="969" alt="Screenshot 2026-01-17 132045" src="https://github.com/user-attachments/assets/9d096df8-6996-423d-81cd-3553e1d2af0b" />

<img width="1915" height="1035" alt="Screenshot 2026-01-17 132058" src="https://github.com/user-attachments/assets/93b03c0f-ffd7-46e7-86a3-8fab299f585a" />

<img width="1913" height="1032" alt="Screenshot 2026-01-17 132117" src="https://github.com/user-attachments/assets/d40e3984-92c3-4bfc-b165-f60c07834b63" />

<img width="1914" height="1031" alt="Screenshot 2026-01-17 132126" src="https://github.com/user-attachments/assets/7659e1f8-d4b5-4c4e-87e8-8f57dc5af913" />


---

## 🙌 Contribution  

Contributions, ideas, and suggestions are always welcome!  
Feel free to check the [issues page](https://github.com/StrimCoder/The-BigBull---Stock-Prediction-Model/issues) or submit a pull request.

---

## 📃 License  

This project is **open-source** and available under the [MIT License](LICENSE).

---

## 👑 Created By  

**Bhushan Navsagar** ✨  
[GitHub](https://github.com/StrimCoder) | [LinkedIn](https://www.linkedin.com/in/bhushan-navsagar-2b683a293/)
