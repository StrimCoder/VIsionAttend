from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from .database import User, Attendance, Class, Enrollment
import json

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
    
    def send_notification(self, user_id: int, message: str, notification_type: str):
        """Send notification to user (placeholder for actual implementation)"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # In a real implementation, you would integrate with:
        # - SMS service (Twilio, AWS SNS)
        # - Email service (SendGrid, AWS SES)
        # - Push notification service (Firebase, OneSignal)
        
        print(f"📱 NOTIFICATION [{notification_type}] to {user.full_name} ({user.phone_number}): {message}")
        return True
    
    def send_sms(self, phone_number: str, message: str):
        """Send SMS notification (placeholder)"""
        print(f"📱 SMS to {phone_number}: {message}")
        return True
    
    def send_email(self, email: str, subject: str, message: str):
        """Send email notification (placeholder)"""
        print(f"📧 EMAIL to {email}: {subject} - {message}")
        return True
    
    def check_late_arrivals(self, class_id: int, expected_start_time: datetime):
        """Check for students who arrived late"""
        late_threshold = expected_start_time + timedelta(minutes=15)
        
        # Get all enrolled students
        enrollments = self.db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
        
        for enrollment in enrollments:
            # Check if student marked attendance after late threshold
            late_attendance = self.db.query(Attendance).filter(
                Attendance.user_id == enrollment.user_id,
                Attendance.class_id == class_id,
                Attendance.timestamp > late_threshold,
                Attendance.timestamp >= expected_start_time.date()
            ).first()
            
            if late_attendance:
                self.notify_late_arrival(enrollment.user_id, class_id, late_attendance.timestamp)
    
    def check_absences(self, class_id: int, class_end_time: datetime):
        """Check for students who didn't attend"""
        # Get all enrolled students
        enrollments = self.db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
        
        for enrollment in enrollments:
            # Check if student marked attendance today
            today_attendance = self.db.query(Attendance).filter(
                Attendance.user_id == enrollment.user_id,
                Attendance.class_id == class_id,
                Attendance.timestamp >= class_end_time.date()
            ).first()
            
            if not today_attendance:
                self.notify_absence(enrollment.user_id, class_id)
    
    def notify_late_arrival(self, user_id: int, class_id: int, arrival_time: datetime):
        """Send late arrival notifications"""
        user = self.db.query(User).filter(User.id == user_id).first()
        class_obj = self.db.query(Class).filter(Class.id == class_id).first()
        
        if not user or not class_obj:
            return
        
        message = f"⏰ Late Arrival Alert: {user.full_name} arrived late to {class_obj.name} at {arrival_time.strftime('%H:%M')}"
        
        # Notify student
        self.send_notification(user_id, f"You arrived late to {class_obj.name}. Please try to be on time.", "LATE_ARRIVAL")
        
        # Notify parent if student
        if user.role == "student" and user.parent_phone:
            self.send_sms(user.parent_phone, f"Your child {user.full_name} arrived late to {class_obj.name}")
        
        # Notify teacher
        if class_obj.teacher_id:
            self.send_notification(class_obj.teacher_id, message, "STUDENT_LATE")
    
    def notify_absence(self, user_id: int, class_id: int):
        """Send absence notifications"""
        user = self.db.query(User).filter(User.id == user_id).first()
        class_obj = self.db.query(Class).filter(Class.id == class_id).first()
        
        if not user or not class_obj:
            return
        
        message = f"❌ Absence Alert: {user.full_name} was absent from {class_obj.name}"
        
        # Notify student
        self.send_notification(user_id, f"You were marked absent from {class_obj.name}. Please contact your teacher if this is incorrect.", "ABSENCE")
        
        # Notify parent if student
        if user.role == "student" and user.parent_phone:
            self.send_sms(user.parent_phone, f"Your child {user.full_name} was absent from {class_obj.name}")
        
        # Notify teacher
        if class_obj.teacher_id:
            self.send_notification(class_obj.teacher_id, message, "STUDENT_ABSENT")
    
    def notify_early_leave(self, user_id: int, class_id: int, leave_time: datetime):
        """Send early leave notifications"""
        user = self.db.query(User).filter(User.id == user_id).first()
        class_obj = self.db.query(Class).filter(Class.id == class_id).first()
        
        if not user or not class_obj:
            return
        
        message = f"🚪 Early Leave Alert: {user.full_name} left {class_obj.name} early at {leave_time.strftime('%H:%M')}"
        
        # Notify parent if student
        if user.role == "student" and user.parent_phone:
            self.send_sms(user.parent_phone, f"Your child {user.full_name} left {class_obj.name} early")
        
        # Notify teacher
        if class_obj.teacher_id:
            self.send_notification(class_obj.teacher_id, message, "STUDENT_EARLY_LEAVE")
    
    def send_meeting_reminder(self, class_id: int, reminder_time: int = 30):
        """Send meeting reminders (X minutes before class)"""
        class_obj = self.db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            return
        
        # Get all enrolled students
        enrollments = self.db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
        
        message = f"📅 Reminder: {class_obj.name} starts in {reminder_time} minutes at {class_obj.location}"
        
        for enrollment in enrollments:
            self.send_notification(enrollment.user_id, message, "MEETING_REMINDER")
        
        # Notify teacher
        if class_obj.teacher_id:
            self.send_notification(class_obj.teacher_id, f"Reminder: Your class {class_obj.name} starts in {reminder_time} minutes", "MEETING_REMINDER")
    
    def send_daily_summary(self, user_id: int):
        """Send daily attendance summary"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return
        
        today = datetime.utcnow().date()
        
        if user.role == "student":
            # Student summary
            today_attendances = self.db.query(Attendance).filter(
                Attendance.user_id == user_id,
                Attendance.timestamp >= today
            ).count()
            
            enrolled_classes = self.db.query(Enrollment).filter(Enrollment.user_id == user_id).count()
            
            message = f"📊 Daily Summary: You attended {today_attendances} out of {enrolled_classes} classes today."
            self.send_notification(user_id, message, "DAILY_SUMMARY")
            
            # Send to parent
            if user.parent_phone:
                self.send_sms(user.parent_phone, f"Daily Summary for {user.full_name}: Attended {today_attendances}/{enrolled_classes} classes")
        
        elif user.role == "teacher":
            # Teacher summary
            my_classes = self.db.query(Class).filter(Class.teacher_id == user_id).all()
            total_attendances = 0
            
            for class_obj in my_classes:
                class_attendances = self.db.query(Attendance).filter(
                    Attendance.class_id == class_obj.id,
                    Attendance.timestamp >= today
                ).count()
                total_attendances += class_attendances
            
            message = f"📊 Daily Summary: {total_attendances} total attendances across your {len(my_classes)} classes today."
            self.send_notification(user_id, message, "DAILY_SUMMARY")
    
    def get_notification_preferences(self, user_id: int):
        """Get user notification preferences"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.notification_preferences:
            return ["email", "sms"]
        
        try:
            return json.loads(user.notification_preferences)
        except:
            return ["email", "sms"]
    
    def update_notification_preferences(self, user_id: int, preferences: List[str]):
        """Update user notification preferences"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.notification_preferences = json.dumps(preferences)
        self.db.commit()
        return True