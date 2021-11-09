from flask import Blueprint, render_template, redirect, url_for, request, flash, make_response, g
from flask_login import login_user, logout_user, login_required
import requests
from .models import Bot, Contact
from .utils import is_token_safe
from . import db


auth = Blueprint('auth', __name__)


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

    bot = Bot.query.filter_by(token=token).first()

    if not bot:
        # first time, signup bot

        if not is_token_safe(token):
            flash('Invalid token format','error')
            return redirect(url_for('auth.login')) 

        # contact telegram api to check if is a valid token
        r = requests.get(f'https://api.telegram.org/bot{token}/getMe')
        
        if (r):
            res = r.json()['result']

            # get the hadle or id
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
            flash('Invalid token','error')
            return redirect(url_for('auth.login'))

    else:
        # login bot

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