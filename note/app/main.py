from flask import Blueprint, render_template, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.utils import redirect
from datetime import date, datetime
from .models import User, Note
from . import db, visit_url

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('home.html')

@main.route('/note', methods=['GET'])
@login_required
def show_notes():
    note_id = request.args.get('id')
    if not note_id:
        notes = Note.query.filter(Note.user_id == current_user.id).all()
        return render_template('notes.html', notes=notes)
    else:
        note = Note.query.filter(Note.id == note_id, Note.user_id == current_user.id).first()
        if note:
            return render_template('note.html',note=note)
        else:
            return 'Not found', 404

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
            return redirect(url_for('main.show_notes'))
        else:
            flash('Invalid data')
            
    return render_template('add_note.html')


@main.route('/abuse', methods=['GET','POST'])
@login_required
def report_abuse():
    if request.method == 'POST':
        url = request.form.get('url')

        if url and url.startswith('http'):
            if visit_url(url):
                return 'ok'
            else:
                return 'something is wrong', 500
        else:
            flash('Invalid data')
            
    return render_template('abuse.html')