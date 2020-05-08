from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, IntegerField, StringField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField
from sqlalchemy_serializer import SerializerMixin


class MoneyForm(FlaskForm, SerializerMixin):
    email = EmailField('Ваша почта', validators=[DataRequired()])
    password = PasswordField('Ваш пароль', validators=[DataRequired()])
    summa = IntegerField('Сумма')
    check = BooleanField('Точно?')
    submit = SubmitField('отправить')