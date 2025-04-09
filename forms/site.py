from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired

class SiteForm(FlaskForm):
    name = StringField('Название (можете придумать сами)', validators=[DataRequired()])
    url = StringField('Адрес сайта', validators=[DataRequired()])
    icon = FileField('Иконка сайта')
    submit = SubmitField('Добавить')