# views.py
from flask import Blueprint, render_template, send_from_directory
from flask_login import login_required, current_user
from models import Appointment , Class , Assignment
import os
import json


views = Blueprint('views', __name__, template_folder='templates',static_folder="static",static_url_path='/static/views')
specialties_file_path = os.path.join(os.getcwd(), 'data', 'specialties.json')
with open(specialties_file_path, 'r') as file:
        data = json.load(file)

@views.route('/')
def index():
    return render_template('index.html')

@views.route('/dashboard')
@login_required
def home():
    classes = Class.query.all()
    assignments = Assignment.query.all()
    if not current_user.is_Teacher:
        appointments = Appointment.query.filter_by(user_id=current_user.id).all()
        classes = Class.query.filter_by(teacher_id=current_user.id).all()
        #assignments = Assignment.query.filter_by(Teacher_id=current_user.id).all()

    else:
        appointments = Appointment.query.filter_by(Teacher_id=current_user.id).all()
    return render_template('dashboard.html',  appointments=appointments , classes=classes , assignments=assignments)

@views.route('/courses')
@login_required
def courses():
   return render_template('courses.html', courses=data["Teacher_specialties"])

@views.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(views.root_path, 'static'),'eduboard-favicon-black.ico', mimetype='image/vnd.microsoft.icon')
