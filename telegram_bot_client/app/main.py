# main.py

from flask import Blueprint, render_template, url_for, request, flash, make_response, redirect, escape
from flask_login import login_required, current_user
from .models import Bot, Contact
from . import db
from .auth import login_required
import requests

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template('home.html')


def parse_telegram_style(msg):
    if 'text' not in msg:
        return ''
    elif 'entities' not in msg:
        return str(escape(msg['text']))
    else:
        entities = msg['entities']
        print(entities)
        text = msg['text']
        res = ''
        i = 0
        for e in entities:
            off = e['offset']
            length = e['length']
            t = e['type']

            res += str(escape(text[i:off]))
            
            
            entity_text = str(escape(text[off:off+length]))
            i = off+length

            if t == 'code':
                res += f'<code>{entity_text}</code>'
            elif t == 'bold':
                res += f'<b>{entity_text}</b>'
            elif t == 'text_link':
                if 'url' not in e:
                    res += f'<a href={entity_text}>{entity_text}</a>'
                else:
                    res += f'<a href={e["url"]}>{entity_text}</a>'
            elif t == 'pre':
                
                if entity_text[0] == '\n' or '\n' not in entity_text:
                    res += f'<pre class=prettyprint>{entity_text}</pre>'
                else:
                    i = entity_text.find('\n')
                    language = entity_text[:i]
                    entity_text = entity_text[i+1:]
                    res += f'<pre class=prettyprint><code class=language-{language}>{entity_text}</code></pre>'

            elif t == 'underline':
                res += f'<u>{entity_text}</u>'
            elif t == 'italic':
                res += f'<i>{entity_text}</i>'
            elif t == 'strikethrough':
                res += f'<s>{entity_text}</s>'
            else:
                res += entity_text

        return res
            

@main.route('/messages')
@login_required
def messages():
    r = requests.post(f'https://api.telegram.org/bot{current_user.token}/getUpdates', json={'offset':current_user.offset+1, 'allowed_updates':['messages']})
    if r:
        res = r.json()['result']

        msgs = []
        #parse and update contacts and locations
        for e in res:
            if 'message' in e:
                msg = e['message']

                handle = msg['from']['id']
                if 'username' in msg['from']:
                    handle = msg['from']['username']

                #parse_telegram_style(msg)
                #msgs.append({'handle':handle, 'text':str(msg)})
                msgs.append({'handle':handle, 'text':parse_telegram_style(msg)})
                
                cont = Contact.query.filter(Contact.bot_id == current_user.id, Contact.handle == handle).one_or_none()
                
                if cont is None:
                    cont = Contact(handle=handle,bot_id=current_user.id)
                    db.session.add(cont)
                    db.session.commit()

                
                if 'location' in msg:
                    latitude = msg['location']['latitude']
                    longitude = msg['location']['longitude']
                    cont.latitude = latitude
                    cont.longitude = longitude
                    db.session.commit()

        print(msgs)            

        if res:
            current_user.offset = res[-1]['update_id']
        
        db.session.commit()
        return render_template('messages.html',messages=msgs)

    else:
        print(r,r.text)
        return 'error', 400

@main.route('/contacts',methods=['GET'])
@login_required
def contacts():
    #if request.method == 'POST':
    #    handle = request.form.get('handle')
    #    if handle:
    #        new_cont = Contact(bot_id=current_user.id, handle=handle)
    #        db.session.add(new_cont)
    #        db.session.commit()
    
    if request.method == 'GET':
        search = request.args.get('search')
        
        if search:
            cont = Contact.query.filter(Contact.bot_id == current_user.id, Contact.handle.startswith(search)).all()
            return render_template('contacts.html',contacts=cont)
            
    cont = current_user.contacts 
    return render_template('contacts.html',contacts=cont)



@main.route('/locations',methods=['GET'])
@login_required
def locations():

    if request.method == 'GET':
        search = request.args.get('search')
        
        if search:
            cont = Contact.query.filter(Contact.bot_id == current_user.id ,Contact.handle.startswith(search), Contact.longitude.is_not(None), Contact.latitude.is_not(None)).all()
            return render_template('locations.html',contacts=cont)

           
    cont = Contact.query.filter(Contact.bot_id == current_user.id ,Contact.longitude.is_not(None), Contact.latitude.is_not(None)).all()
    return render_template('locations.html',contacts=cont)




@main.route('/404')
@login_required
def error():
    return 'not found', 404
