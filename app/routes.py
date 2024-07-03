from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.forms import RegistrationForm, LoginForm, UpdateProfileForm, CreateTripForm
from app.models import User, Trip, Friend
from flask_login import login_user, current_user, logout_user, login_required
import re

@app.route("/")
@app.route("/home")
def home():
    return render_template('base.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    tags = current_user.tags.split(';')[:-1] if current_user.tags else []  
    return render_template('profile.html', user=current_user, tags=tags)

@app.route('/profileid/<int:user_id>')
@login_required
def profileid(user_id):
    user = User.query.get_or_404(user_id)
    tags = user.tags.split(';')[:-1] if current_user.tags else []
    return render_template('profile.html', user=user, tags=tags)
    
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateProfileForm()
    if request.method == 'GET' or not form.validate_on_submit():
        form.username.data = current_user.username
        form.description.data = current_user.description
        form.country.data = current_user.country
        form.city.data = current_user.city
        form.birthdate.data = current_user.birthdate
        form.tags = current_user.tags.split(';')[:-1] if current_user.tags else []
    if form.validate_on_submit():
        if form.delete_account.data:
            db.session.delete(current_user)
            db.session.commit()
            flash('Your account has been deleted.', 'success')
            return redirect(url_for('index'))
        current_user.username = form.username.data
        current_user.description = form.description.data
        current_user.country = form.country.data
        current_user.city = form.city.data
        current_user.birthdate = form.birthdate.data
        current_user.tags = form.tag.data
        db.session.commit()
        return redirect(url_for('profile', username=current_user.username))
    return render_template('edit_profile.html', form=form)

@app.route("/create_trip", methods=['GET', 'POST'])
@login_required
def create_trip():
    form = CreateTripForm()
    if form.validate_on_submit():
        trip = Trip(country=form.country.data, city=form.city.data, start_date=form.start_date.data, end_date=form.end_date.data, user_id=current_user.id)
        db.session.add(trip)
        db.session.commit()
        # Notification logic will go here
        flash('Your trip has been created!', 'success')
        return redirect(url_for('profile'))
    return render_template('create_trip.html', title='Create Trip', form=form)

@app.route('/users')
@login_required
def users():
    users = User.query.all()  # Consulta para obtener todos los usuarios
    return render_template('users.html', users=users)
    
@app.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    # Lógica para manejar las notificaciones
    return render_template('notifications.html', title='Notifications')
    
@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    # Lógica para manejar las notificaciones
    return render_template('messages.html', title='Messages')