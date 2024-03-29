from flask import (
    request, render_template, redirect, url_for, Blueprint,
    flash, abort, jsonify
)
from flask_login import login_user, login_required, logout_user, current_user
from flaskr.forms import (
    LoginForm, RegisterForm, PasswordResetForm, UserForm, ForgotPasswordForm,
    RegisterBookForm, ChangePasswordForm, DeleteBookForm, BookForm, BoardForm
)
from flaskr.models import (
    BookInfo, User, transaction, PasswordResetToken, Board
)
from flaskr.utils.post_formats import make_post_format, make_old_post_format
from datetime import datetime
import os

bp = Blueprint('app', __name__, url_prefix='')

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/newtitle')
def newtitle():
    book_list = None
    book_list = BookInfo.get_books()
    return render_template('newtitle.html', book_list=book_list)

@bp.route('newtitle/book/<int:id>')
def book_detail(id):
    book = BookInfo.select_book_by_id(id)
    if book:
        return render_template('book_detail.html', book=book)
    return redirect(url_for('app.home'))

@bp.route('/newtitle/book/<int:id>/info', methods=['GET', 'POST'])
@login_required
def book_info(id):
    form = BookForm(request.form)
    from setup import app
    with app.app_context():
        book = BookInfo.select_book_by_id(id)
        if book.user_id != int(current_user.get_id()):
            flash('You do not have permission to update.')
            return redirect(url_for('app.book_detail', id=id))
        if request.method == 'POST' and form.validate():
            if BookInfo.select_book_by_title(form.title.data):
                flash('The book with that title is already registered.')
                return redirect(url_for('app.newtitle'))
            with transaction():
                book.title = form.title.data
                book.price = form.price.data
                book.genre = form.genre.data
                book.arrival_day = form.arrival_day.data
                file = request.files[form.picture_path.name].read()
                if file:
                    file_name = str(id) + '_' + str(int(datetime.now().timestamp())) + '.jpg'
                    picture_path = 'flaskr/static/book_image/' + file_name
                    open(picture_path, 'wb').write(file)
                    book.picture_path = 'book_image/' + file_name
            flash('Book registration information has been successfully updated.')
        return render_template('book_info.html', form=form, book=book)

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
            flash('We have sent you the URL to set the password.')
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

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        from setup import app
        with app.app_context():
            user = User.select_user_by_id(current_user.get_id())
            password = form.password.data
            with transaction():
                user.save_new_password(password)
            flash('Password updated successfully.')
            return redirect(url_for('app.user_info'))
    return render_template('change_password.html', form=form)


@bp.route('register_books', methods=['GET', 'POST'])
@login_required
def register_books():
    form = RegisterBookForm(request.form)
    if request.method == 'POST' and form.validate():
        if BookInfo.select_book_by_title(form.title.data):
            flash('The book with that title is already registered.')
            return redirect(url_for('app.newtitle'))
        book = BookInfo(
            title = form.title.data,
            price = form.price.data,
            genre = form.genre.data,
            arrival_day = form.arrival_day.data,
            user_id = current_user.get_id()
        )
        from setup import app
        with app.app_context():
            with transaction():
                book.create_new_book()
            flash('Book registration has been completed')
        return redirect(url_for('app.newtitle'))
    return render_template('register_books.html', form=form)

@bp.route('newtitle/confirm_delete/<id>', methods=['GET', 'POST'])
@login_required
def confirm_delete(id):
    form = DeleteBookForm(request.form)
    book = BookInfo.select_book_by_id(id)
    if not book:
        flash('The book is not registered.')
        return redirect(url_for('app.newtitle'))
    if request.method == 'POST' and form.validate():
        if book.user_id == int(current_user.get_id()):
            with transaction():
                book.delete_book(id)
                Board.delete_posts_by_book_id(id)
                if book.picture_path:
                    app_root = os.path.dirname(os.path.abspath(__file__))
                    os.remove(os.path.join(app_root, 'static', book.picture_path))
            flash(f'Removed "{book.title}".')
            return redirect(url_for('app.newtitle'))
        flash('You do not have permission to delete.')
        return redirect(url_for('app.newtitle'))
    form.id.data = id
    return render_template('confirm_delete.html', form=form, book=book)
    
@bp.route('/newtitle/book/<int:id>/board', methods=['GET', 'POST'])
@login_required
def board(id):
    form = BoardForm(request.form)
    book = BookInfo.select_book_by_id(id)
    if not book:
        flash('The book is not currently registered.')
        return redirect(url_for('app.newtitle'))
    posts = Board.get_book_posts(id)
    from setup import app
    with app.app_context():
        read_post_ids = [post.id for post in posts if (not post.read) and (post.from_user_id != int(current_user.get_id()))]
        if read_post_ids:
            with transaction():
                Board.update_read_by_ids(read_post_ids)
        if request.method == 'POST' and form.validate():
            if form.post.data == '':
                return redirect(url_for('app.board', id=id))
            new_post = Board(current_user.get_id(), id, form.post.data)
            with transaction():
                new_post.create_post()
            return redirect(url_for('app.board', id=id))
    return render_template('board.html', form=form, posts=posts, book=book)

@bp.route('/post_ajax', methods=['GET'])
@login_required
def post_ajax():
    book_id = request.args.get('book_id', -1, type=int)
    not_read_posts = Board.select_not_read_posts(book_id)
    not_read_posts_ids = [post.id for post in not_read_posts]
    from setup import app
    with app.app_context():
        if not_read_posts_ids:
            with transaction():
                Board.update_read_by_ids(not_read_posts_ids)
    return jsonify(data=make_post_format(not_read_posts))

@bp.route('/load_old_posts', methods=['GET'])
@login_required
def load_old_posts():
    book_id = request.args.get('book_id', -1, type=int)
    offset_value = request.args.get('offset_value', -1, type=int)
    if book_id == -1 or offset_value == -1:
        return
    posts = Board.get_book_posts(book_id, offset_value * 100)
    return jsonify(data=make_old_post_format(posts))

@bp.app_errorhandler(404)
def redirect_main_page(e):
    return redirect(url_for('app.home'))

@bp.app_errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
