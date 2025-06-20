from functools import wraps
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from werkzeug.security import check_password_hash

from .models import db
from .repositories.user_repository import UserRepository

user_repository = UserRepository(db)
bp = Blueprint('auth', __name__, url_prefix='/auth')

def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)
    login_manager.init_app(app)

def load_user(user_id):
    return user_repository.get_user_by_id(user_id)

def check_rights(action):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Для выполнения данного действия необходимо пройти процедуру аутентификации', 'warning')
                return redirect(url_for('auth.login', next=request.url))

            if action == 'create_animal' and not current_user.is_admin:
                flash('У вас недостаточно прав для выполнения данного действия', 'danger')
                return redirect(url_for('main.index'))
            elif action == 'edit_animal' and not (current_user.is_admin or current_user.is_moderator):
                flash('У вас недостаточно прав для выполнения данного действия', 'danger')
                return redirect(url_for('main.index'))
            elif action == 'delete_animal' and not current_user.is_admin:
                flash('У вас недостаточно прав для выполнения данного действия', 'danger')
                return redirect(url_for('main.index'))
            elif action == 'process_adoption' and not (current_user.is_admin or current_user.is_moderator):
                flash('У вас недостаточно прав для выполнения данного действия', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        if login and password:
            user = user_repository.get_user_by_login(login)
            if user and user.check_password(password):
                login_user(user, remember=remember)
                flash('Вы успешно аутентифицированы', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main.index'))
        
        flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))