from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, TextField
from wtforms.validators import InputRequired, Length, Email

#################### User Related Forms ####################

class AddUserForm(FlaskForm):
    """ Form for adding new user accounts. """
    username = StringField("User Name", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=50)])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=30)])


class LogInForm(FlaskForm):
    """ Form for logging in users. """
    username = StringField("User Name", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])


class EditUserForm(FlaskForm):
    """ Form for editing a user account. """
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=50)])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=30)])
    password = PasswordField("Password", validators=[InputRequired()])


#################### Force Creator Forms ####################

class ForceSelection(FlaskForm):
    """ Form for use with Force Creator. """
    force_name = StringField('Force Name', validators=[Length(max=50)])
    point_max = IntegerField('Point Total', default=150)
    select_nation = SelectField('Nation', choices=[], render_kw={'readonly': True})
    select_faction = SelectField('Faction', choices=[])
    select_commander = SelectField('Commander', choices=[])

class AddToList(FlaskForm):
    """ Form for use with Force Creator. """
    component_selector = SelectField('', choices=[('artillery', 'Artillery'), ('character', 'Characters'), ('ship', 'Ships'), ('unit', 'Units'), ('misc', 'Terrain & Miscellaneous')])