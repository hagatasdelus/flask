from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, PasswordField, SubmitField, HiddenField
)
from wtforms import ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from flaskr.models import User

class LoginForm(FlaskForm):
    email = StringField('メールアドレス: ', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード: ', validators=[DataRequired(), EqualTo('confirm_password', message='パスワードが一致しません')])
    confirm_password = PasswordField('パスワード再入力: ', validators=[DataRequired()]) #ここログイン用だしいらないかもと思った
    submit = SubmitField('ログイン')

class RegisterForm(FlaskForm):
    email = StringField('メールアドレス: ', validators=[DataRequired(), Email('メールアドレスが誤っています')])
    submit = SubmitField('登録')

    def validate_email(self, field):
        if User.select_user_by_email(field.data):
            raise ValidationError('メールアドレスはすでに登録されています')

class UserForm(FlaskForm):
    email = StringField('メール: ')
    username = StringField('利用者ID: ')
    submit = SubmitField('登録情報更新')

    # def validate(self):
