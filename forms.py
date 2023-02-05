from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import InputRequired, Length


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