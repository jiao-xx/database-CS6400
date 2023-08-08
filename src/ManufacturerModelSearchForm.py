from wtforms.validators import InputRequired
from flask_wtf import FlaskForm
from wtforms import (StringField)

class ManufacturerModelSearchForm(FlaskForm):
    searchTerm = StringField('Search String', validators=[InputRequired()])