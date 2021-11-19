from flask import Blueprint, render_template, url_for, request, flash, make_response, redirect
from flask_login import login_required, current_user
import requests
from .models import Bot, Contact
from .utils import parse_telegram_style
from . import db


main = Blueprint('main', __name__)


@main.route('/')
@login_required
def index():
    return render_template('home.html')


@main.route('/messages')
@login_required
def messages():
    # contact the api to get the new messages
    r = requests.post(f'https://api.telegram.org/bot{current_user.token}/getUpdates', json={'offset':current_user.offset+1, 'allowed_updates':['messages']})
    if r:
        res = r.json()['result']

        msgs = []
        #parse and update contacts and locations
        for e in res:
            if 'message' in e:
                msg = e['message']

                # get the handle of the sender if exists (or use the id)
                handle = msg['from']['id']
                if 'username' in msg['from']:
                    handle = msg['from']['username']
                
                msgs.append({'handle':handle, 'text':parse_telegram_style(msg)})
                
                cont = Contact.query.filter(Contact.bot_id == current_user.id, Contact.handle == handle).one_or_none()
                
                if cont is None:
                    # if a new contact add to the contact list
                    cont = Contact(handle=handle,bot_id=current_user.id)
                    db.session.add(cont)
                    db.session.commit()
                
                if 'location' in msg:
                    # if a location was sent update the position of the contact
                    latitude = msg['location']['latitude']
                    longitude = msg['location']['longitude']
                    cont.latitude = latitude
                    cont.longitude = longitude
                    db.session.commit()

        if res:
            # update the message id to avoid reading the same messages the next time
            current_user.offset = res[-1]['update_id']
            db.session.commit()
        
        return render_template('messages.html',messages=msgs)

    else:
        flash('Something went wrong')
        return render_template('messages.html',messages=[])


@main.route('/contacts',methods=['GET'])
@login_required
def contacts():
    search = request.args.get('search')
    
    if search:
        cont = Contact.query.filter(Contact.bot_id == current_user.id, Contact.handle.startswith(search,autoescape=True)).all()
        return render_template('contacts.html',contacts=cont)
        
    cont = current_user.contacts 
    return render_template('contacts.html',contacts=cont)


@main.route('/locations',methods=['GET'])
@login_required
def locations():

    if request.method == 'GET':
        search = request.args.get('search')
        
        if search:
            cont = Contact.query.filter(Contact.bot_id == current_user.id ,Contact.handle.startswith(search,autoescape=True), Contact.longitude.is_not(None), Contact.latitude.is_not(None)).all()
            return render_template('locations.html',contacts=cont)
           
    cont = Contact.query.filter(Contact.bot_id == current_user.id ,Contact.longitude.is_not(None), Contact.latitude.is_not(None)).all()
    return render_template('locations.html',contacts=cont)
