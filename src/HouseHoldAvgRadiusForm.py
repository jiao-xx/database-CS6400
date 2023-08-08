from wtforms.validators import InputRequired, Length, NumberRange, Optional
from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField)
from flaskext.mysql import MySQL
import app_constants

class HouseHoldAvgRadiusForm(FlaskForm):

    postalCode = StringField('Postal Code', validators=[InputRequired(), Length(min=5, max=5)])
    searchRadius = SelectField('Search Radius',  choices=app_constants.SEARCH_RADIUS, validate_choice=True)