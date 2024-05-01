# classes.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import  db , Class , Assignment , Resource

classes = Blueprint('classes', __name__, template_folder='templates',static_folder="static",static_url_path='/static/classes')

from flask import render_template, redirect, url_for, request
from forms import ClassForm, AssignmentForm, ResourceForm

from functools import wraps
from datetime import datetime

def student_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.is_Teacher:
            flash('You need to be a student to access this page.', 'danger')
            return redirect(url_for('views.home')) 
        return func(*args, **kwargs)
    return decorated_function

def teacher_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_Teacher:
            flash('You need to be an teacher to access this page.', 'danger')
            return redirect(url_for('views.home'))  
        return func(*args, **kwargs)
    return decorated_function


@classes.route('/create_class', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_class():
    form = ClassForm()
    if form.validate_on_submit():
        # Assuming current_user is available and represents the logged-in teacher
        new_class = Class(title=form.title.data,
                          description=form.description.data,
                          teacher_id=current_user.id)
        db.session.add(new_class)
        db.session.commit()
        return redirect(url_for('views.home'))  # Redirect to the dashboard or any other route
    return render_template('create_class.html', form=form)

@classes.route('/create_assignment/<int:class_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_assignment(class_id):
    form = AssignmentForm()
    if form.validate_on_submit():
        new_assignment = Assignment(title=form.title.data,
                                    description=form.description.data,
                                    due_date=form.due_date.data,
                                    class_id=class_id)
        db.session.add(new_assignment)
        db.session.commit()
        return redirect(url_for('views.home'))  # Redirect to the dashboard or any other route
    return render_template('create_assignment.html', form=form)

@classes.route('/create_resource', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_resource():
    form = ResourceForm()
    if form.validate_on_submit():
        new_resource = Resource(title=form.title.data,
                                description=form.description.data,
                                file_url=form.file_url.data,
                                teacher_id=current_user.id)
        db.session.add(new_resource)
        db.session.commit()
        return redirect(url_for('views.home'))  # Redirect to the dashboard or any other route
    return render_template('create_resource.html', form=form)

@classes.route('/classes')
@login_required
def view_classes():
    classes = Class.query.all()
    return render_template('classes.html', classes=classes)

@classes.route('/class/<int:class_id>')
@login_required
def view_class(class_id):
    # Fetch the class by its ID
    selected_class = Class.query.get(class_id)
    if selected_class:
        due_date_threshold = datetime.now()  # Example due date threshold, replace with the actual due date you want to use

        # Query assignments for a specific class and with a due date greater than the threshold
        assignments = Assignment.query.filter(
            Assignment.class_id == class_id,
            Assignment.due_date > due_date_threshold
        ).all()

        return render_template('class.html', selected_class=selected_class , assignments=assignments)
    else:
        flash('Class not found.', 'error')
        return redirect(url_for('classes.view_classes'))

@classes.route('/edit_class/<int:class_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_class(class_id):
    selected_class = Class.query.get_or_404(class_id)
    form = ClassForm(obj=selected_class)
    if form.validate_on_submit():
        # Update class details based on form data
        selected_class.title = form.title.data
        selected_class.description = form.description.data
        db.session.commit()
        return redirect(url_for('classes.view_classes'))
    return render_template('edit_class.html', form=form, class_id=class_id)

@classes.route('/assignments')
@login_required
def view_assignments():
    assignments = Assignment.query.all()
    return render_template('assignments.html', assignments=assignments)

@classes.route('/assignment/<int:assignment_id>')
@login_required
def view_assignment(assignment_id):
    # Fetch the assignment by its ID
    selected_assignment = Assignment.query.get_or_404(assignment_id)
    return render_template('assignment.html', selected_assignment=selected_assignment)

@classes.route('/edit_assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_assignment(assignment_id):
    selected_assignment = Assignment.query.get_or_404(assignment_id)
    form = AssignmentForm(obj=selected_assignment)
    #form.class_id.choices = [(c.id, c.title) for c in current_user.teacher_details.classes]
    if form.validate_on_submit():
        # Update assignment details based on form data
        selected_assignment.title = form.title.data
        selected_assignment.description = form.description.data
        selected_assignment.due_date = form.due_date.data
        selected_assignment.assigned_class = Class.query.get(form.class_id.data)
        db.session.commit()
        return redirect(url_for('views.home'))  # Redirect to the dashboard or any other route
    return render_template('edit_assignment.html', form=form, assignment_id=assignment_id)
