from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, PasswordField, SubmitField, HiddenField
)
from wtforms.validators import DataRequired, Email, EqualTo

class LoginForm(FlaskForm):
    email = StringField('メールアドレス: ', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード: ', validators=[DataRequired(), EqualTo('confirm_password', message='パスワードが一致しません')])
    confirm_password = PasswordField('パスワード再入力: ', validators=[DataRequired()]) #ここログイン用だしいらないかもと思った
    submit = SubmitField('ログイン')

class RegisterForm(FlaskForm):
    email = StringField('メールアドレス: ', validators=[DataRequired(), Email('メールアドレスが誤っています')])
    submit = SubmitField('登録')
