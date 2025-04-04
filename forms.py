from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Length, Email, DataRequired

#################### User Related Forms ####################

class AddUserForm(FlaskForm):
    """ Form for adding new user accounts. """
    username = StringField("User Name", validators=[InputRequired(), Length(max=30)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=75)])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=50)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=50)])
    recaptcha_response = StringField('reCAPTCHA', validators=[DataRequired()])

class LogInForm(FlaskForm):
    """ Form for logging in users. """
    username = StringField("User Name", validators=[InputRequired(), Length(max=30)])
    password = PasswordField("Password", validators=[InputRequired()])
    recaptcha_response = StringField('reCAPTCHA', validators=[DataRequired()])

class EditUserForm(FlaskForm):
    """ Form for editing a user account. """
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=75)])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=50)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=50)])
    password = PasswordField("Password", validators=[InputRequired()])
    recaptcha_response = StringField('reCAPTCHA', validators=[DataRequired()])

class DeleteUserForm(FlaskForm):
    recaptcha_response = StringField('reCAPTCHA', validators=[DataRequired()])

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    recaptcha_response = StringField('reCAPTCHA', validators=[DataRequired()])
    submit = SubmitField('Send Message')
#################### Force Creator Forms ####################

class AddToList(FlaskForm):
    """ Form for use with Force Creator. """
    component_selector = SelectField('', choices=[('artillery', 'Artillery'), ('character', 'Characters'), ('ship', 'Ships'), ('unit', 'Units')])