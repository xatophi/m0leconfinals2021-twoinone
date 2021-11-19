from flask import Blueprint, render_template, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.utils import redirect
from datetime import datetime
import requests
import os
from .models import Note
from . import db


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('home.html')


@main.route('/note', methods=['GET'])
@login_required
def show_notes():
    note_id = request.args.get('id')

    if not note_id:
        # show all notes
        notes = Note.query.filter(Note.user_id == current_user.id).all()
        return render_template('notes.html', notes=notes)
    else:
        # show the selected note (only if it belongs to the user)
        note = Note.query.filter(Note.id == note_id, Note.user_id == current_user.id).first()
        if note:
            return render_template('note.html',note=note)
        else:
            flash('Note not found','error')
            return redirect(url_for('main.show_notes'))


@main.route('/add_note', methods=['GET','POST'])
@login_required
def add_note():
    if request.method == 'POST':
        title = request.form.get('title')
        text = request.form.get('text')

        if title and text:
            note = Note(user_id=current_user.id, title=title, text=text, ts_creation=datetime.now())
            db.session.add(note)
            db.session.commit()
            flash('Note added','success')
            return redirect(url_for('main.show_notes'))
        else:
            flash('Invalid data','error')
            
    return render_template('add_note.html')


@main.route('/abuse', methods=['GET','POST'])
@login_required
def report_abuse():
    if request.method == 'POST':
        url = request.form.get('url')
        team_token = request.form.get('token')

        if team_token and url and url.startswith('http'):
            try:
                # send the request to the bot to visit
                r = requests.post(os.environ['BOT_URL'],json={'url':url, 'token':team_token})
                if r:
                    flash('Visited','success')
                else:
                    flash(f'Error: {r.text}', 'error')
            except:
                flash('Error, contact an admin')
        else:
            flash('Invalid data','error')
            
    return render_template('abuse.html')