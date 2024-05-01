# views.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db ,Appointment, TeacherDetails
from forms import AppointmentForm
import stripe
import os

appointments = Blueprint('appointments', __name__, template_folder='templates')
stripe.api_key = os.getenv('STRIPE_KEY')

@appointments.route('/appointments/create', methods=['GET', 'POST'])
@login_required
def create_appointment():
    form = AppointmentForm()
    form.Teacher_id.choices = [(Teacher.id, Teacher.full_name) for Teacher in TeacherDetails.query.all()]
    if form.validate_on_submit():
        new_appointment = Appointment(
            title=form.title.data,
            description=form.description.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            user_id=form.user_id.data,
            Teacher_id=form.Teacher_id.data
        )
        new_appointment.calculate_total_price(new_appointment.Teacher_id)
        db.session.add(new_appointment)
        db.session.commit()

        if form.skip_payment.data:  # Assuming you have a field in the form for skipping payment
            flash('Appointment created successfully (Payment Skipped)', 'success')
            return redirect(url_for('appointments.checkout_cancel'))  # Redirect to dashboard or any other page
        else:
            product = stripe.Product.create(name="Appointment Booking")

            # Create a Stripe Checkout Session
            price = stripe.Price.create(
                currency="usd",
                unit_amount=int(new_appointment.total_price * 100),
                product = product.id
            )
            session = stripe.checkout.Session.create(
                success_url=url_for('appointments.checkout_success', appointment_id=new_appointment.id, _external=True),
                cancel_url=url_for('appointments.checkout_cancel', _external=True),
                line_items=[{"price": price.id, "quantity": 1}],
                mode="payment",
            )

            flash('Appointment created successfully', 'success')
            # Redirect user to the Stripe Checkout page
            return redirect(session.url, code=303)
    return render_template('create_appointment.html', form=form)

# Define your success and cancel routes for Stripe Checkout
@login_required
@appointments.route('/checkout/success')
def checkout_success():
    # Retrieve the appointment ID from the query parameters
    appointment_id = request.args.get('appointment_id')
    if appointment_id:
        # Find the appointment in the database and mark it as paid
        appointment = Appointment.query.get(appointment_id)
        if appointment:
            appointment.paid = True
            db.session.commit()
            flash('Appointment created and paid successfully', 'success')
        else:
            flash('Appointment not found', 'error')
    else:
        flash('Appointment ID not provided', 'error')
    return redirect(url_for('appointments.get_appointments'))

@login_required
@appointments.route('/checkout/cancel')
def checkout_cancel():
    flash('Appointment creation cancelled', 'warning')
    return redirect(url_for('appointments.get_appointments'))

# Route to view appointments
@login_required
@appointments.route('/appointments', methods=['GET'])
def get_appointments():
    appointments = Appointment.query.all()
    return render_template('appointments.html', appointments=appointments)

@login_required
@appointments.route('/appointments/<int:appointment_id>', methods=['GET'])
def view_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    return render_template('view_appointment.html', appointment=appointment)

# Route to reschedule an appointment
@login_required
@appointments.route('/appointments/<int:appointment_id>/reschedule', methods=['GET', 'POST'])
def reschedule_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    form = AppointmentForm()
    form.Teacher_id.choices = [(Teacher.id, Teacher.full_name) for Teacher in TeacherDetails.query.all()]
    if form.validate_on_submit():
        appointment.start_time = form.start_time.data
        appointment.end_time = form.end_time.data
        appointment.Teacher_id = form.Teacher_id.data
        appointment.calculate_total_price(form.Teacher_id.data)
        db.session.commit()
        flash('Appointment rescheduled successfully', 'success')
        return redirect(url_for('appointments.get_appointments'))
    form.title.data = appointment.title
    form.description.data = appointment.description
    form.start_time.data = appointment.start_time
    form.end_time.data = appointment.end_time
    form.user_id.data = appointment.user_id
    form.Teacher_id.data = appointment.Teacher_id
    return render_template('reschedule_appointment.html', form=form)

# Route to pay for unpaid appointments
@login_required
@appointments.route('/appointments/<int:appointment_id>/pay', methods=['GET'])
def pay_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if not appointment.paid:
        # Create a Stripe Checkout Session
        product = stripe.Product.create(name="Appointment Booking")
        price = stripe.Price.create(
            currency="usd",
            unit_amount=int(appointment.total_price * 100),  # Amount in cents
            product=product.id
        )
        session = stripe.checkout.Session.create(
            success_url=url_for('appointments.checkout_success', appointment_id=appointment.id, _external=True),
            cancel_url=url_for('appointments.checkout_cancel', _external=True),
            payment_method_types=["card"],
            line_items=[{"price": price.id, "quantity": 1}],
            mode="payment",
        )
        flash('Redirecting to payment gateway...', 'info')
        # Redirect user to the Stripe Checkout page
        return redirect(session.url, code=303)
    else:
        flash('Appointment is already paid', 'warning')
        return redirect(url_for('appointments.get_appointments'))


@login_required
@appointments.route('/appointments/<int:appointment_id>/cancel', methods=['GET'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if not appointment.paid:
        db.session.delete(appointment)
        db.session.commit()
        flash('Appointment cancelled successfully', 'success')
    else:
        flash('Cannot cancel paid appointment', 'warning')
    return redirect(url_for('appointments.get_appointments'))