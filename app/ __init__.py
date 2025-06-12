from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# criar instâncias
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    from .reports import reports_bp
    app.register_blueprint(reports_bp, url_prefix='/relatorios')

    return app