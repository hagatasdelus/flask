from flask import (
    request, render_template, redirect, url_for, Blueprint,
    session, flash, abort
)
from flask_login import login_user, login_required, logout_user, current_user
from flaskr.forms import (
    LoginForm, RegisterForm, PasswordResetForm, UserForm, ForgotPasswordForm,
    BookForm
)
from flaskr.models import (
    BookInfo, User, transaction, PasswordResetToken
)

bp = Blueprint('app', __name__, url_prefix='')

# book_list = [
#         BookInfo(0, 'はらぺこあおむし', '絵本', 2000, '2023/2/14', 'image/harapekoaomushi.jpg'),
#         BookInfo(1, 'ぐりとぐら', '絵本', 1500, '2023/2/9', 'image/guritogura.jpg'),
#         BookInfo(2, '11匹のねこ', '絵本', 1400, '2023/2/20', 'image/11pikinoneko.jpeg'),
#         BookInfo(3, 'やさしいC', '専門書', 2750, '2017/5/15', 'image/yasashiiC.jpg')
#     ]


@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/newtitle')
def newtitle():
    book_list = None
    book_list = BookInfo.get_books()
    return render_template('newtitle.html', book_list=book_list)

@bp.route('/book/<int:id>')
def book_detail(id):
    book = BookInfo.get_book_by_id(id)
    if book:
        return render_template('book_detail.html', book=book)
    return redirect(url_for('app.home'))

@bp.route('/terms')
def terms_of_service():
    return render_template('terms.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('app.home'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.select_user_by_email(form.email.data)
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
    return render_template('login.html', form=form)

@bp.route('/register_users', methods=['GET', 'POST'])
def register_users():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            username = form.username.data,
            email = form.email.data
            )
        from setup import app
        with app.app_context():
            with transaction():
                user.create_new_user()
            token = ''
            with transaction():
                token = PasswordResetToken.publish_token(user)  #* 有効期限1日のランダムな文字列でできたtoken, そのuserのid, tokenの有効期限をDBに追加してtokenを返す
            #メールに飛ばす方が良い(メールが合っているかの確認ができるから)
            print(f'パスワード設定用URL: http://127.0.0.1:5000/password_reset/{token}')
            flash('パスワード設定用のURLをお送りしました。')
        return redirect(url_for('app.login')) #login関数に遷移
    return render_template('register_users.html', form=form) #GETの場合、register.htmlが表示される

@bp.route('/password_reset/<uuid:token>', methods=['GET', 'POST'])
def reset_password(token):
    form = PasswordResetForm(request.form)
    from setup import app
    with app.app_context():
        reset_user_id = PasswordResetToken.get_user_id_by_token(token)
        if not reset_user_id:
            abort(500)
        if request.method == 'POST' and form.validate():
            password = form.password.data
            user = User.select_user_by_id(reset_user_id)
            with transaction():
                user.save_new_password(password)
                PasswordResetToken.delete_token(token)
            flash('Updated your password')
            return redirect(url_for('app.login'))
    return render_template('password_reset.html', form=form)

@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if request.method == 'POST' and form.validate():
        email = form.email.data
        user = User.select_user_by_email(email)
        if user:
            with transaction():
                token = PasswordResetToken.publish_token(user)
            print(f'http:/127.0.0.1:5000:password_reset/{token}')
            flash('')
        else:
            flash('User does not exist')
    return render_template('forgot_password.html', form=form)

@bp.route('/user_info', methods=['GET', 'POST'])
@login_required
def user_info():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        from setup import app
        with app.app_context():
            user_id = current_user.get_id()
            user = User.select_user_by_id(user_id)
            with transaction():
                user.username = form.username.data
                user.email = form.email.data
            flash('Successfully updated user information')
    return render_template('user_info.html', form=form)

@bp.route('register_books', methods=['GET', 'POST'])
@login_required
def register_books():
    form = BookForm(request.form)
    if request.method == 'POST' and form.validate():
        book = BookInfo(
            title = form.title.data,
            price = form.price.data,
            genre = form.genre.data,
            arrival_day = form.arrival_day.data
        )
        from setup import app
        with app.app_context():
            with transaction():
                book.create_new_book()
            flash('Book registration has been completed')
        return redirect(url_for('app.newtitle'))
    return render_template('register_books.html', form=form)

@bp.app_errorhandler(404) #ページが間違うとmain
def redirect_main_page(e):
    return redirect(url_for('app.home'))

@bp.app_errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
