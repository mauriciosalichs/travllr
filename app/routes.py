from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.forms import RegistrationForm, LoginForm, UpdateProfileForm, CreateTripForm, SearchForm
from app.models import User, Trip, Friend
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy import or_
import re
import base64
from datetime import datetime, date, timedelta

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
            if current_user.last_login:
                current_user.last_login = datetime.utcnow()
                db.session.commit()
                return redirect(url_for('home'))
            else:
                current_user.last_login = datetime.utcnow()
                db.session.commit()
                form = UpdateProfileForm()
                form.username.data = current_user.username
                return render_template('edit_profile.html', form=form)
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    tags = user.tags.split(';')[:-1] if user.tags else []  
    return render_template('profile.html', user=user, tags=tags)
    
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateProfileForm()
    if request.method == 'GET' or not form.validate_on_submit():
        form.username.data = current_user.username
        form.gender.data = current_user.gender
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
        current_user.gender = form.gender.data
        current_user.tags = form.tag.data
        current_user.description = form.description.data
        current_user.country = form.country.data
        current_user.city = form.city.data
        current_user.birthdate = form.birthdate.data
        current_user.tags = form.tag.data
        if form.file.data:
            image_data = form.file.data.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            current_user.image_file = image_base64
        db.session.commit()
        return redirect(url_for('profile', user_id=current_user.id))
    return render_template('edit_profile.html', form=form)

@app.route("/edit_trip/<int:trip_id>", methods=['GET', 'POST'])
@login_required
def edit_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    form = CreateTripForm()
    if request.method == 'GET' or not form.validate_on_submit():
        form.country.data = trip.country
        form.city.data = trip.city
        form.start_date.data = trip.start_date
        form.end_date.data = trip.end_date
        form.comments.data = trip.comments
    if form.validate_on_submit():
        trip.start_date = form.start_date.data
        trip.end_date = form.end_date.data
        trip.comments = form.comments.data
        db.session.commit()
        flash('Your trip has been edited!', 'success')
        return redirect(url_for('profile', user_id=current_user.id))
    return render_template('edit_trip.html', trip=trip, form=form)
    
@app.route("/create_trip", methods=['GET', 'POST'])
@login_required
def create_trip():
    form = CreateTripForm()
    if form.validate_on_submit():
        trip = Trip(country=form.country.data,
                    city=form.city.data,
                    start_date=form.start_date.data,
                    end_date=form.end_date.data,
                    comments=form.comments.data,
                    user_id=current_user.id)
        db.session.add(trip)
        db.session.commit()
        print("TRIP",trip.id)
        flash('Your trip has been created!', 'success')
        return redirect(url_for('profile', user_id=current_user.id))
    return render_template('create_trip.html', title='Create Trip', form=form)
    
@app.route('/search', methods=['GET','POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        keyword = form.keyword.data
        min_age = form.min_age.data
        max_age = form.max_age.data
        country = form.country.data
        sorted = form.sorted.data
        query = User.query
        
        if current_user:
            query = query.filter(User.id != current_user.id)
        if keyword:
            query = query.filter((User.description.ilike(f'%{keyword}%'))
                                |(User.username.ilike(f'%{keyword}%'))
                                |(User.tags.ilike(f'%{keyword}%')))
        if min_age:
            today = date.today()
            threshold_birthdate = today.replace(year=today.year - int(min_age))
            query = query.filter(User.birthdate <= threshold_birthdate)
        if max_age:
            today = date.today()
            threshold_birthdate = today.replace(year=today.year - int(max_age))
            query = query.filter(User.birthdate >= threshold_birthdate)
        if country:
            query = query.filter(User.country == country)
        if sorted == 'Alphabetical':
            query = query.order_by(User.username)
        elif sorted == 'Last Login':
            query = query.order_by(User.last_login.desc())
        return render_template('users.html', users=query.all())
    else:
        print(form.errors)
    return render_template('search.html', form=form)
    
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