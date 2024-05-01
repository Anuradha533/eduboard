from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from forms import EmergencyContactForm, TeacherDetailsForm, studentDetailsForm
from models import TeacherDetails, studentDetails, studentEmergencyDetails ,db , User

profile = Blueprint('profile', __name__, template_folder='templates')

@profile.route('/profile', methods=['GET'])
@login_required
def view_profile():
    if current_user.is_Teacher:
        user_details = current_user.teacher_details
        return render_template('teacher_profile.html', user_details=user_details)
    else:
        user_details = current_user.student_details
        emergency_details = current_user.emergency_details
        return render_template('student_profile.html', user_details=user_details, emergency_details=emergency_details)

@profile.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.is_Teacher:
        form = TeacherDetailsForm(obj=current_user.teacher_details)
    else:
        form = studentDetailsForm(obj=current_user.student_details)
    
    if form.validate_on_submit():
        if current_user.is_Teacher:
            user_details = current_user.teacher_details
            form.populate_obj(user_details)
            db.session.commit()
            flash('Teacher details updated successfully!', 'success')
        else:
            user_details = current_user.student_details
            form.populate_obj(user_details)
            db.session.commit()
            flash('student details updated successfully!', 'success')
        
        return redirect(url_for('profile.view_profile'))
    
    return render_template('edit_profile.html', form=form)

@profile.route('/profile/emergency/edit', methods=['GET', 'POST'])
@login_required
def edit_emergency_details():
    if current_user.is_Teacher:
        flash('Only students can update emergency contact details!', 'error')
        return redirect(url_for('profile.view_profile'))
    
    form = EmergencyContactForm(obj=current_user.emergency_details)
    
    if form.validate_on_submit():
        if not current_user.emergency_details:
            emergency_details = studentEmergencyDetails(student_id=current_user.id)
            form.populate_obj(emergency_details)
            db.session.add(emergency_details)
        else:
            form.populate_obj(current_user.emergency_details)
        db.session.commit()
        flash('Emergency contact details updated successfully!', 'success')
        return redirect(url_for('profile.view_profile'))
    
    return render_template('edit_emergency_details.html', form=form)

@profile.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def view_other_profile(user_id):
    user = None
    if current_user.id == user_id:  # If the logged-in user is trying to view their own profile
        if current_user.is_Teacher:
            user_details = current_user.teacher_details
            return render_template('teacher_profile.html', user_details=user_details)
        else:
            user_details = current_user.student_details
            emergency_details = current_user.emergency_details
            return render_template('student_profile.html', user_details=user_details, emergency_details=emergency_details)
    else:  # If a user is trying to view another user's profile
        user = User.query.get(user_id)  # Assuming User is your model for users
        if user:
            if user.is_Teacher:
                user_details = user.teacher_details
                return render_template('teacher_profile.html', user_details=user_details)
            else:
                user_details = user.student_details
                emergency_details = user.emergency_details
                return render_template('student_profile.html', user_details=user_details, emergency_details=emergency_details)
        else:
            flash('User not found!', 'error')
            return redirect(url_for('views.home'))  # Assuming 'home' is the name of your homepage route
