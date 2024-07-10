from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, BooleanField, FormField, DateField, SelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Optional, ValidationError, Length, Email, EqualTo
from datetime import date
import os

countries_file_path = os.path.dirname(os.path.realpath(__file__))+'./static/json/countries.json'
cities_file_path = os.path.dirname(os.path.realpath(__file__))+'./static/json/cities.json'

with open(countries_file_path, 'r', encoding='utf-8') as f:
        countries_list = eval(f.read())
with open(cities_file_path, 'r', encoding='utf-8') as f:
        cities_dict = eval(f.read())

class RegistrationForm(FlaskForm):
    username = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    remember = BooleanField('Recuerdame')

class SearchForm(FlaskForm):
    keyword = StringField('Keyword:', validators=[Length(max=20)])
    min_age = StringField('Min Age:', validators=[Length(max=2)])
    max_age = StringField('Max Age:', validators=[Length(max=2)])
    country = SelectField('Country',choices=['']+countries_list, validators=[Optional()])
    sorted = SelectField('Sorted By',choices=['Alphabetical','Last Login','Tag Match'], validators=[DataRequired()], default='Last Login')
    submit = SubmitField('Search')
    
class UpdateProfileForm(FlaskForm):
    username = StringField('Full Name:', validators=[DataRequired(), Length(max=100)])
    country = StringField('Country:', validators=[DataRequired(), Length(max=30)])
    city = StringField('City:', validators=[DataRequired(), Length(max=30)])
    description = TextAreaField('Description:', validators=[Length(max=5000)])
    tag = StringField('Add Tag:', validators=[Length(max=300)])
    birthdate = DateField('Birthdate:', format='%Y-%m-%d', validators=[DataRequired()])
    file = FileField('Update Profile Picture:', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    addtag = SubmitField('Add Tag')
    tags = []
    gender = SelectField('Gender',choices=['Male ♂','Female ♀','Muxe ⚧','Other 🌈'],
    validators=[DataRequired()])
    submit = SubmitField('Update')
    delete_account = SubmitField('Delete User')
    
def validate_start_date(form, field):
    start_date = form.start_date.data
    if start_date < date.today():
        raise ValidationError('Start date cannot be in the past.')

def validate_end_date(form, field):
    start_date = form.start_date.data
    end_date = form.end_date.data
    if start_date > end_date:
        raise ValidationError('End date must be after start date.')

def validate_country(form, field):
    country = form.country.data
    if country not in countries_list:
        raise ValidationError('Not a valid country.')
        
def validate_city(form, field):
    country = form.country.data
    if country not in countries_list:
        raise ValidationError('Not a valid country.')
    city = form.city.data
    if city not in cities_dict[country]:
        print(city,cities_dict[country])
        raise ValidationError('Not a valid city.')
 
class CreateTripForm(FlaskForm):
    country = StringField('Country', validators=[DataRequired(), Length(max=100), validate_country])
    city = StringField('City', validators=[DataRequired(), Length(max=100), validate_city])
    start_date = DateField('Start Date', validators=[DataRequired(), validate_start_date])
    end_date = DateField('End Date', validators=[DataRequired(), validate_end_date])
    comments = TextAreaField('Tell us about your trip:', validators=[Length(max=1000)])
    submit = SubmitField('Create Trip')
    edit = SubmitField('Edit Trip')