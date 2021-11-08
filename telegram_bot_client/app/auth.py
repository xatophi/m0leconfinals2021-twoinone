# auth.py

#from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, flash, make_response, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import Bot, Contact
from . import db
import re
import requests

auth = Blueprint('auth', __name__)

token_regex = re.compile(r"^\d+:[\w_-]{35}$")
def is_token_safe(token):
    if(token_regex.fullmatch(token)):
        return True
    return False


#def login_required(f):
#    @wraps(f)
#    def decorated_function(*args, **kwargs):
#        if 'bot_token' in request.cookies:
#            token = request.cookies['bot_token']
#            if is_token_safe(token):
#                g.bot_token = token
#                return f(*args, **kwargs)    
#        return redirect(url_for('auth.login'))
#        
#    return decorated_function

@auth.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    token = request.form.get('bot_token')

    latitude = None
    longitude = None
    try:
        latitude = float(request.form.get('latitude'))
        longitude = float(request.form.get('longitude'))
    except:
        pass

    print(latitude,longitude)

    bot = Bot.query.filter_by(token=token).first()

    if not bot:
        # signup bot

        if not is_token_safe(token):
            flash('Invalid token format')
            return redirect(url_for('auth.login')) 

        r = requests.get(f'https://api.telegram.org/bot{token}/getMe')
        
        if (r):
            res = r.json()['result']
            handle = res['id']
            if 'username' in res:
                handle = res['username']
            
            new_bot = Bot(token=token, handle=handle)
            db.session.add(new_bot)
            db.session.commit()


            if latitude and longitude:
                new_con = Contact(bot_id=new_bot.id, handle=handle, latitude=latitude, longitude=longitude)
            else:
                new_con = Contact(bot_id=new_bot.id, handle=handle)
            

            db.session.add(new_con)
            db.session.commit()

            login_user(new_bot)
            resp = make_response(redirect(url_for('main.index')))
            return resp
        else:
            flash('Invalid token')
            return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page

    else:
        #login bot

        if latitude and longitude:
            cont = Contact.query.filter(Contact.bot_id == bot.id, Contact.handle == bot.handle ).first_or_404()
            cont.latitude = latitude
            cont.longitude = longitude
            db.session.commit()
        
        login_user(bot)
        return redirect(url_for('main.index'))



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))