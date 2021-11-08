from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 
import os

db = SQLAlchemy()

from .models import Bot, Contact


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = b'\xc71\xe5\xc3\xea\x16\r\x9b\xac\xe7\xc5\xe5\xea\xde8m'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_COOKIE_NAME'] = "telegram_session"

    @app.cli.command("create-db")
    def create_db():
        db.create_all()
        db.session.commit()
    

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return Bot.query.get(int(user_id))


    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app