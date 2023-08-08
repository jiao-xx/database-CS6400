from wtforms.validators import InputRequired, Length, NumberRange, Optional
from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,
                     RadioField, EmailField, SelectField, SelectMultipleField)
from flaskext.mysql import MySQL
import app_constants


# https://www.digitalocean.com/community/tutorials/how-to-use-and-validate-web-forms-with-flask-wtf
class HouseholdForm(FlaskForm, MySQL):
    email = EmailField('email', validators=[InputRequired(), Length(min=5, max=100)])
    # postalCode = StringField('Postal Code', validators=[InputRequired(), Length(min=5, max=5), Regexp('/\b\d{5}\b/g', 
    # message="Must be a 5-digit numeric value.")])

    postalCode = StringField('Postal Code', validators=[InputRequired(), Length(min=5, max=5)])
    squareFootage = IntegerField('Square Footage', validators=[InputRequired(), NumberRange(min=0, max=100000)])
    heatingSetting = IntegerField('Heating Setting', validators=[Optional(), NumberRange(min=0, max=100)])
    coolingSetting = IntegerField('Cooling Setting', validators=[Optional(), NumberRange(min=0, max=100)])

    householdType = SelectField('householdType',  choices=app_constants.HOUSEHOLD_TYPES, validate_choice=True)

    checkNoHeat = BooleanField('No Heat')
    checkNoCooling = BooleanField('noCooling')
    publicUtilities = SelectMultipleField('publicUtilities',  choices=app_constants.PUBLIC_UTILITY_TYPES)
