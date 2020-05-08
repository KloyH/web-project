from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired
from sqlalchemy_serializer import SerializerMixin


class OffersForm(FlaskForm, SerializerMixin):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField("Описание")
    price = IntegerField('Цена')
    submit = SubmitField('Применить')
