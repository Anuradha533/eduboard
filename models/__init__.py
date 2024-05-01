from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import secrets
import json

db = SQLAlchemy()


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_Teacher = db.Column(db.Boolean, default=False)
    onboard = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(32), unique=True, default=None)
    reset_token_expiration = db.Column(db.DateTime, default=None)
    verify_token = db.Column(db.String(32), unique=True, default=None)
    verify_token_expiration = db.Column(db.DateTime, default=None)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    icon = db.Column(db.String(120), nullable=False)
   
    def get_verify_token(self):
        return secrets.token_hex(32)

    def get_reset_token(self):
        return secrets.token_hex(32)
    
    def to_json(self):
        return dict(id=self.id,
                    username=self.email,
                    email=self.email)
    
    @staticmethod
    def verify_reset_token(token):
        user = User.query.filter_by(reset_token=token).first()
        if user and user.reset_token_expiration > datetime.utcnow():
            return user
        return None

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    Teacher_id = db.Column(db.Integer, db.ForeignKey('teacher_details.id'), nullable=False)
    total_price = db.Column(db.Float)
    paid = db.Column(db.Boolean, default=False)

    # Relationship to User
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))
    Teacher = db.relationship('TeacherDetails', backref=db.backref('appointments', lazy=True))

    def calculate_total_price(self,id):
        Teacher = TeacherDetails.query.filter_by(id=id).first()
        duration_hours = (self.end_time - self.start_time).total_seconds() / 3600
        self.total_price = duration_hours * Teacher.consultation_fee

    
class studentDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(200))
    phone_number = db.Column(db.String(15))
    gender = db.Column(db.String(10))
    blood_group = db.Column(db.String(5))
    allergies = db.Column(db.String(200))
    medical_history = db.Column(db.Text)

    # Relationship to User
    user = db.relationship('User', backref=db.backref('student_details', uselist=False), lazy=True)

    def to_json(self):
        return dict(id=self.id,
                    username=self.full_name,
                    email=self.full_name)

    def __repr__(self):
        return f"studentDetails('{self.full_name}', '{self.date_of_birth}', '{self.address}', '{self.phone_number}', '{self.gender}', '{self.blood_group}', '{self.allergies}', '{self.medical_history}')"

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symptoms = db.Column(db.String(200))
    diagnosis = db.Column(db.String(200))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    Teacher_name = db.Column(db.String(100))
    treatment = db.Column(db.Text)
    prescription = db.Column(db.Text)

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"MedicalRecord('{self.symptoms}', '{self.diagnosis}', '{self.date_created}', '{self.Teacher_name}', '{self.treatment}', '{self.prescription}')"

class TeacherDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(200))
    phone_number = db.Column(db.String(15))
    gender = db.Column(db.String(10))
    specialty = db.Column(db.String(100), nullable=False)
    qualifications = db.Column(db.Text)
    experience_years = db.Column(db.Integer)
    School_name = db.Column(db.String(100))
    consultation_fee = db.Column(db.Float)

    # Relationship to User
    user = db.relationship('User', backref=db.backref('teacher_details', uselist=False), lazy=True)
    #resources = db.relationship('Resource', backref=db.backref('teacher', lazy=True))

    def to_json(self):
        return dict(id=self.id,
                    username=self.full_name,
                    email=self.full_name)

    def __repr__(self):
        return f"TeacherDetails('{self.full_name}', '{self.date_of_birth}', '{self.address}', '{self.phone_number}', '{self.gender}', '{self.specialty}', '{self.qualifications}', '{self.experience_years}', '{self.School_name}', '{self.consultation_fee}')"

class studentEmergencyDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    emergency_contact_name = db.Column(db.String(100), nullable=False)
    emergency_contact_relationship = db.Column(db.String(100), nullable=False)
    emergency_contact_phone = db.Column(db.String(15), nullable=False)
    additional_notes = db.Column(db.Text)

    # Relationship to User (student)
    student = db.relationship('User', backref=db.backref('emergency_details', uselist=False), lazy=True)

    def __repr__(self):
        return f"studentEmergencyDetails('{self.emergency_contact_name}', '{self.emergency_contact_relationship}', '{self.emergency_contact_phone}')"


class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher_details.id'), nullable=False)

    # Relationship to Teacher
    teacher = db.relationship('TeacherDetails', backref=db.backref('classes', lazy=True))


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)

    # Relationship to Class
    assigned_class = db.relationship('Class', backref=db.backref('assignments', lazy=True))

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    submission_time = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.Text)
    grade = db.Column(db.Float)

    # Relationships to Assignment and Student
    assignment = db.relationship('Assignment', backref=db.backref('submissions', lazy=True))
    student = db.relationship('User', backref=db.backref('submissions', lazy=True))

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    file_url = db.Column(db.String(255), nullable=False)  # Assuming you'll store the file URL
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher_details.id'), nullable=False)

    # Relationship to Teacher
    teacher = db.relationship('TeacherDetails', backref=db.backref('resources', lazy=True))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    
    user = db.relationship('User', backref='notifications')