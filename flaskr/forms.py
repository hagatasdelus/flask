from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, PasswordField, SubmitField, HiddenField
)
from wtforms import ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from flask_login import current_user
# from flask import flash
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
    email = StringField('メール: ', validators=[DataRequired(), Email('メールアドレスが誤っています')])
    username = StringField('利用者ID: ', validators=[DataRequired()])
    submit = SubmitField('登録情報更新')

    def validate(self):
        if not super(FlaskForm, self).validate():
            return False
        user = User.select_user_by_email(self.email.data)
        if user:
            if user.id != int(current_user.get_id()):
                #なんか処理
                return False
        return True

class PasswordResetForm(FlaskForm):
    password = PasswordField('パスワード: ',validators=[DataRequired(), EqualTo('confirm_password', message='パスワード不一致')])
    confirm_password = PasswordField('パスワード確認: ', validators=[DataRequired()])
    submit = SubmitField('パスワード更新')

