from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField
from sqlalchemy_serializer import SerializerMixin


class RegisterForm(FlaskForm, SerializerMixin):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    address = StringField('Адрес')
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')