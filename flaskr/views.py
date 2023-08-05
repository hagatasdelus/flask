from flask import (
    request, render_template, redirect, url_for, Blueprint,
    session, flash
)
from flask_login import login_user, login_required, logout_user, current_user
from flaskr.forms import (
    LoginForm, RegisterForm, PasswordResetForm, UserForm
)
from flaskr.models import (
    BookInfo, User, transaction
)

bp = Blueprint('app', __name__, url_prefix='')

book_list = [
        BookInfo(0, 'はらぺこあおむし', '絵本', 2000, '2023/2/14', 'image/harapekoaomushi.jpg'),
        BookInfo(1, 'ぐりとぐら', '絵本', 1500, '2023/2/9', 'image/guritogura.jpg'),
        BookInfo(2, '11匹のねこ', '絵本', 1400, '2023/2/20', 'image/11pikinoneko.jpeg'),
        BookInfo(3, 'やさしいC', '専門書', 2750, '2017/5/15', 'image/yasashiiC.jpg')
    ]


@bp.route('/')

def main():
    # session['url'] = 'app.home'
    return render_template('main.html')

@bp.route('/newtitle')
def load_new_title():
    return render_template('newtitle.html', book_list=book_list)

@bp.route('/book/<int:book_number>') #メンバー詳細ページ
def book_detail(book_number):
    for book in book_list:
        if book.number == book_number:
            return render_template('book_detail.html', book=book)
    return redirect(url_for('main')) #いなかったらmainにリダイレクトする

@bp.route('/terms') #利用規約
def terms_of_service():
    return render_template('terms.html')

@bp.errorhandler(404) #ページが間違うとmain
def redirect_main_page(error):
    return redirect(url_for('main'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.select_user_by_email(form.emal.data)
        if user and user.is_active and user.validate_password(form.password.data):
            login_user(user, remember=True)
            next = request.args.get('next')
            if not next:
                next = url_for('app.home')
            return redirect(next)
        elif not user:
            flash('User does not exist.')
        elif not user.is_active:
            flash('Invalid user. Please reset your password.')
        elif not user.validate_password(form.password.data):
            flash('Incorrect email address/password combination.')
    return render_template('', form=form)

@bp.route('/user_info', methods=['GET', 'POST'])
@login_required
def user_info():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        user = User.select_user_by_id(user_id)
        with transaction():
            user.username = form.username.data
    return render_template('user_info.html', form=form)


    
