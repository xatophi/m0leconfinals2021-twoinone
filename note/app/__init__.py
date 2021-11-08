from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from werkzeug.security import generate_password_hash
import os
import requests

db = SQLAlchemy()

def visit_url(url):
    if url and url.startswith('http'):
        r = requests.post(os.environ['BOT_URL'],json={'url':url})
        if r:
            return True
        else:
            return False

def create_app():
    app = Flask(__name__)
    csrf = CSRFProtect(app)

    csp = {'script-src': '\'self\''}
    talisman = Talisman(app,session_cookie_secure=False,force_https=False,content_security_policy=csp,content_security_policy_nonce_in=['script-src'])

    app.config['SECRET_KEY'] = b'\xcae\xb4\x05va\xb2^\xe5!\xfe3\x99\xaf\xe2\x14'
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

        note = Note(user_id=user.id, title='Flag', text='ptm{test_flag}', ts_creation=datetime.now())
        db.session.add(note)
        
        db.session.commit()


    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)




    return app