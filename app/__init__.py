import bleach
from flask import Flask
from flask_migrate import Migrate
from markdown import markdown
from sqlalchemy.exc import SQLAlchemyError

from .models import db
from .auth import bp as auth_bp, init_login_manager
from .animals import bp as animals_bp
from .routes import bp as main_bp

def handle_sqlalchemy_error(err):
    error_msg = ('Возникла ошибка при подключении к базе данных. '
                 'Повторите попытку позже.')
    return f'{error_msg} (Подробнее: {err})', 500

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile("config.py")
    
    if test_config:
        app.config.from_mapping(test_config)

    db.init_app(app)
    migrate = Migrate(app, db)

    init_login_manager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(animals_bp)
    app.register_blueprint(main_bp)
    app.errorhandler(SQLAlchemyError)(handle_sqlalchemy_error)

    @app.template_filter('markdown')
    def markdown_filter(text):
        allowed_tags = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'b', 'i', 'strong', 'em', 'tt',
            'p', 'br', 'span', 'div', 'blockquote', 'code', 'hr',
            'ul', 'ol', 'li', 'dd', 'dt', 'dl',
            'img', 'a', 'sub', 'sup'
        ]
        allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title']
        }
        
        html = markdown(text)
        cleaned = bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes)
        return cleaned

    return app

app = create_app()