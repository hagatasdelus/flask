from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, PasswordField, SubmitField, HiddenField, IntegerField, DateField, SelectField
)
from wtforms import ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange
from flask_login import current_user
# from flask import flash
from flaskr.models import User

class LoginForm(FlaskForm):
    email = StringField('メールアドレス: ', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード: ', validators=[DataRequired(), EqualTo('confirm_password', message='パスワードが一致しません')])
    confirm_password = PasswordField('パスワード再入力: ', validators=[DataRequired()]) #ここログイン用だしいらないかもと思った
    submit = SubmitField('ログイン')

class RegisterForm(FlaskForm):
    username = StringField('ユーザー名: ', validators=[DataRequired()])
    email = StringField('メールアドレス: ', validators=[DataRequired(), Email('メールアドレスが誤っています')])
    submit = SubmitField('登録')

    def validate_email(self, field):
        if User.select_user_by_email(field.data):
            raise ValidationError('メールアドレスはすでに登録されています')

class PasswordResetForm(FlaskForm):
    password = PasswordField('パスワード: ',validators=[DataRequired(), EqualTo('confirm_password', message='Password does not match.')])
    confirm_password = PasswordField('パスワード確認: ', validators=[DataRequired()])
    submit = SubmitField('パスワード更新')

    def validate_email(self, field):
        if len(field.data) < 8:
            raise ValidationError('Password must be at least 8 characters.')


class ForgotPasswordForm(FlaskForm):
    email = StringField('メール: ', validators=[DataRequired(), Email()])
    submit = SubmitField('パスワードを再設定')

    def validate_email(self, field):
        if not User.select_user_by_email(field.data): #DBからそのEmailを取ってこれなかったら
            raise ValidationError('そのメールアドレスは存在しません')
        
class UserForm(FlaskForm):
    email = StringField('メール: ', validators=[DataRequired(), Email('メールアドレスが誤っています')])
    username = StringField('ユーザー名: ', validators=[DataRequired()])
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

class BookForm(FlaskForm):
    title = StringField('タイトル: ', validators=[DataRequired()])
    price = IntegerField('値段: ', validators=[NumberRange(0, 10000, 'Incorrect value')])
    genre = SelectField('ジャンル: ', choices=[('文学・評論', '文学・評論'), ('ノンフィクション', 'ノンフィクション'), ('ビジネス・経済', 'ビジネス・経済'),
           ('歴史・地理', '歴史・地理'), ('政治・社会', '政治・社会'), ('芸能・エンターテインメント', '芸能・エンターテインメント'),
           ('アート・建築・デザイン', 'アート・建築・デザイン'), ('人文・思想・宗教', '人文・思想・宗教'), ('暮らし・健康・料理', '暮らし・健康・料理'),
           ('サイエンス・テクノロジー', 'サイエンス・テクノロジー'), ('趣味・実用', '趣味・実用'), ('教育・自己啓発', '教育・自己啓発'),
           ('スポーツ・アウトドア', 'スポーツ・アウトドア'), ('事典・年鑑・本・ことば', '事典・年鑑・本・ことば'), ('音楽', '音楽'),
           ('旅行・紀行', '旅行・紀行'), ('絵本・児童書', '絵本・児童書'), ('コミックス', 'コミックス'), ('その他', 'その他')])
    arrival_day = DateField('到着日: ', validators=[DataRequired('Please enter data')], format='%Y-%m-%d', render_kw={"placeholder": "yyyy/mm/dd"})
    user_id = HiddenField()
    submit = SubmitField('登録')

class ChangePasswordForm(FlaskForm):
    password = PasswordField('パスワード: ', validators=[DataRequired(), EqualTo('confirm_password', message='Password does not match.')])
    confirm_password = PasswordField('パスワード確認: ', validators=[DataRequired()])
    submit = SubmitField('パスワード更新')

    def validate_email(self, field):
        if len(field.data) < 8:
            raise ValidationError('Password must be at least 8 characters.')

class DeleteBookForm(FlaskForm):
    id = HiddenField()
    submit = SubmitField('削除')
