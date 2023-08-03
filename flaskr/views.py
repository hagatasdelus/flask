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

@bp.route('/')
def home():
    session['url'] = 'app.home'
    return render_template('')

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


    
