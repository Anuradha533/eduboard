from flask_wtf import FlaskForm
from wtforms import StringField,DecimalField,SelectField, PasswordField, BooleanField, DateField, IntegerField, TextAreaField, SelectField , SubmitField , DateTimeLocalField,FloatField , MultipleFileField,  HiddenField
from wtforms.validators import DataRequired, Email, Length ,EqualTo ,Optional , NumberRange
import json
import os
from wtforms.validators import ValidationError

# Get the path to the JSON file
specialties_file_path = os.path.join(os.getcwd(), 'data', 'specialties.json')
courses_file_path = os.path.join(os.getcwd(), 'data', 'allergies.json')

blood_group_choices = [('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')]

# Load Teacher specialties from JSON file
with open(specialties_file_path, 'r') as file:
    specialties_data = json.load(file)
    specialty_choices = [(spec['name'], spec['name']) for spec in specialties_data['Teacher_specialties']]

with open(courses_file_path, 'r') as file:
    courses_data = json.load(file)
    allergy_choices = [(allergy['name'], allergy['name']) for allergy in courses_data['student_allergies']]


def school_email(form, field):
    allowed_tlds = ['edu' , 'com']  # List of valid top-level domains
    domain = field.data.split('@')[-1].split('.')[-1]
    if domain not in allowed_tlds:
        raise ValidationError(f'Only {allowed_tlds} emails are allowed.')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120), school_email])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_Teacher = BooleanField('Are you a Teacher?')
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=60)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationFormold(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_Teacher = BooleanField('Are you a Teacher?')
    submit = SubmitField('Sign Up')

class LoginFormold(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=60)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

# Define forms
class AppointmentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    start_time = DateTimeLocalField('Start Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_time = DateTimeLocalField('End Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    user_id = HiddenField('User ID')
    Teacher_id = SelectField('Teacher', coerce=int, validators=[DataRequired()])
    skip_payment = BooleanField('Skip Prepay?')
    submit = SubmitField('Submit')


class studentDetailsForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    address = StringField('Address', validators=[Length(max=200)])
    phone_number = StringField('Phone Number', validators=[Length(max=15)])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=blood_group_choices , validators=[Length(max=5)])
    allergies = SelectField('Allergies',choices=allergy_choices ,  validators=[Length(max=200)])
    medical_history = TextAreaField('Medical History')

class MedicalRecordForm(FlaskForm):
    symptoms = StringField('Symptoms', validators=[Length(max=200)])
    diagnosis = StringField('Diagnosis', validators=[Length(max=200)])
    Teacher_name = StringField('Teacher Name', validators=[DataRequired(), Length(max=100)])
    treatment = TextAreaField('Treatment')
    prescription = TextAreaField('Prescription')

class TeacherDetailsForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired(), Length(max=200)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=15)])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    specialty = SelectField('Specialty', choices=specialty_choices, validators=[DataRequired()])
    qualifications = MultipleFileField('Qualification Documents', validators=[DataRequired()])
    experience_years = IntegerField('Experience (Years)', validators=[DataRequired()])
    School_name = StringField('School Name', validators=[DataRequired(), Length(max=100)])
    consultation_fee = FloatField('Consultation Fee (Per Hour)', validators=[DataRequired()])

class studentDetailsForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired(), Length(max=200)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=15)])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=blood_group_choices , validators=[DataRequired(), Length(max=5)])
    allergies =  SelectField('Allergies', choices=allergy_choices,validators=[DataRequired(), Length(max=200)])
    medical_history = TextAreaField('Medical History', validators=[DataRequired()])

class studentEmergencyDetailsForm(FlaskForm):
    emergency_contact_name = StringField('Emergency Contact Name', validators=[DataRequired(), Length(max=100)])
    emergency_contact_relationship = StringField('Relationship to student', validators=[DataRequired(), Length(max=100)])
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[DataRequired(), Length(max=15)])
    additional_notes = TextAreaField('Additional Notes')

class TeacherSearchForm(FlaskForm):
    specialty = SelectField('Specialty', choices=specialty_choices, validators=[DataRequired()])
    location = StringField('Location')
    experience = IntegerField('Minimum Experience (years)', validators=[Optional(), NumberRange(min=0)])
    fee = DecimalField('Maximum Consultation Fee ($)', validators=[Optional(), NumberRange(min=0)])

# Define the WTForm for student search
class studentSearchForm(FlaskForm):
    blood_group = SelectField('Blood Group', choices=blood_group_choices , validators=[DataRequired()])
    allergies = SelectField('Allergies',choices=allergy_choices ,  validators=[DataRequired()])
    medical_history = StringField('Medical History')

class EmergencyContactForm(FlaskForm):
    emergency_contact_name = StringField('Emergency Contact Name', validators=[DataRequired()])
    emergency_contact_relationship = StringField('Relationship', validators=[DataRequired()])
    emergency_contact_phone = StringField('Phone Number', validators=[DataRequired()])
    additional_notes = TextAreaField('Additional Notes')

class ClassForm(FlaskForm):
    title = SelectField('Title', choices=specialty_choices, validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Create Class')

class AssignmentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    due_date = DateTimeLocalField('Due Date', validators=[DataRequired()])
    submit = SubmitField('Create Assignment')

class ResourceForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    file_url = StringField('File URL', validators=[DataRequired()])
    submit = SubmitField('Create Resource')

class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')
