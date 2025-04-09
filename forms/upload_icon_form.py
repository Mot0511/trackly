from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired

class UploadIconForm(FlaskForm):
    id = StringField()
    icon_file = FileField(validators=[DataRequired()])