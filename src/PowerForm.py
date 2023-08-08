from wtforms.validators import InputRequired, Length, NumberRange, Optional
from flask_wtf import FlaskForm
from wtforms import (IntegerField, SelectField)
from flaskext.mysql import MySQL
import app_constants

class PowerForm(FlaskForm):

    avgKwh = IntegerField('Monthly kWh', validators=[InputRequired(), NumberRange(min=0, max=100000)])
    batteryStorageCapacity = IntegerField('Storage kWh', validators=[Optional(), NumberRange(min=0, max=100000)])
    powerGenerationType = SelectField('Type',  choices=app_constants.POWER_TYPES, validate_choice=True)