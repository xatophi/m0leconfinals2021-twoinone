from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from werkzeug.security import generate_password_hash
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    csrf = CSRFProtect(app)

    csp = {'script-src': '\'self\''}
    talisman = Talisman(app,session_cookie_secure=False,force_https=False,content_security_policy=csp,content_security_policy_nonce_in=['script-src'])

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = "Strict"

    @app.cli.command("create-db")
    def create_db():
        db.create_all()
        from .models import User, Note

        user = User(email=os.environ['EMAIL_NOTE'], password=generate_password_hash(os.environ['PASSWORD_NOTE'], method='sha256'))
        db.session.add(user)
        db.session.flush()
        db.session.refresh(user)

        note = Note(user_id=user.id, title='Flag', text='ptm{For3ign_c00kie5_t4st3_b4d}', ts_creation=datetime.now())
        db.session.add(note)
        
        db.session.commit()


    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'User needs to be logged in to view this page'
    login_manager.login_message_category = 'error'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app