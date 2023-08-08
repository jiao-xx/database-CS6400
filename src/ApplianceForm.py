from wtforms.validators import InputRequired, Length, NumberRange, Regexp, Optional, ValidationError
from flask_wtf import FlaskForm
from wtforms import (StringField, IntegerField, BooleanField,
                     DecimalField, EmailField, SelectField, SelectMultipleField)
from flaskext.mysql import MySQL
import app_constants

# https://www.digitalocean.com/community/tutorials/how-to-use-and-validate-web-forms-with-flask-wtf
# https://wtforms.readthedocs.io/en/2.3.x/validators/
# class ApplianceForm(FlaskForm):

#     applianceType = SelectField('Appliance Type',  choices=app_constants.APPLIANCE_TYPES, validate_choice=True) 
#     manufacturer = SelectField('Manufacturer',  choices=app_constants.APPLIANCE_TYPES, validate_choice=False)
#     btus = IntegerField('BTUs', validators=[InputRequired(), NumberRange(min=0, max=100000)])
#     modelName = StringField('Model Name', validators=[InputRequired(), Length(min=1, max=50)])

class AirhandlerForm(FlaskForm):

    ahApplianceType = SelectField('Appliance Type',  choices=app_constants.APPLIANCE_TYPES, default='Air handler',validate_choice=True) 
    ahManufacturer = SelectField('Manufacturer',  choices=app_constants.APPLIANCE_TYPES, validate_choice=False)
    ahBtus = IntegerField('BTUs', validators=[InputRequired(), NumberRange(min=0, max=100000)])
    ahModelName = StringField('Model Name', validators=[InputRequired(), Length(min=1, max=50)])

    fanRpms = IntegerField('fanRpms', validators=[InputRequired(), NumberRange(min=0, max=100000)])
    eer = DecimalField('EER', validators=[Optional(), NumberRange(min=0, max=100000)])
    seer = DecimalField('SEER', validators=[Optional(), NumberRange(min=0, max=100000)])
    hspf = DecimalField('HSPF', validators=[Optional(), NumberRange(min=0, max=100000)])
    heaterEnergySource = SelectField('Heater Energy Source',  choices=app_constants.HEATER_ENERGY_SOURCES, validate_choice=True)
    heatingCoolingTypes = SelectMultipleField('Heating/Cooling Types',  choices=app_constants.HEATING_COOLING_TYPES) 

class WaterHeaterForm(FlaskForm):

    whApplianceType = SelectField('Appliance Type',  choices=app_constants.APPLIANCE_TYPES, default='Water heater', validate_choice=True) 
    whManufacturer = SelectField('Manufacturer',  choices=app_constants.APPLIANCE_TYPES, validate_choice=False)
    whBtus = IntegerField('BTUs', validators=[InputRequired(), NumberRange(min=0, max=100000)])
    whModelName = StringField('Model Name', validators=[InputRequired(), Length(min=1, max=50)])

    waterHeaterEnergySource = SelectField('Water Heater Energy Source',  choices=app_constants.WATER_HEATER_ENERGY_SOURCES, validate_choice=True)
    tankSize = DecimalField('tankSize', validators=[InputRequired(), NumberRange(min=0, max=100000)])
    #btuRating = IntegerField('BTU Rating', validators=[InputRequired(), NumberRange(min=0, max=100000)])
    currentTempSetting = IntegerField('Temperature', validators=[InputRequired(), NumberRange(min=0, max=200)])

