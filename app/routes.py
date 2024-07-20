from flask import render_template, url_for, flash, redirect, request, jsonify
from app import app, db
from app.forms import RegistrationForm, LoginForm, UpdateProfileForm, CreateTripForm, SearchForm, fetch_cities_from, countries_list
from app.models import User, Trip, Message, Friend, Location
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_
import re, base64
from datetime import datetime, date, timedelta


# Variables
unread_messages = 0
pending_requests = 0

@app.context_processor
def inject_global_vars():
    return {
        'unread_messages': unread_messages,
        'pending_requests': pending_requests
    }

@app.route('/countries', methods=['GET'])
def countries():
    return countries_list
    
@app.route('/cities', methods=['GET'])
def cities():
    country = request.args.get('country')
    return fetch_cities_from(country)
    
@app.route("/")
@app.route("/home")
def home():
    global unread_messages, pending_requests
    if current_user.is_authenticated:
        unread_messages = len(Message.query.filter(
                                      Message.receiver_id == current_user.id,
                                      Message.read == False).all())
        pending_requests = len(Friend.query.filter(
                                      Friend.friend_id == current_user.id,
                                      Friend.is_accepted == False).all())
        return render_template('base.html')
    else:
        return login()

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        users = User.query.filter(User.email == form.email.data).all()
        if users:
            flash('Email account already in use!', 'danger')
            return render_template('register.html', title='Register', form=form)
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    global unread_messages
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
                unread_messages = len(Message.query.filter(
                                      Message.receiver_id == current_user.id,
                                      Message.read == False).all())
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
    trips = Trip.query.filter_by(user_id=user_id).order_by(Trip.start_date.asc()).all()
    
    past_trips = []
    current_trip = None
    future_trips = []
    today = date.today()

    for trip in trips:
        if trip.end_date < today:
            past_trips.append(trip)
        elif trip.start_date <= today <= trip.end_date:
            current_trip = trip
        else:
            future_trips.append(trip)
    print(current_trip)
    tags = user.tags.split(';')[:-1] if user.tags else []  
    return render_template('profile.html', user=user, tags=tags, past_trips=past_trips, current_trip=current_trip, future_trips=future_trips)
    
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateProfileForm()
    if request.method == 'GET' or not form.validate_on_submit():
        print("F",form)
        form.username.data = current_user.username
        form.gender.data = current_user.gender
        form.description.data = current_user.description
        form.country.data = current_user.country
        form.city.data = current_user.city
        form.birthdate.data = current_user.birthdate
        form.tags = current_user.tags.split(';')[:-1] if current_user.tags else []
    if form.validate_on_submit():
        print('G',form)
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
    if trip.user_id != current_user.id:
        return redirect(url_for('profile', user_id=trip.user_id))
        
    form = CreateTripForm()
    if request.method == 'POST':
        trip.start_date = form.start_date.data
        trip.end_date = form.end_date.data
        trip.comments = form.comments.data
        db.session.commit()
        flash('Your trip has been edited!', 'success')
        return redirect(url_for('profile', user_id=current_user.id))
    if request.method == 'GET' or not form.validate_on_submit():
        form.country.data = trip.country
        form.city.data = trip.city
        form.start_date.data = trip.start_date
        form.end_date.data = trip.end_date
        form.comments.data = trip.comments
    return render_template('edit_trip.html', trip=trip, form=form)
    
@app.route("/create_trip", methods=['GET', 'POST'])
@login_required
def create_trip():
    form = CreateTripForm()
    if form.validate_on_submit():
        overlapping_trips = Trip.query.filter(Trip.user_id == current_user.id,
        db.or_(
            db.and_(Trip.start_date <= form.start_date.data, Trip.end_date >= form.start_date.data),
            db.and_(Trip.start_date <= form.end_date.data, Trip.end_date >= form.end_date.data),
            db.and_(Trip.start_date >= form.start_date.data, Trip.end_date <= form.end_date.data)
        )).all()
        
        if overlapping_trips:
            trip = overlapping_trips[0]
            flash(f'Error: Trip dates overlap with an existing trip to {trip.city}, {trip.country} from {trip.start_date} to {trip.end_date}.', 'error')
            return render_template('create_trip.html', title='Create Trip', form=form)
    
        trip = Trip(country=form.country.data,
                    city=form.city.data,
                    start_date=form.start_date.data,
                    end_date=form.end_date.data,
                    comments=form.comments.data,
                    user_id=current_user.id)
        db.session.add(trip)
        db.session.commit()
        flash('Your trip has been created!', 'success')
        return redirect(url_for('profile', user_id=current_user.id))
    return render_template('create_trip.html', title='Create Trip', form=form)

@app.route('/delete_trip/<int:trip_id>', methods=['GET','POST'])
def delete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    print(trip.id, current_user.id)
    if trip.user_id != current_user.id:
        return redirect(url_for('profile', user_id=trip.user_id))
    db.session.delete(trip)
    db.session.commit()
    return redirect(url_for('profile', user_id=trip.user_id))
    
def count_matching_tags(user_tags, current_user_tags_set):
    user_tags_set = set(user_tags.split(';'))
    return len(user_tags_set & current_user_tags_set)

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
            users=query.all()
        elif sorted == 'Last Login':
            query = query.order_by(User.last_login.desc())
            users=query.all()
        elif sorted == 'Tag Match':
            users = query.all()
            current_user_tags = set(current_user.tags.split(';'))
            users.sort(key=lambda u: count_matching_tags(u.tags, current_user_tags), reverse=True)
        return render_template('users.html', users=users)
    else:
        print(form.errors)
    return render_template('search.html', form=form)
    
