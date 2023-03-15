from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, TextField
from wtforms.validators import InputRequired, Length, Email

#################### User Related Forms ####################

class AddUserForm(FlaskForm):
    """ Form for adding new user accounts. """
    username = StringField("User Name", validators=[InputRequired(), Length(max=30)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=75)])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=50)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=50)])


class LogInForm(FlaskForm):
    """ Form for logging in users. """
    username = StringField("User Name", validators=[InputRequired(), Length(max=30)])
    password = PasswordField("Password", validators=[InputRequired()])


class EditUserForm(FlaskForm):
    """ Form for editing a user account. """
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=75)])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=50)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=50)])
    password = PasswordField("Password", validators=[InputRequired()])


#################### Force Creator Forms ####################

class AddToList(FlaskForm):
    """ Form for use with Force Creator. """
    component_selector = SelectField('', choices=[('artillery', 'Artillery'), ('character', 'Characters'), ('ship', 'Ships'), ('unit', 'Units')])