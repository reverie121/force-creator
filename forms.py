from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo, Optional

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
    password = PasswordField("Current Password", validators=[InputRequired()])
    new_password = PasswordField("New Password", validators=[Optional(), Length(min=8, max=128, message="Password must be at least 8 characters long")], render_kw={"autocomplete": "new-password"})
    confirm_password = PasswordField("Confirm New Password", validators=[Optional(), EqualTo('new_password', message="Passwords must match")], render_kw={"autocomplete": "new-password"})
    recaptcha_response = StringField('reCAPTCHA', validators=[DataRequired()])
    
class ResetPasswordRequestForm(FlaskForm):
    """ Form for requesting a password reset. """
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=75)])
    recaptcha_response = StringField('reCAPTCHA', validators=[DataRequired()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    """ Form for resetting password with token. """
    new_password = PasswordField("New Password", validators=[Length(min=8, max=128, message="Password must be at least 8 characters long"), DataRequired()])
    confirm_password = PasswordField("Confirm New Password", validators=[EqualTo('new_password', message="Passwords must match"), DataRequired()])
    submit = SubmitField('Reset Password')

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