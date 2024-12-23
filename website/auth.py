from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Admin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
          
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@auth.route('/admin-addition', methods=['GET', 'POST'])
def admin_addition():
    if request.method == 'POST':
        email = request.form.get('admin-email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')

        admin = Admin.query.filter_by(email=email).first()
        if admin:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
          
            new_admin = Admin(email=email, full_name=full_name, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(new_admin)
            db.session.commit()
            login_user(new_admin, remember=True)
            flash('Account created!', category='success')
            return render_template("admin-dashboard.html", user=current_user)


    return render_template("admin-dashboard.html", user=current_user)


@auth.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('admin-email')
        password = request.form.get('password')

        admin = Admin.query.filter_by(email=email).first()

        if admin:
            if admin.password and check_password_hash(admin.password, password):
                flash('Logged in successfully!', category='success')
                login_user(admin, remember=True)
                return redirect(url_for('views.admin_dashboard'))  # Correctly redirect to dashboard
            else:
                flash('Invalid credentials. Please try again.', category='error')
        else:
            flash('Admin account does not exist.', category='error')

    return render_template("admin-login.html", user=current_user)




@auth.route('/admin', methods=['GET'])
@login_required
def admin():
    if not isinstance(current_user, Admin):
        flash('You must be an admin to access this page.', category='error')
        return redirect(url_for('auth.admin'))
    admins= Admin.query.all()
    users = User.query.all()  # Query all users to display in the admin dashboard
    
    return render_template("admin-dashboard.html", user=current_user, users=users, admins=admins)

