from flask import Blueprint, redirect, render_template, request, flash, jsonify, url_for
from flask_login import login_required, current_user
from .models import Admin, Note, User, Chat
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  
            db.session.add(new_note) 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)



@views.route('/lounge', methods=['GET', 'POST'])
@login_required
def lounge():
    if request.method == 'POST': 
        chat = request.form.get('chat') 
        if len(chat) < 1:
            flash('Chat message is too short!', category='error') 
        else:
            new_chat = Chat(chat=chat, user_id=current_user.id)
            db.session.add(new_chat)
            db.session.commit()
            flash('Chat added!', category='success')
    
    # Query all chats to pass to the template
    all_chats = Chat.query.order_by(Chat.date.desc()).all()
    return render_template("lounge.html", user=current_user, chats=all_chats)
    
    


@views.route('/admin-dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    if not isinstance(current_user, Admin):
        flash('You must be an admin to access this page.', category='error')
        #return redirect(url_for('auth.admin_login'))
        users = User.query.all()  # Query all users to display in the admin dashboard

        admins=Admin.query.all()
        return render_template("admin-dashboard.html", user=current_user, users=users)
    users = User.query.all()  # Query all users to display in the admin dashboard
    admins=Admin.query.all()
    return render_template("admin-dashboard.html", user=current_user, users=users, admins=admins)


@views.route('/add-admin', methods=['POST'])
@login_required
def add_admin():
    if isinstance(current_user, Admin):
        flash('Access Denied: Only admins can add users.', category='error')
        return redirect(url_for('views.admin_dashboard'))

    email = request.form.get('email')
    full_name = request.form.get('full_name')
    password = request.form.get('password')

    # Check for duplicate emails
    if Admin.query.filter_by(email=email).first():
        flash('Email already exists.', category='error')
        return redirect(url_for('views.admin_dashboard'))

    new_admin = Admin(email=email, full_name=full_name, password=password)
    db.session.add(new_admin)
    db.session.commit()
    flash('Admin added successfully!', category='success')
    return redirect(url_for('views.admin_dashboard'))

@views.route('/add-user', methods=['POST'])
@login_required
def add_user():
    if isinstance(current_user, Admin):
        flash('Access Denied: Only admins can add users.', category='error')
        return redirect(url_for('views.admin_dashboard'))

    email = request.form.get('email')
    first_name = request.form.get('first_name')
    password = request.form.get('password')

    # Check for duplicate emails
    if User.query.filter_by(email=email).first():
        flash('Email already exists.', category='error')
        return redirect(url_for('views.admin_dashboard'))

    new_user = User(email=email, first_name=first_name, password=password)
    db.session.add(new_user)
    db.session.commit()
    flash('User added successfully!', category='success')
    return redirect(url_for('views.admin_dashboard'))

@views.route('/delete-user', methods=['POST'])
@login_required
def delete_user():
    if isinstance(current_user, Admin):  # Ensure only admins can delete users
        flash('Access Denied: Only admins can delete users.', category='error')
        return jsonify({'success': False}), 403

    user_data = json.loads(request.data)
    user_id = user_data.get('userId')
    user = User.query.get(user_id)

    if user:
        # Delete all chats associated with the user
        chats = Chat.query.filter_by(user_id=user_id).all()
        for chat in chats:
            db.session.delete(chat)
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()

        flash('User and their chats were successfully deleted.', category='success')
        return jsonify({'success': True})
    
    flash('User not found.', category='error')
    return jsonify({'success': False}), 404



@views.route('/edit-user', methods=['POST'])
@login_required
def edit_user():
    if isinstance(current_user, Admin):
        flash('Access Denied: Only admins can edit users.', category='error')
        return jsonify({'success': False}), 403

    user_data = json.loads(request.data)
    user_id = user_data.get('userId')
    email = user_data.get('email')
    first_name = user_data.get('first_name')

    user = User.query.get(user_id)
    if user:
        user.email = email
        user.first_name = first_name
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/delete-chat', methods=['POST'])
def delete_chat():  
    chat = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    chatId = chat['chatId']
    chat = Chat.query.get(chatId)
    if chat:
        if chat.user_id == current_user.id:
            db.session.delete(chat)
            db.session.commit()

    return jsonify({})

@views.route('/delete-all-chat', methods=['POST'])
@login_required
def delete_all_chats():
    if isinstance(current_user, Admin):  # Ensure only admins can perform this action
        flash('Access Denied: Only admins can delete all chats.', category='error')
        return jsonify({'success': False}), 403

    try:
        # Delete all chats
        db.session.query(Chat).delete()
        db.session.commit()
        flash('All chats deleted successfully!', category='success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting chats.', category='error')
        return jsonify({'success': False}), 500
