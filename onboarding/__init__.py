# onboarding_bp.py

from flask import Blueprint, render_template, redirect, url_for, flash , request
from flask_login import login_required, current_user
from models import User , studentEmergencyDetails ,studentDetails ,TeacherDetails, db
from forms import TeacherDetailsForm, studentDetailsForm , studentEmergencyDetailsForm
from werkzeug.utils import secure_filename
import os

onboarding = Blueprint('onboarding', __name__ , template_folder='templates')
# Initialize UploadSet for documents

@onboarding.route('/onboarding', methods=['GET', 'POST'])
@login_required
def home():
    form = TeacherDetailsForm() if current_user.is_Teacher else studentDetailsForm()
    user_details = current_user.teacher_details if current_user.is_Teacher else current_user.student_details

    if form.validate_on_submit():
        if form.validate_on_submit():
            if current_user.is_Teacher:
                # Save Teacher details
                uploaded_files = request.files.getlist(form.qualifications.name)
                qualifications_paths= []   
                for file in uploaded_files:
                    filename = secure_filename(file.filename)
                    os.makedirs(os.getenv('UPLOADED_DOCUMENTS_DEST'),exist_ok=True)
                    path = os.path.join(os.getenv('UPLOADED_DOCUMENTS_DEST'), filename)
                    file.save(path)
                    qualifications_paths.append(path)
                    

                teacher_details = TeacherDetails(
                    user_id=current_user.id,
                    full_name=form.full_name.data,
                    date_of_birth=form.date_of_birth.data,
                    address=form.address.data,
                    phone_number=form.phone_number.data,
                    gender=form.gender.data,
                    specialty=form.specialty.data,
                    qualifications='\n'.join(qualifications_paths),
                    experience_years=form.experience_years.data,
                    School_name=form.School_name.data,
                    consultation_fee=form.consultation_fee.data
                )
                db.session.add(teacher_details)
            else:
                # Save student details
                student_details = studentDetails(
                    user_id=current_user.id,
                    full_name=form.full_name.data,
                    date_of_birth=form.date_of_birth.data,
                    address=form.address.data,
                    phone_number=form.phone_number.data,
                    gender=form.gender.data,
                    blood_group=form.blood_group.data,
                    allergies=form.allergies.data,
                    medical_history=form.medical_history.data
                )
                db.session.add(student_details)


        current_user.onboard = True
        db.session.commit()
        # Check if student emergency details are missing
        if not current_user.is_Teacher and not current_user.emergency_details:
            flash('Please provide your emergency contact details.', 'info')
            return redirect(url_for('onboarding.emergency_details'))
        
        flash('Onboarding completed successfully!', 'success')
        return redirect(url_for('views.home'))  # Redirect to dashboard or any other route

    return render_template('onboarding.html', form=form)

@login_required
@onboarding.route('/emergency_details', methods=['GET', 'POST'])
def emergency_details():
    if current_user.is_authenticated and not current_user.is_Teacher:
        form = studentEmergencyDetailsForm()

        if form.validate_on_submit():
            emergency_details = studentEmergencyDetails(
                emergency_contact_name=form.emergency_contact_name.data,
                emergency_contact_relationship=form.emergency_contact_relationship.data,
                emergency_contact_phone=form.emergency_contact_phone.data,
                additional_notes=form.additional_notes.data,
                student_id=current_user.id
            )
            db.session.add(emergency_details)
            db.session.commit()
            flash('Emergency contact details saved successfully!', 'success')
            return redirect(url_for('views.home'))  # Redirect to dashboard or any other route

        return render_template('emergency_details.html', form=form)

    return redirect(url_for('auth.login'))  # Redirect to login if user is not authenticated or if user is a Teacher