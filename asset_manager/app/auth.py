from flask import Blueprint, render_template, redirect, url_for, flash
from . import db
from .models import User
from .forms import LoginForm, RegisterForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

auth = Blueprint('auth', __name__)

MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.asset_list'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if user and user.locked_until and user.locked_until > datetime.utcnow():
            flash('Account temporarily locked. Please try again later.', 'danger')
            return render_template('login.html', form=form)

        if user and check_password_hash(user.password, password):
            user.failed_login_attempts = 0
            user.locked_until = None
            db.session.commit()
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.asset_list'))
        else:
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
                    user.failed_login_attempts = 0
                db.session.commit()
            flash('Invalid credentials. Please try again.', 'danger')

    elif form.is_submitted():
        for errors in form.errors.values():
            for error in errors:
                flash(error, 'danger')

    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.asset_list'))

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('auth.register'))
        
        new_user = User(
            username=username, 
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    elif form.is_submitted():
        for errors in form.errors.values():
            for error in errors:
                flash(error, 'danger')

    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))