@app.route("/city/<country>/<city>", methods=['GET', 'POST'])
@login_required
def city(city, country):
    location = Location(city, country)
    travllrs = User.query.filter(User.city==city,User.country==country).order_by(User.last_login.asc()).all()
    return render_template('city.html', location=location, travllrs=travllrs)

@app.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    # Lógica para manejar las notificaciones
    return render_template('notifications.html', title='Notifications')

# -------- Messages --------

@app.route('/message/<int:user_id>', methods=['GET', 'POST'])
def message(user_id):
    other = User.query.get(user_id) 
    conversation_messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()
    for message in conversation_messages:
        if message.sender_id != current_user.id:
            message.read = True
    db.session.commit()
    return render_template('message.html', other=other, messages=conversation_messages)
    
@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    global unread_messages
    unread_messages = 0
    users = User.query.all()
    conversations = []
    for user in users:
        last_message = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == user.id)) |
            ((Message.sender_id == user.id) & (Message.receiver_id == current_user.id))
        ).order_by(Message.timestamp.desc()).first()       
        if last_message:
            conversations.append({
                'user': user,
                'last_message': last_message,
                'mysent': last_message.sender_id == current_user.id
            })
    conversations.sort(key=lambda c: c['last_message'].timestamp, reverse=True)
    return render_template('messages.html', conversations=conversations)

@app.route('/send_message/<int:user_id>', methods=['GET','POST'])
@login_required
def send_message(user_id):
    if user_id == current_user.id:
        return jsonify({"error": "Cant send a message to you"}), 403
    content = request.form['message']
    new_message = Message(sender_id=current_user.id, receiver_id=user_id, content=content)
    db.session.add(new_message)
    db.session.commit()
    return jsonify(new_message=content)

@app.route('/check_new_messages/<int:user_id>', methods=['GET'])
@login_required
def check_new_messages(user_id):
    check_time = datetime.utcnow() - timedelta(seconds=5)
    new_messages = Message.query.filter(
        (Message.sender_id == user_id) & (Message.receiver_id == current_user.id),
        Message.timestamp > check_time).order_by(Message.timestamp.asc()).all()
    messages_contents=[message.content for message in new_messages]
    return jsonify(new_messages=messages_contents)
    
@app.route('/delete_conversations/<user_ids>', methods=['GET','POST'])
@login_required
def delete_converations(user_ids):
    list_ids = user_ids.split(',')
    conversation_messages = []
    for user_id in list_ids:
        conversation_messages += Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
            ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))).all()
    for conv in conversation_messages:
        db.session.delete(conv)
    db.session.commit()
    return messages()

# -------- Friends requests --------

@app.route('/send_friend_request/<int:user_id>', methods=['POST'])
@login_required
def send_friend_request(user_id):
    friend_id = user_id
    message = request.form.get('message')
    # Check if request already exists
    existing_request = Friend.query.filter_by(user_id=current_user.id, friend_id=friend_id).first()
    if existing_request:
        return jsonify({"error": "Request already exists"}), 400
    friend_request = Friend(user_id=current_user.id, friend_id=friend_id, message=message)
    db.session.add(friend_request)
    db.session.commit()
    return jsonify({"status": "Request sent"}), 200

@app.route('/accept_friend_request/<int:user_id>', methods=['GET','POST'])
@login_required
def accept_friend_request(user_id):
    friend_request = Friend.query.filter(Friend.user_id == user_id).first()
    if not friend_request:
        return jsonify({"error": "Friendship not existing"}), 403
    friend_request.is_accepted = True
    db.session.commit()
    return jsonify({"status": "Friendship accepted"}), 200

@app.route('/cancel_friend_request/<int:user_id>', methods=['GET','POST'])
@login_required
def cancel_friend_request(user_id):
    friend_request = Friend.query.filter(
        ((Friend.user_id == current_user.id) & (Friend.friend_id == user_id)) |
        ((Friend.user_id == user_id) & (Friend.friend_id == current_user.id))
    ).first()
    if not friend_request:
        return jsonify({"error": "Request not existing"}), 403
    db.session.delete(friend_request)
    db.session.commit()
    return jsonify({"status": "Friendship canceled"}), 200
    
@app.route('/get_friend_status/<int:user_id>', methods=['GET'])
@login_required
def get_friend_status(user_id):
    global pending_requests
    pending_requests = len(Friend.query.filter(
                           Friend.friend_id == current_user.id,
                           Friend.is_accepted == False).all())
    friend_request = Friend.query.filter(
        ((Friend.user_id == current_user.id) & (Friend.friend_id == user_id)) |
        ((Friend.user_id == user_id) & (Friend.friend_id == current_user.id))
    ).first()
    if not friend_request:
        status = "none"
    elif friend_request.is_accepted:
        status = "accepted"
    elif friend_request.user_id == current_user.id:
        status = "pending_sent"
    else:
        status = "pending_received"
    return jsonify({"status": status,"message": friend_request.message if friend_request else None}), 200
    
@app.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
    accepted=[]
    pending=[]
    accepted_requests = Friend.query.filter(
        (Friend.user_id == current_user.id) | (Friend.friend_id == current_user.id),
         Friend.is_accepted==True).all()
    pending_requests = Friend.query.filter(
        (Friend.user_id == current_user.id) | (Friend.friend_id == current_user.id),
         Friend.is_accepted==False).all()
    for req in accepted_requests:
        if req.user_id == current_user.id:
            accepted.append(User.query.get_or_404(req.friend_id))
        else:
            accepted.append(User.query.get_or_404(req.user_id))
    for req in pending_requests:
        if req.user_id == current_user.id:
            pending.append(User.query.get_or_404(req.friend_id))
        else:
            pending.append(User.query.get_or_404(req.user_id))
    return render_template('friends.html', accepted=accepted, acc_len=len(accepted),
                                           pending=pending, pen_len=len(pending))