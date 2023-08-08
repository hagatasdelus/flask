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
    password = PasswordField('パスワード: ',validators=[DataRequired(), EqualTo('confirm_password', message='パスワード不一致')])
    confirm_password = PasswordField('パスワード確認: ', validators=[DataRequired()])
    submit = SubmitField('パスワード更新')


class ForgotPasswordForm(FlaskForm):
    email = StringField('メール: ', validators=[DataRequired(), Email()])
    submit = SubmitField('パスワードを再設定')

    def validate_email(self, field):
        if not User.select_user_by_email(field.data): #DBからそのEmailを取ってこれなかったら
            raise ValidationError('そのメールアドレスは存在しません')
        
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

class BookForm(FlaskForm):
    title = StringField('タイトル: ', validators=[DataRequired()])
    price = IntegerField('値段: ', validators=[NumberRange(0, 10000, 'Incorrect value')])
    genre = SelectField('ジャンル: ', choices=[('lit-crit', '文学・評論'), ('nonfiction', 'ノンフィクション'), ('biz-econ', 'ビジネス・経済'),
                                            ('hist-geogr', '歴史・地理'), ('pol-soc', '政治・社会'), ('entertainment', '芸能・エンターエンターテインメント'),
                                            ('art-arch-des','アート・建築・デザイン'), ('hum-phil-rel', '人文・思想・宗教'), ('liv-hlt-cook', '暮らし・健康・料理'),
                                            ('sci-tech', 'サイエンス・テクノロジー'), ('hob-prac_use', '趣味・実用'), ('educ-self_dev', '教育・自己啓発'),
                                            ('sports-outdoor', 'スポーツ・アウトドア'), ('enc-alm-books-words', '事典・年鑑・本・ことば'), ('music', '音楽'),
                                            ('travel', '旅行・紀行'), ('pic-child-book', '絵本・児童書'), ('comics', 'コミックス'), ('others', 'その他')])
    arrival_day = DateField('到着日: ', validators=[DataRequired('Please enter data')], format='%Y-%m-%d', render_kw={"placeholder": "yyyy/mm/dd"})
