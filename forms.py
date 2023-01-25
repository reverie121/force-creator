from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import InputRequired, Length


class ForceSelection(FlaskForm):
    """ Form for use with Force Creator. """

    force_name = StringField('Force Name', validators=[Length(max=50)])
    point_max = IntegerField('Point Total', default=150)
    select_nation = SelectField('Nationality', choices=[('dutch','Dutch'), ('english','English'), ('french','French'), ('native','Native'), ('spanish','Spanish'), ('unaligned','Unaligned')])
    select_faction = SelectField('Faction', choices=[])
    select_commander = SelectField('Commander', choices=[])

class AddToList(FlaskForm):
    """ Form for use with Force Creator. """

    component_selector = SelectField('', choices=[('artillery', 'Artillery'), ('characters', 'Characters'), ('ships', 'Ships'), ('units', 'Units'), ('misc', 'Terrain & Miscellaneous')])