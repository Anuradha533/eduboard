# views.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from forms import TeacherSearchForm , studentSearchForm
from models import TeacherDetails , studentDetails
import os

search = Blueprint('search', __name__, template_folder='templates')

@search.route('/search' , methods=['GET', 'POST'])
@login_required
def home():
    Teacher_form = TeacherSearchForm(request.form)
    student_form = studentSearchForm(request.form)

    if request.method == 'POST':
        if Teacher_form.validate():
            specialty = Teacher_form.specialty.data
            location = Teacher_form.location.data
            experience = Teacher_form.experience.data
            fee = Teacher_form.fee.data

            # Perform Teacher search based on form data
            Teachers = TeacherDetails.query

            if specialty:
                Teachers = Teachers.filter_by(specialty=specialty)
            if location:
                Teachers = Teachers.filter(TeacherDetails.address.ilike(f'%{location}%'))
            if experience is not None:
                Teachers = Teachers.filter(TeacherDetails.experience_years >= experience)
            if fee is not None:
                Teachers = Teachers.filter(TeacherDetails.consultation_fee <= fee)

            Teachers = Teachers.all()

            return render_template('search_results.html', items=Teachers, type='Teacher',agoraAppID=os.getenv('AGORA_APP_ID'))

        elif student_form.validate():
            blood_group = student_form.blood_group.data
            allergies = student_form.allergies.data
            medical_history = student_form.medical_history.data

            # Perform student search based on form data
            students = studentDetails.query

            if blood_group:
                students = students.filter_by(blood_group=blood_group)
            if allergies:
                students = students.filter(studentDetails.allergies.ilike(f'%{allergies}%'))
            if medical_history:
                students = students.filter(studentDetails.medical_history.ilike(f'%{medical_history}%'))

            students = students.all()

            return render_template('search_results.html', items=students, type='student')

    return render_template('search.html', Teacher_form=Teacher_form, student_form=student_form)