from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def appointment():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'wowixczzzzz'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fernandez_clinic.db'

    db.init_app(app)
    login_manager.init_app(app)

    from . import models  

    with app.app_context():
        db.create_all()   # create tables if not exists

    # Register routes (or blueprints)
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app

