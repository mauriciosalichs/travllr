from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, BooleanField, FieldList, FormField, DateField
from wtforms.validators import DataRequired, ValidationError, Length, Email, EqualTo
from datetime import date

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
    remember = BooleanField('Remember Me')

class UpdateProfileForm(FlaskForm):
    username = StringField('Full Name:', validators=[Length(max=100)])
    country = StringField('Country:', validators=[Length(max=30)])
    city = StringField('City:', validators=[Length(max=30)])
    description = TextAreaField('Description:', validators=[Length(max=5000)])
    tag = StringField('Add Tag:', validators=[Length(max=300)])
    birthdate = DateField('Birthdate:', format='%Y-%m-%d')
    addtag = SubmitField('Add Tag')
    tags = []
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
        
class CreateTripForm(FlaskForm):
    country = StringField('Country', validators=[DataRequired(), Length(max=100)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    start_date = DateField('Start Date', validators=[DataRequired(), validate_start_date])
    end_date = DateField('End Date', validators=[DataRequired(), validate_end_date])
    submit = SubmitField('Create Trip')