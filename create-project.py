import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

# Create project structure
project_root = 'project_root'
os.makedirs(project_root, exist_ok=True)
os.makedirs(os.path.join(project_root, 'app', 'templates'), exist_ok=True)

# app/__init__.py
init_content = '''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.routes import main, auth
    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app
'''
create_file(os.path.join(project_root, 'app', '__init__.py'), init_content)

# app/models.py
models_content = '''
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
'''
create_file(os.path.join(project_root, 'app', 'models.py'), models_content)

# app/routes.py
routes_content = '''
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

@main.route('/')
@login_required
def index():
    return render_template('dashboard.html')

@main.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    users = User.query.all()
    return render_template('admin.html', users=users)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_approved:
                flash('Your account is not approved yet.', 'warning')
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please wait for admin approval.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@main.route('/approve/<int:user_id>')
@login_required
def approve_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    flash(f'User {user.username} has been approved.', 'success')
    return redirect(url_for('main.admin'))
'''
create_file(os.path.join(project_root, 'app', 'routes.py'), routes_content)

# app/forms.py
forms_content = '''
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Please use a different email address.')
'''
create_file(os.path.join(project_root, 'app', 'forms.py'), forms_content)

# app/templates/base.html
base_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Flask App{% endblock %}</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <a class="navbar-brand" href="{{ url_for('main.index') }}">Flask App</a>
        <div class="navbar-nav">
            {% if current_user.is_authenticated %}
                <a class="nav-item nav-link" href="{{ url_for('main.index') }}">Home</a>
                {% if current_user.is_admin %}
                    <a class="nav-item nav-link" href="{{ url_for('main.admin') }}">Admin</a>
                {% endif %}
                <a class="nav-item nav-link" href="{{ url_for('auth.logout') }}">Logout</a>
            {% else %}
                <a class="nav-item nav-link" href="{{ url_for('auth.login') }}">Login</a>
                <a class="nav-item nav-link" href="{{ url_for('auth.register') }}">Register</a>
            {% endif %}
        </div>
    </nav>
    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
'''
create_file(os.path.join(project_root, 'app', 'templates', 'base.html'), base_html)

# app/templates/login.html
login_html = '''
{% extends "base.html" %}

{% block content %}
    <h1>Login</h1>
    <form method="POST" action="{{ url_for('auth.login') }}">
        {{ form.hidden_tag() }}
        <div class="form-group">
            {{ form.username.label }}
            {{ form.username(class="form-control") }}
        </div>
        <div class="form-group">
            {{ form.password.label }}
            {{ form.password(class="form-control") }}
        </div>
        <div class="form-check">
            {{ form.remember_me(class="form-check-input") }}
            {{ form.remember_me.label(class="form-check-label") }}
        </div>
        {{ form.submit(class="btn btn-primary") }}
    </form>
{% endblock %}
'''
create_file(os.path.join(project_root, 'app', 'templates', 'login.html'), login_html)

# app/templates/register.html
register_html = '''
{% extends "base.html" %}

{% block content %}
    <h1>Register</h1>
    <form method="POST" action="{{ url_for('auth.register') }}">
        {{ form.hidden_tag() }}
        <div class="form-group">
            {{ form.username.label }}
            {{ form.username(class="form-control") }}
        </div>
        <div class="form-group">
            {{ form.email.label }}
            {{ form.email(class="form-control") }}
        </div>
        <div class="form-group">
            {{ form.password.label }}
            {{ form.password(class="form-control") }}
        </div>
        <div class="form-group">
            {{ form.password2.label }}
            {{ form.password2(class="form-control") }}
        </div>
        {{ form.submit(class="btn btn-primary") }}
    </form>
{% endblock %}
'''
create_file(os.path.join(project_root, 'app', 'templates', 'register.html'), register_html)

# app/templates/dashboard.html
dashboard_html = '''
{% extends "base.html" %}

{% block content %}
    <h1>Welcome, {{ current_user.username }}!</h1>
    <p>This is your dashboard. You can add your content here.</p>
{% endblock %}
'''
create_file(os.path.join(project_root, 'app', 'templates', 'dashboard.html'), dashboard_html)

# app/templates/admin.html
admin_html = '''
{% extends "base.html" %}

{% block content %}
    <h1>Admin Dashboard</h1>
    <table class="table">
        <thead>
            <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Approved</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {% for user in users %}
                <tr>
                    <td>{{ user.username }}</td>
                    <td>{{ user.email }}</td>
                    <td>{{ 'Yes' if user.is_approved else 'No' }}</td>
                    <td>
                        {% if not user.is_approved %}
                            <a href="{{ url_for('main.approve_user', user_id=user.id) }}" class="btn btn-sm btn-primary">Approve</a>
                        {% endif %}
                    </td>
                </tr>
            {% endfor %}
        </tbody>
    </table>
{% endblock %}
'''
create_file(os.path.join(project_root, 'app', 'templates', 'admin.html'), admin_html)

# config.py
config_content = '''
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
'''
create_file(os.path.join(project_root, 'config.py'), config_content)

# run.py
run_content = '''
from app import create_app, db
from app.models import User

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

if __name__ == '__main__':
    app.run(debug=True)
'''
create_file(os.path.join(project_root, 'run.py'), run_content)

# requirements.txt
requirements_content = '''
Flask==2.0.1
Flask-SQLAlchemy==2.5.1
Flask-Login==0.5.0
Flask-WTF==0.15.1
email-validator==1.1.3
Flask-Migrate==3.1.0
'''
create_file(os.path.join(project_root, 'requirements.txt'), requirements_content)

print("Project structure and files have been created successfully.")
