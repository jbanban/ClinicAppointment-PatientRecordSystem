from flask import Flask
from flask_login import LoginManager
from .models import db, User, Account
import os

login_manager = LoginManager()

def appointment():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'wowixczzzzz'

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fernandez_clinic.db'

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        user = Account.query.get(user_id)
        if user:
            return user
    
        # Fallback to Admin User
        return User.query.get(user_id)

    from .routes import abp
    app.register_blueprint(abp)

    with app.app_context():
        db.create_all() 
        print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"Current working directory: {os.getcwd()}")

    return app

