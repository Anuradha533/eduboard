from flask import Blueprint, render_template, flash, redirect, url_for , session
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from flask_mail import Mail, Message
from flask_avatars import Avatars
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegistrationForm , PasswordResetRequestForm , ResetPasswordForm
from models import User, db
import datetime
import hashlib

auth = Blueprint('auth', __name__, template_folder='templates')
login_manager = LoginManager()
avatars = Avatars()
mail = Mail()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
online_users = {}


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            online_users[user.id] = {
                'id': user.id,
                'email': user.email,
                'icon': user.icon,
            }
            if user.verified:
                flash('Logged in successfully!', category='success')
                login_user(user, remember=form.remember.data)
                session['user_id'] = user.id
                if user.onboard:
                    return redirect(url_for('views.home'))
                else:
                    return redirect(url_for('onboarding.home'))
            else:
                send_verification_email(user)
                flash('A verification email has been sent to your email address. Please verify your account.',
                      category='info')
                return redirect(url_for('auth.login'))
        else:
            flash('Incorrect email or password.', category='error')
    return render_template('login.html', form=form)


def send_verification_email(user):
    user.verify_token = user.get_verify_token()
    user.verify_token_expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    db.session.commit()

    msg = Message('Verify Your Email', sender='noreply@example.com', recipients=[user.email])
    msg.body = f'''
            To verify your email, visit the following link: {url_for('auth.verify_email', token=user.verify_token, _external=True)}

            If you did not make this request, simply ignore this email.
            '''
    mail.send(msg)

def send_password_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@example.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
            {url_for('auth.reset_password', token=token, _external=True)}

            If you did not make this request, simply ignore this email and no changes will be made.
            '''
    mail.send(msg)
    
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', category='error')
        else:
            create_user_from_registration_form(form)
            flash('Account created!', category='success')
            return redirect(url_for('auth.login'))
    return render_template('registration.html', form=form, user=current_user)


def create_user_from_registration_form(form):
    new_user = User(
        is_Teacher=form.is_Teacher.data,
        email=form.email.data,
        password=generate_password_hash(form.password.data, method='pbkdf2:sha256'),
        icon=avatars.gravatar(hashlib.md5(form.email.data.lower().encode('utf-8')).hexdigest())
    )
    db.session.add(new_user)
    db.session.commit()


@auth.route('/logout')
@login_required
def logout():
    # Remove the user from the dictionary of online users
    if current_user.id in online_users:
        del online_users[current_user.id]
    session.pop('user_id', None)
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    user = User.query.filter_by(verify_token=token).first()
    if user:
        if user.verify_token_expiration > datetime.datetime.utcnow():
            user.verified = True
            db.session.commit()
            flash('Your email has been verified. You can now log in.', category='success')
        else:
            flash('The verification link has expired. Please request a new one.', category='warning')
    else:
        flash('Invalid verification link.', category='error')
    return redirect(url_for('auth.login'))


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for instructions to reset your password.', category='info')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired token.', category='error')
        return redirect(url_for('auth.reset_password_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', category='success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html', form=form)
