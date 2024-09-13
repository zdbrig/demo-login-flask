from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app.utils.email_handler import EmailHandler

# Initialize the email handler
email_handler = EmailHandler()

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
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_approved:
                flash('Your account is not approved yet.', 'warning')
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Invalid email or password', 'danger')
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

        # Send registration email
        email_handler.send_email(
            subject="Welcome to Our App!",
            message="Thank you for registering! Your account is currently pending approval. We appreciate your patience and look forward to having you on board soon. \n\nBest regards,\nSQOIN Team",
            email_to=user.email
        )

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

   # Send approval email
    email_handler.send_email(
        subject="Your Account Has Been Approved!",
        message="Congratulations ! 🎉 \nYour account has been approved! You can now log in and start making things happen. 🚀\n\nWe truly appreciate your trust in our platform. Welcome aboard!\n\nWarm regards,\nSQOIN Team",
        email_to=user.email
    )


    flash(f'User {user.username} has been approved.', 'success')
    return redirect(url_for('main.admin'))

@main.route('/suspend/<int:user_id>')
@login_required
def suspend_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)
    user.is_approved = False  # Set is_approved to False to suspend the user
    db.session.commit()

    # Send suspension email
    email_handler.send_email(
        subject="Your Account Has Been Suspended",
        message="We regret to inform you that your account has been suspended. If you believe this is a mistake or have any questions, please contact our support team for assistance. \n\nBest regards,\nSQOIN Team",
        email_to=user.email
    )

    flash(f'User {user.username} has been suspended.', 'warning')
    return redirect(url_for('main.admin'))
