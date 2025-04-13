from flask import Flask, render_template, redirect, jsonify, session, request, json, make_response, url_for, flash
from forms import AddToList, AddUserForm, LogInForm, EditUserForm, DeleteUserForm, ContactForm
import uuid
import os
import pdfkit
import smtplib
from email.mime.text import MIMEText
import requests
import config
from helpers import prepPdfData
import logging
from psycopg2 import IntegrityError
from flask_migrate import Migrate
import json
import datetime
from werkzeug.exceptions import MethodNotAllowed, Forbidden
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

app.config['SECRET_KEY'] = config.SECRET_KEY
app.debug = False

# Session security configurations
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['SESSION_COOKIE_SECURE'] = True    # Cookies only sent over HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' # Protect against CSRF
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=60)  # Timeout after 60 min

csrf = CSRFProtect(app)

# Exempt form routes (already protected by WTForms)
csrf.exempt('user.new')
csrf.exempt('user.login')
csrf.exempt('contact')
csrf.exempt('users.edit')
csrf.exempt('users.delete')

db_conn_str = config.DATABASE_URI
if config.IS_LOCAL == 0:
    db_conn_str = db_conn_str.replace("postgres", "postgresql")
app.config['SQLALCHEMY_DATABASE_URI'] = db_conn_str
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

# Initialize Flask-Limiter with in-memory storage
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

import models
from models import db

models.connect_db(app)
migrate = Migrate(app, db)

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

# Existing log_to_db function (unchanged)
def log_to_db(level, message, user_id=None, request_path=None, details=None, ip_address=None, user_agent=None, list_uuid=None):
    """Log a message to the log_entry table without committing the transaction."""
    def convert_datetime(obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return str(obj)
    try:
        # Convert any datetime objects in details to strings
        if details:
            details = json.loads(json.dumps(details, default=convert_datetime))
        log_entry = models.LogEntry(
            log_level=level,
            message=message,
            list_uuid=list_uuid,
            user_id=user_id,
            request_path=request_path,
            log_details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        models.db.session.add(log_entry)
        # Do not commit here; let the calling route handle the commit
    except Exception as e:
        logging.error(f"Failed to log to DB: {e}")

# Log session timeouts
@app.before_request
def check_session_timeout():
    session.permanent = True  # Enable timeout
    if 'username' in session:
        last_activity = session.get('last_activity')
        now = datetime.datetime.utcnow()
        if last_activity:
            last_activity = datetime.datetime.fromisoformat(last_activity)
            if (now - last_activity) > app.config['PERMANENT_SESSION_LIFETIME']:
                username = session['username']
                ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
                if ip_address:
                    ip_address = ip_address.split(',')[0].strip()
                user_agent = request.headers.get('User-Agent')
                session.pop('username', None)
                log_to_db(
                    'INFO',
                    'Session timed out',
                    user_id=username,
                    request_path=request.path,
                    details={'username': username},
                    ip_address=ip_address,
                    user_agent=user_agent,
                    list_uuid=None
                )
                flash('Your session has timed out. Please log in again.', 'warning')
                return redirect(url_for('log_in_user'))
        session['last_activity'] = now.isoformat()

# CSRF Failure error handler
@app.errorhandler(403)
def csrf_error(e):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    user_id = session.get('username')
    log_to_db(
        'WARNING',
        'CSRF token validation failed',
        user_id=user_id,
        request_path=request.path,
        details={'error': str(e)},
        ip_address=ip_address,
        user_agent=user_agent,
        list_uuid=None
    )
    usage_event = models.UsageEvent(
        event_type='csrf_failure',
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        event_details={
            'request_path': request.path,
            'error': str(e)
        }
    )
    models.db.session.add(usage_event)
    models.db.session.commit()
    flash('Invalid request. Please refresh the page.', 'danger')
    return render_template('error.html', error="Invalid request. Please refresh the page."), 403

# Rate limit error handler
@app.errorhandler(429)
def ratelimit_handler(e):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    user_id = session.get('username')
    log_to_db(
        'WARNING',
        f"Rate limit exceeded: {e.description}",
        user_id=user_id,
        request_path=request.path,
        details={'limit': e.description},
        ip_address=ip_address,
        user_agent=user_agent,
        list_uuid=None
    )
    models.db.session.commit()
    flash('Too many requests. Please try again later.', 'danger')
    return render_template('error.html', error="Too many requests. Please try again later."), 429

# Verify reCAPTCHA token with Google API
def validate_recaptcha(response, remote_ip):
    secret_key = config.RECAPTCHA_SECRET_KEY
    payload = {
        'secret': secret_key,
        'response': response,
        'remoteip': remote_ip
    }
    recaptcha_result = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload).json()
    success = recaptcha_result.get('success', False)
    if not success:
        logging.debug(f"reCAPTCHA failed with error-codes: {recaptcha_result.get('error-codes', 'No error codes provided')}")
    return success

@app.route('/')
def main():
    return redirect('/new')

@app.route('/new')
def show_creator():
    add_to_list = AddToList()
    return render_template('fc.html', add_to_list=add_to_list)

@app.route('/known-issues')
def known_issues():
    return render_template('known-issues.html')

@app.route('/contact', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def contact():
    form = ContactForm()
    if request.method == 'POST':
        logging.debug("Form data: %s", form.data)
        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            message = form.message.data
            recaptcha_response = form.recaptcha_response.data
            ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ip_address:
                ip_address = ip_address.split(',')[0].strip()
            user_agent = request.headers.get('User-Agent')
            if not validate_recaptcha(recaptcha_response, ip_address):
                flash('reCAPTCHA verification failed. Please try again.', 'error')
                log_to_db('WARNING', 'reCAPTCHA verification failed', user_id=None, request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
                return redirect(url_for('contact'))
            msg = MIMEText(f"Name: {name}\nEmail: {email}\nMessage: {message}")
            msg['Subject'] = 'New Contact Form Submission from ForceCreator'
            msg['From'] = config.EMAIL_ADDRESS
            msg['To'] = config.EMAIL_ADDRESS
            msg['Reply-To'] = email
            try:
                with smtplib.SMTP('mi3-ts107.a2hosting.com', 587) as server:
                    server.starttls()
                    server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
                    server.send_message(msg)
                flash('Your message has been sent successfully!', 'success')
                log_to_db('INFO', 'Contact form submitted successfully', user_id=None, request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
            except Exception as e:
                flash(f'Error sending message: {str(e)}', 'danger')
                log_to_db('ERROR', f"Error sending contact form message: {e}", user_id=None, request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
            return redirect(url_for('contact'))
        else:
            logging.debug("Form validation failed: %s", form.errors)
            ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ip_address:
                ip_address = ip_address.split(',')[0].strip()
            user_agent = request.headers.get('User-Agent')
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {field}: {error}", 'danger')
            log_to_db('WARNING', 'Contact form validation failed', user_id=None, request_path=request.path, details={'errors': form.errors}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return render_template('contact.html', form=form, recaptcha_site_key=config.RECAPTCHA_SITE_KEY)

############### USER ROUTES ###############

@app.route('/user/new', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def new_user():
    form = AddUserForm()
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    if request.method == 'POST':
        logging.debug(f"Raw form data: {request.form}")
        log_to_db('DEBUG', 'User registration form submitted', user_id=None, request_path=request.path, details={'form_data': request.form.to_dict()}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    if form.validate_on_submit():
        recaptcha_response = form.recaptcha_response.data
        logging.debug(f"reCAPTCHA response from form: {recaptcha_response}")
        if not validate_recaptcha(recaptcha_response, ip_address):
            log_to_db('WARNING', 'reCAPTCHA verification failed during user registration', user_id=None, request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
            return render_template('user-new.html', form=form, recaptcha_site_key=config.RECAPTCHA_SITE_KEY)
        username = form.username.data
        password = form.password.data
        email = form.email.data
        if models.Account.query.filter_by(email=email).first():
            flash('That email is already registered. Please use a different email or log in.', 'danger')
            log_to_db('WARNING', 'Email already registered during user registration', user_id=None, request_path=request.path, details={'email': email}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
            return render_template('user-new.html', form=form, recaptcha_site_key=config.RECAPTCHA_SITE_KEY)
        try:
            user = models.Account.register(username, password)
            user.email = email
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            models.db.session.add(user)
            # Log usage event
            usage_event = models.UsageEvent(
                event_type='user_registered',
                user_id=username,
                ip_address=ip_address,
                user_agent=user_agent,
                event_details={'email': email}
            )
            models.db.session.add(usage_event)
            models.db.session.commit()
            session["username"] = user.username
            flash('User registered successfully!', 'success')
            log_to_db('INFO', 'User registered successfully', user_id=username, request_path=request.path, details={'username': username, 'email': email}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
            return redirect(f'/users/{user.username}')
        except IntegrityError as e:
            models.db.session.rollback()
            flash('An error occurred. The username might already be taken. Please try a different username.', 'danger')
            log_to_db('ERROR', f"IntegrityError during user registration: {e}", user_id=None, request_path=request.path, details={'username': username, 'error_type': str(type(e))}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
            models.db.session.commit()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
        log_to_db('WARNING', 'User registration form validation failed', user_id=None, request_path=request.path, details={'errors': form.errors}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return render_template('user-new.html', form=form, recaptcha_site_key=config.RECAPTCHA_SITE_KEY)

@app.route('/user/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def log_in_user():
    form = LogInForm()
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    if form.validate_on_submit():
        recaptcha_response = form.recaptcha_response.data
        logging.debug(f"reCAPTCHA response from form: {recaptcha_response}")
        if not validate_recaptcha(recaptcha_response, ip_address):
            flash('reCAPTCHA verification failed. Please try again.', 'danger')
            log_to_db('WARNING', 'reCAPTCHA verification failed during login', user_id=None, request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
            return render_template('user-log-in.html', form=form, recaptcha_site_key=config.RECAPTCHA_SITE_KEY)
        usr = form.username.data
        pwd = form.password.data
        user = models.Account.authenticate(usr, pwd)
        if user:
            session["username"] = user.username
            # Log usage event
            usage_event = models.UsageEvent(
                event_type='user_login',
                user_id=user.username,
                ip_address=ip_address,
                user_agent=user_agent,
                event_details={'username': user.username}
            )
            models.db.session.add(usage_event)
            models.db.session.commit()
            flash('Login successful!', 'success')
            log_to_db('INFO', 'User logged in successfully', user_id=user.username, request_path=request.path, details={'username': user.username}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
            return redirect(f'/users/{user.username}')
        else:
            flash("* Username or Password is incorrect *", 'danger')
            log_to_db('WARNING', 'Login failed: incorrect username or password', user_id=None, request_path=request.path, details={'username': usr}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
        log_to_db('WARNING', 'Login form validation failed', user_id=None, request_path=request.path, details={'errors': form.errors}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return render_template('user-log-in.html', form=form, recaptcha_site_key=config.RECAPTCHA_SITE_KEY)

@app.route('/user/logout')
def log_out_user():
    username = session.get("username")
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    session.pop("username", None)
    # Log usage event
    usage_event = models.UsageEvent(
        event_type='user_logout',
        user_id=username,
        ip_address=ip_address,
        user_agent=user_agent,
        event_details={'username': username}
    )
    models.db.session.add(usage_event)
    models.db.session.commit()
    flash('You have been logged out successfully.', 'success')
    log_to_db('INFO', 'User logged out successfully', user_id=username, request_path=request.path, details={'username': username}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return redirect('/user/login')

@app.route('/users/<username>')
def show_secrets(username):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    if 'username' not in session or session['username'] != username:
        log_to_db('WARNING', 'Unauthorized access to user profile', user_id=None, request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
        return redirect('/')
    user = models.Account.query.get_or_404(username)
    # Filter saved lists to exclude list_status='deleted' or 'pdf'
    saved_lists = models.SavedList.query.filter_by(username=username).filter(models.SavedList.list_status == 'saved').all()
    saved_list_data = [save.pack_data() for save in saved_lists]
    json_list_data = json.dumps(saved_list_data)
    delete_form = DeleteUserForm()
    log_to_db('INFO', 'User profile accessed', user_id=username, request_path=request.path, details={'username': username, 'list_count': len(saved_lists)}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return render_template('user-info.html', user=user, savedlists=saved_lists, listdata=json_list_data, delete_form=delete_form, recaptcha_site_key=config.RECAPTCHA_SITE_KEY)

@app.route('/users/<username>/delete', methods=['POST'])
@limiter.limit("5 per minute")
def delete_user(username):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    if 'username' not in session or session['username'] != username:
        flash('You must be logged in to delete your account.', 'danger')
        log_to_db('WARNING', 'Unauthorized attempt to delete user account', user_id=None, request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
        return redirect('/user/login')
    form = DeleteUserForm()
    if form.validate_on_submit():
        recaptcha_response = form.recaptcha_response.data
        logging.debug(f"reCAPTCHA response from form: {recaptcha_response}")
        if not validate_recaptcha(recaptcha_response, ip_address):
            flash('reCAPTCHA verification failed. Please try again.', 'danger')
            log_to_db('WARNING', 'reCAPTCHA verification failed during user deletion', user_id=username, request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
            return redirect(f'/users/{username}')
        user = models.Account.query.get_or_404(username)
        # Log usage event
        usage_event = models.UsageEvent(
            event_type='user_deleted',
            user_id=username,
            ip_address=ip_address,
            user_agent=user_agent,
            event_details={'username': username}
        )
        models.db.session.add(usage_event)
        models.db.session.delete(user)
        models.db.session.commit()
        session.pop("username", None)
        flash('Your account has been deleted successfully.', 'success')
        log_to_db('INFO', 'User account deleted successfully', user_id=username, request_path=request.path, details={'username': username}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
        return redirect('/user/new')
    else:
        flash('Form validation failed.', 'danger')
        log_to_db('WARNING', 'User deletion form validation failed', user_id=username, request_path=request.path, details={'errors': form.errors}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
        return redirect(f'/users/{username}')

@app.route('/users/<username>/edit', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def edit_user(username):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    if 'username' not in session:
        flash('Please log in to edit your account.', 'danger')
        log_to_db('WARNING', 'Unauthorized attempt to edit user account: not logged in', user_id=None, request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
        return redirect('/user/login')
    if session['username'] != username:
        flash('You are not authorized to edit this account.', 'danger')
        log_to_db('WARNING', 'Unauthorized attempt to edit user account: wrong user', user_id=session.get('username'), request_path=request.path, details={'attempted_username': username}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
        return redirect(f'/users/{session["username"]}')
    
    form = EditUserForm()
    user = models.Account.query.get_or_404(username)
    
    if form.validate_on_submit():
        recaptcha_response = form.recaptcha_response.data
        logging.debug(f"reCAPTCHA response from form: {recaptcha_response}")
        if not validate_recaptcha(recaptcha_response, ip_address):
            flash('reCAPTCHA verification failed. Please try again.', 'danger')
            log_to_db('WARNING', 'reCAPTCHA verification failed during user edit', user_id=username, request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
            return render_template('user-edit.html', form=form, user=user, recaptcha_site_key=config.RECAPTCHA_SITE_KEY)
        usr = session['username']
        pwd = form.password.data
        user = models.Account.authenticate(usr, pwd)
        if user:
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data
            # Log usage event
            usage_event = models.UsageEvent(
                event_type='user_updated',
                user_id=user.username,
                ip_address=ip_address,
                user_agent=user_agent,
                event_details={
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email
                }
            )
            models.db.session.add(usage_event)
            models.db.session.commit()
            flash('Account updated successfully!', 'success')
            log_to_db('INFO', 'User account updated successfully', user_id=user.username, request_path=request.path, details={'username': user.username, 'email': user.email}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
            return redirect(f'/users/{usr}')
        else:
            flash("* Password is incorrect *", 'danger')
            log_to_db('WARNING', 'User edit failed: incorrect password', user_id=usr, request_path=request.path, details={'username': usr}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
        log_to_db('WARNING', 'User edit form validation failed', user_id=username, request_path=request.path, details={'errors': form.errors}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return render_template('user-edit.html', form=form, user=user, recaptcha_site_key=config.RECAPTCHA_SITE_KEY)

############### FC USER ROUTES ###############

@app.route('/lists/save', methods=['POST'])
@limiter.limit("20 per hour")
def save_forcelist():
    save_data = request.get_json()
    list_id = save_data.get('uuid')
    current_username = session.get("username")
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')

    log_to_db('DEBUG', 'Save data received', user_id=current_username, request_path=request.path, details={
        'uuid': save_data.get('uuid'),
        'force_name': save_data.get('name', 'Unknown')
    }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)

    try:
        if 'username' not in session:
            log_to_db('DEBUG', 'User not logged in, creating new save', user_id=current_username, request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
            new_save = models.SavedList()
            new_uuid = uuid.uuid4()
            new_save.uuid = str(new_uuid)
            new_save.list_status = 'saved'
            list_id = new_save.save_to_db(save_data)
            event_type = 'list_created'
            event_details = {'force_name': save_data.get('name', 'Unknown')}
        else:
            log_to_db('DEBUG', 'User logged in, checking conditions', user_id=current_username, request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)
            current_username = session["username"]
            if 'uuid' in save_data and save_data.get('username') == current_username:
                log_to_db('DEBUG', 'Updating existing save for logged-in user', user_id=current_username, request_path=request.path, details={'uuid': save_data['uuid']}, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)
                saved_list = models.SavedList.query.get_or_404(save_data['uuid'])
                saved_list_dict = models.serialize(saved_list)

                # Track field changes
                field_changes = {}
                if saved_list.name != save_data['name']:
                    field_changes['name'] = {'old': saved_list.name, 'new': save_data['name']}
                if saved_list.maxpoints != save_data['maxpoints']:
                    field_changes['maxpoints'] = {'old': saved_list.maxpoints, 'new': save_data['maxpoints']}
                if saved_list.totalforcepoints != save_data['totalforcepoints']:
                    field_changes['totalforcepoints'] = {'old': saved_list.totalforcepoints, 'new': save_data['totalforcepoints']}
                if saved_list.nationality_id != save_data['nationality_id']:
                    field_changes['nationality_id'] = {'old': saved_list.nationality_id, 'new': save_data['nationality_id']}
                if saved_list.faction_id != save_data['faction_id']:
                    field_changes['faction_id'] = {'old': saved_list.faction_id, 'new': save_data['faction_id']}
                if saved_list.forceoption_id != save_data.get('forceoption_id'):
                    field_changes['forceoption_id'] = {'old': saved_list.forceoption_id, 'new': save_data.get('forceoption_id')}
                if saved_list.commander_id != save_data['commander_id']:
                    field_changes['commander_id'] = {'old': saved_list.commander_id, 'new': save_data['commander_id']}
                if saved_list.commandernickname != save_data['commandernickname']:
                    field_changes['commandernickname'] = {'old': saved_list.commandernickname, 'new': save_data['commandernickname']}
                if saved_list.commanderhorseselected != save_data['commanderhorseselected']:
                    field_changes['commanderhorseselected'] = {'old': saved_list.commanderhorseselected, 'new': save_data['commanderhorseselected']}
                if saved_list.commandersr1_id != save_data.get('commandersr1_id'):
                    field_changes['commandersr1_id'] = {'old': saved_list.commandersr1_id, 'new': save_data.get('commandersr1_id')}
                if saved_list.commandersr2_id != save_data.get('commandersr2_id'):
                    field_changes['commandersr2_id'] = {'old': saved_list.commandersr2_id, 'new': save_data.get('commandersr2_id')}
                if saved_list.idcounter != save_data['idcounter']:
                    field_changes['idcounter'] = {'old': saved_list.idcounter, 'new': save_data['idcounter']}
                if saved_list.artillerycount != save_data['artillerycount']:
                    field_changes['artillerycount'] = {'old': saved_list.artillerycount, 'new': save_data['artillerycount']}
                if saved_list.charactercount != save_data['charactercount']:
                    field_changes['charactercount'] = {'old': saved_list.charactercount, 'new': save_data['charactercount']}
                if saved_list.shipcount != save_data['shipcount']:
                    field_changes['shipcount'] = {'old': saved_list.shipcount, 'new': save_data['shipcount']}
                if saved_list.unitcount != save_data['unitcount']:
                    field_changes['unitcount'] = {'old': saved_list.unitcount, 'new': save_data['unitcount']}
                if saved_list.misccount != save_data['misccount']:
                    field_changes['misccount'] = {'old': saved_list.misccount, 'new': save_data['misccount']}

                # Update savedlist fields in-place
                saved_list.name = save_data['name']
                saved_list.maxpoints = save_data['maxpoints']
                saved_list.totalforcepoints = save_data['totalforcepoints']
                saved_list.nationality_id = save_data['nationality_id']
                saved_list.faction_id = save_data['faction_id']
                saved_list.forceoption_id = save_data.get('forceoption_id', 0) or None
                saved_list.commander_id = save_data['commander_id']
                saved_list.commandernickname = save_data['commandernickname']
                saved_list.commanderhorseselected = save_data['commanderhorseselected']
                saved_list.commandersr1_id = save_data.get('commandersr1_id', 0) or None
                saved_list.commandersr2_id = save_data.get('commandersr2_id', 0) or None
                saved_list.idcounter = save_data['idcounter']
                saved_list.artillerycount = save_data['artillerycount']
                saved_list.charactercount = save_data['charactercount']
                saved_list.shipcount = save_data['shipcount']
                saved_list.unitcount = save_data['unitcount']
                saved_list.misccount = save_data['misccount']
                saved_list.last_modified = db.func.now()
                saved_list.list_status = 'saved'

                # Manage components: delete old ones, add new ones
                existing_components = {
                    'artillery': {comp.fid: comp for comp in saved_list.artillerycomponent},
                    'character': {comp.fid: comp for comp in saved_list.charactercomponent},
                    'ship': {comp.fid: comp for comp in saved_list.shipcomponent},
                    'unit': {comp.fid: comp for comp in saved_list.unitcomponent},
                    'custom': {comp.fid: comp for comp in saved_list.customcomponent},
                }

                changes = {
                    'added': {'artillery': [], 'character': [], 'ship': [], 'unit': [], 'custom': []},
                    'removed': {'artillery': [], 'character': [], 'ship': [], 'unit': [], 'custom': []},
                    'updated': {'artillery': [], 'character': [], 'ship': [], 'unit': [], 'custom': []}
                }

                # Process artillery components
                new_artillery_fids = set()
                if save_data['artillerycount'] > 0:
                    for n in range(save_data['artillerycount']):
                        key_prefix = f'artillery_{n+1}_'
                        fid = save_data.get(f'{key_prefix}fid', '')
                        if not fid:  # Skip empty fid values
                            continue
                        new_artillery_fids.add(fid)
                        if fid in existing_components['artillery']:
                            comp = existing_components['artillery'][fid]
                            comp_changes = {}
                            if comp.nickname != save_data.get(f'{key_prefix}nickname', ''):
                                comp_changes['nickname'] = {'old': comp.nickname, 'new': save_data.get(f'{key_prefix}nickname', '')}
                            if comp.artillery_id != save_data.get(f'{key_prefix}id'):
                                comp_changes['artillery_id'] = {'old': comp.artillery_id, 'new': save_data.get(f'{key_prefix}id')}
                            if comp.qty != save_data.get(f'{key_prefix}qty', 1):
                                comp_changes['qty'] = {'old': comp.qty, 'new': save_data.get(f'{key_prefix}qty', 1)}
                            if comp.options != save_data.get(f'{key_prefix}options', ''):
                                comp_changes['options'] = {'old': comp.options, 'new': save_data.get(f'{key_prefix}options', '')}
                            comp.nickname = save_data.get(f'{key_prefix}nickname', '')
                            comp.artillery_id = save_data.get(f'{key_prefix}id')
                            comp.qty = save_data.get(f'{key_prefix}qty', 1)
                            comp.options = save_data.get(f'{key_prefix}options', '')
                            if comp_changes:
                                changes['updated']['artillery'].append({
                                    'fid': fid,
                                    'name': comp.nickname,
                                    'artillery_id': comp.artillery_id,
                                    'changes': comp_changes
                                })
                        else:
                            new_comp = models.ArtilleryComponent()
                            new_comp.list_uuid = saved_list.uuid
                            new_comp.nickname = save_data.get(f'{key_prefix}nickname', '')
                            new_comp.fid = fid
                            new_comp.artillery_id = save_data.get(f'{key_prefix}id')
                            new_comp.qty = save_data.get(f'{key_prefix}qty', 1)
                            new_comp.options = save_data.get(f'{key_prefix}options', '')
                            models.db.session.add(new_comp)
                            changes['added']['artillery'].append({
                                'fid': fid,
                                'name': new_comp.nickname,
                                'artillery_id': new_comp.artillery_id
                            })
                for fid, comp in existing_components['artillery'].items():
                    if fid not in new_artillery_fids:
                        models.db.session.delete(comp)
                        changes['removed']['artillery'].append({
                            'fid': fid,
                            'name': comp.nickname,
                            'artillery_id': comp.artillery_id
                        })

                # Process character components
                new_character_fids = set()
                if save_data['charactercount'] > 0:
                    for n in range(save_data['charactercount']):
                        key_prefix = f'character_{n+1}_'
                        fid = save_data.get(f'{key_prefix}fid', '')
                        if not fid:
                            continue
                        new_character_fids.add(fid)
                        if fid in existing_components['character']:
                            comp = existing_components['character'][fid]
                            comp_changes = {}
                            if comp.nickname != save_data.get(f'{key_prefix}nickname', ''):
                                comp_changes['nickname'] = {'old': comp.nickname, 'new': save_data.get(f'{key_prefix}nickname', '')}
                            if comp.character_id != save_data.get(f'{key_prefix}id'):
                                comp_changes['character_id'] = {'old': comp.character_id, 'new': save_data.get(f'{key_prefix}id')}
                            comp.nickname = save_data.get(f'{key_prefix}nickname', '')
                            comp.character_id = save_data.get(f'{key_prefix}id')
                            if comp_changes:
                                changes['updated']['character'].append({
                                    'fid': fid,
                                    'name': comp.nickname,
                                    'character_id': comp.character_id,
                                    'changes': comp_changes
                                })
                        else:
                            new_comp = models.CharacterComponent()
                            new_comp.list_uuid = saved_list.uuid
                            new_comp.nickname = save_data.get(f'{key_prefix}nickname', '')
                            new_comp.fid = fid
                            new_comp.character_id = save_data.get(f'{key_prefix}id')
                            models.db.session.add(new_comp)
                            changes['added']['character'].append({
                                'fid': fid,
                                'name': new_comp.nickname,
                                'character_id': new_comp.character_id
                            })
                for fid, comp in existing_components['character'].items():
                    if fid not in new_character_fids:
                        models.db.session.delete(comp)
                        changes['removed']['character'].append({
                            'fid': fid,
                            'name': comp.nickname,
                            'character_id': comp.character_id
                        })

                # Process ship components
                new_ship_fids = set()
                if save_data['shipcount'] > 0:
                    for n in range(save_data['shipcount']):
                        key_prefix = f'ship_{n+1}_'
                        fid = save_data.get(f'{key_prefix}fid', '')
                        if not fid:
                            continue
                        new_ship_fids.add(fid)
                        if fid in existing_components['ship']:
                            comp = existing_components['ship'][fid]
                            comp_changes = {}
                            if comp.nickname != save_data.get(f'{key_prefix}nickname', ''):
                                comp_changes['nickname'] = {'old': comp.nickname, 'new': save_data.get(f'{key_prefix}nickname', '')}
                            if comp.ship_id != save_data.get(f'{key_prefix}id'):
                                comp_changes['ship_id'] = {'old': comp.ship_id, 'new': save_data.get(f'{key_prefix}id')}
                            if comp.upgrades != save_data.get(f'{key_prefix}upgrades', ''):
                                comp_changes['upgrades'] = {'old': comp.upgrades, 'new': save_data.get(f'{key_prefix}upgrades', '')}
                            comp.nickname = save_data.get(f'{key_prefix}nickname', '')
                            comp.ship_id = save_data.get(f'{key_prefix}id')
                            comp.upgrades = save_data.get(f'{key_prefix}upgrades', '')
                            if comp_changes:
                                changes['updated']['ship'].append({
                                    'fid': fid,
                                    'name': comp.nickname,
                                    'ship_id': comp.ship_id,
                                    'changes': comp_changes
                                })
                        else:
                            new_comp = models.ShipComponent()
                            new_comp.list_uuid = saved_list.uuid
                            new_comp.nickname = save_data.get(f'{key_prefix}nickname', '')
                            new_comp.fid = fid
                            new_comp.ship_id = save_data.get(f'{key_prefix}id')
                            new_comp.upgrades = save_data.get(f'{key_prefix}upgrades', '')
                            models.db.session.add(new_comp)
                            changes['added']['ship'].append({
                                'fid': fid,
                                'name': new_comp.nickname,
                                'ship_id': new_comp.ship_id
                            })
                for fid, comp in existing_components['ship'].items():
                    if fid not in new_ship_fids:
                        models.db.session.delete(comp)
                        changes['removed']['ship'].append({
                            'fid': fid,
                            'name': comp.nickname,
                            'ship_id': comp.ship_id
                        })

                # Process unit components
                new_unit_fids = set()
                if save_data['unitcount'] > 0:
                    for n in range(save_data['unitcount']):
                        key_prefix = f'unit_{n+1}_'
                        fid = save_data.get(f'{key_prefix}fid', '')
                        if not fid:
                            continue
                        new_unit_fids.add(fid)
                        if fid in existing_components['unit']:
                            comp = existing_components['unit'][fid]
                            comp_changes = {}
                            if comp.nickname != save_data.get(f'{key_prefix}nickname', ''):
                                comp_changes['nickname'] = {'old': comp.nickname, 'new': save_data.get(f'{key_prefix}nickname', '')}
                            if comp.unit_id != save_data.get(f'{key_prefix}id'):
                                comp_changes['unit_id'] = {'old': comp.unit_id, 'new': save_data.get(f'{key_prefix}id')}
                            if comp.qty != save_data.get(f'{key_prefix}qty', 1):
                                comp_changes['qty'] = {'old': comp.qty, 'new': save_data.get(f'{key_prefix}qty', 1)}
                            if comp.options != save_data.get(f'{key_prefix}options', ''):
                                comp_changes['options'] = {'old': comp.options, 'new': save_data.get(f'{key_prefix}options', '')}
                            comp.nickname = save_data.get(f'{key_prefix}nickname', '')
                            comp.unit_id = save_data.get(f'{key_prefix}id')
                            comp.qty = save_data.get(f'{key_prefix}qty', 1)
                            comp.options = save_data.get(f'{key_prefix}options', '')
                            if comp_changes:
                                changes['updated']['unit'].append({
                                    'fid': fid,
                                    'name': comp.nickname,
                                    'unit_id': comp.unit_id,
                                    'changes': comp_changes
                                })
                        else:
                            new_comp = models.UnitComponent()
                            new_comp.list_uuid = saved_list.uuid
                            new_comp.nickname = save_data.get(f'{key_prefix}nickname', '')
                            new_comp.fid = fid
                            new_comp.unit_id = save_data.get(f'{key_prefix}id')
                            new_comp.qty = save_data.get(f'{key_prefix}qty', 1)
                            new_comp.options = save_data.get(f'{key_prefix}options', '')
                            models.db.session.add(new_comp)
                            changes['added']['unit'].append({
                                'fid': fid,
                                'name': new_comp.nickname,
                                'unit_id': new_comp.unit_id
                            })
                for fid, comp in existing_components['unit'].items():
                    if fid not in new_unit_fids:
                        models.db.session.delete(comp)
                        changes['removed']['unit'].append({
                            'fid': fid,
                            'name': comp.nickname,
                            'unit_id': comp.unit_id
                        })

                # Process custom components
                new_custom_fids = set()
                if save_data['misccount'] > 0:
                    for n in range(save_data['misccount']):
                        key_prefix = f'misc_{n+1}_'
                        fid = save_data.get(f'{key_prefix}fid', '')
                        if not fid:
                            continue
                        new_custom_fids.add(fid)
                        if fid in existing_components['custom']:
                            comp = existing_components['custom'][fid]
                            comp_changes = {}
                            if comp.name != save_data.get(f'{key_prefix}name', ''):
                                comp_changes['name'] = {'old': comp.name, 'new': save_data.get(f'{key_prefix}name', '')}
                            if comp.details != save_data.get(f'{key_prefix}details', ''):
                                comp_changes['details'] = {'old': comp.details, 'new': save_data.get(f'{key_prefix}details', '')}
                            if comp.points != save_data.get(f'{key_prefix}points', 0):
                                comp_changes['points'] = {'old': comp.points, 'new': save_data.get(f'{key_prefix}points', 0)}
                            if comp.qty != save_data.get(f'{key_prefix}qty', 1):
                                comp_changes['qty'] = {'old': comp.qty, 'new': save_data.get(f'{key_prefix}qty', 1)}
                            comp.name = save_data.get(f'{key_prefix}name', '')
                            comp.details = save_data.get(f'{key_prefix}details', '')
                            comp.points = save_data.get(f'{key_prefix}points', 0)
                            comp.qty = save_data.get(f'{key_prefix}qty', 1)
                            if comp_changes:
                                changes['updated']['custom'].append({
                                    'fid': fid,
                                    'name': comp.name,
                                    'changes': comp_changes
                                })
                        else:
                            new_comp = models.CustomComponent()
                            new_comp.list_uuid = saved_list.uuid
                            new_comp.name = save_data.get(f'{key_prefix}name', '')
                            new_comp.fid = fid
                            new_comp.details = save_data.get(f'{key_prefix}details', '')
                            new_comp.points = save_data.get(f'{key_prefix}points', 0)
                            new_comp.qty = save_data.get(f'{key_prefix}qty', 1)
                            models.db.session.add(new_comp)
                            changes['added']['custom'].append({
                                'fid': fid,
                                'name': new_comp.name
                            })
                for fid, comp in existing_components['custom'].items():
                    if fid not in new_custom_fids:
                        models.db.session.delete(comp)
                        changes['removed']['custom'].append({
                            'fid': fid,
                            'name': comp.name
                        })

                list_id = saved_list.uuid
                event_type = 'list_updated'
                event_details = {
                    'force_name': save_data.get('name', 'Unknown'),
                    'field_changes': field_changes,
                    'component_changes': changes
                }
            else:
                log_to_db('DEBUG', 'Creating new save for logged-in user', user_id=current_username, request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
                new_save = models.SavedList()
                new_uuid = uuid.uuid4()
                new_save.uuid = str(new_uuid)
                new_save.username = current_username
                new_save.list_status = 'saved'
                list_id = new_save.save_to_db(save_data)
                event_type = 'list_created'
                event_details = {'force_name': save_data.get('name', 'Unknown')}

        # Log usage event
        usage_event = models.UsageEvent(
            event_type=event_type,
            user_id=current_username,
            list_uuid=list_id,
            ip_address=ip_address,
            user_agent=user_agent,
            event_details=event_details
        )
        models.db.session.add(usage_event)
        models.db.session.commit()

        log_to_db('INFO', 'List saved successfully', user_id=current_username, request_path=request.path, details={'uuid': list_id, 'event_type': event_type}, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)
        return list_id, 200
    except Exception as e:
        models.db.session.rollback()
        log_to_db('ERROR', f"Save failed: {e}", user_id=current_username, request_path=request.path, details={'uuid': save_data.get('uuid'), 'error_type': str(type(e)), 'force_name': save_data.get('name', 'Unknown')}, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)
        models.db.session.commit()
        return jsonify({"error": "An error occurred while saving the list. Please try again later."}), 500
    
@app.route('/lists/<uuid>', methods=['GET'])
def show_forcelist(uuid):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    add_to_list = AddToList()
    response = models.SavedList.query.filter_by(uuid=uuid).filter(models.SavedList.list_status == 'saved').first()
    if not response:
        flash('The requested list is not available. It may have been deleted or is a temporary list.', 'warning')
        log_to_db('WARNING', 'List not found or unavailable', user_id=session.get('username'), request_path=request.path, details={'uuid': uuid}, ip_address=ip_address, user_agent=user_agent, list_uuid=uuid)
        return redirect(url_for('main'))
    data = json.dumps(response.pack_data())
    log_to_db('INFO', 'Force list accessed', user_id=session.get('username'), request_path=request.path, details={'uuid': uuid}, ip_address=ip_address, user_agent=user_agent, list_uuid=uuid)
    return render_template('list-edit.html', add_to_list=add_to_list, data=data)

@app.route('/lists/<uuid>/delete', methods=['POST'])
@limiter.limit("5 per minute")
def del_forcelist(uuid):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    saved_list = models.SavedList.query.get_or_404(uuid)
    saved_list_dict = models.serialize(saved_list)
    current_user = session.get("username")
    if saved_list_dict['username'] == current_user:
        try:
            if saved_list.list_status == 'deleted':
                log_to_db('INFO', 'List already deleted', user_id=current_user, request_path=request.path, details={'uuid': uuid}, ip_address=ip_address, user_agent=user_agent, list_uuid=uuid)
                return jsonify({"success": True, "redirect": f"/users/{current_user}"}), 200
            saved_list.list_status = 'deleted'
            
            usage_event = models.UsageEvent(
                event_type='list_deleted',
                user_id=current_user,
                list_uuid=uuid,
                ip_address=ip_address,
                user_agent=user_agent,
                event_details={'force_name': saved_list_dict.get('name', 'Unknown')}
            )
            models.db.session.add(usage_event)
            
            log_to_db('INFO', 'Soft deleting force list', user_id=current_user, request_path=request.path, details={'uuid': uuid, 'force_name': saved_list_dict.get('name', 'Unknown')}, ip_address=ip_address, user_agent=user_agent, list_uuid=uuid)
            
            models.db.session.commit()
            return jsonify({"success": True, "redirect": f"/users/{current_user}"}), 200
        except Exception as e:
            models.db.session.rollback()
            log_to_db('ERROR', f"Soft delete failed: {e}", user_id=current_user, request_path=request.path, details={'uuid': uuid, 'error_type': str(type(e))}, ip_address=ip_address, user_agent=user_agent, list_uuid=uuid)
            models.db.session.commit()
            return jsonify({"success": False, "error": "An error occurred while deleting the list. Please try again later."}), 500
    log_to_db('WARNING', 'Unauthorized attempt to delete list', user_id=current_user, request_path=request.path, details={'uuid': uuid}, ip_address=ip_address, user_agent=user_agent, list_uuid=uuid)
    return jsonify({"success": False, "redirect": f"/lists/{uuid}"}), 403

@app.route('/lists/pdf', methods=['POST'])
@limiter.limit("20 per hour")
def pdf_from_forcelist():
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    user_id = session.get("username", None)  # Initialize early
    try:
        cpanel_path = os.path.expanduser('~/bin/wkhtmltopdf')
        config = pdfkit.configuration(wkhtmltopdf=cpanel_path) if os.path.exists(cpanel_path) else None
        force_list_data = request.get_json()
        list_id = force_list_data.get('uuid')
        log_to_db('DEBUG', 'Received force_list_data', user_id=user_id, request_path=request.path, details={
            'uuid': list_id,
            'force_name': force_list_data.get('name', 'Unknown'),
            'unit_count': len(force_list_data.get('units', {}))
        }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)

        if not force_list_data.get('nationality', {}).get('id'):
            raise ValueError("Nationality ID is required for PDF generation")

        pdf_data = prepPdfData(force_list_data)
        log_to_db('DEBUG', 'Processed pdf_data', user_id=user_id, request_path=request.path, details={
            'force_name': pdf_data.get('name', 'Unknown'),
            'uuid': list_id
        }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)

        metadata = {
            'include_special_rules': force_list_data.get('pdfOptions', {}).get('includeSpecialRules', True),
            'include_ship_traits': force_list_data.get('pdfOptions', {}).get('includeShipTraits', True)
        }
        log_to_db('DEBUG', 'Metadata prepared', user_id=user_id, request_path=request.path, details={
            'metadata': metadata,
            'uuid': list_id
        }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)

        # Check if the list is saved
        saved_list = models.SavedList.query.filter_by(uuid=list_id, list_status='saved').first()
        if not saved_list:
            # List is unsaved; save it as a temporary list
            new_save = models.SavedList()
            # Generate a new UUID if list_id is None
            if not list_id:
                list_id = str(uuid.uuid4())
            new_save.uuid = list_id
            new_save.username = user_id
            new_save.list_status = 'pdf'

            # Transform force_list_data into the flattened format expected by save_to_db
            save_data = {
                'name': force_list_data.get('name', 'A Force Without A Name'),
                'username': user_id,
                'idcounter': force_list_data.get('idCounter', 0),
                'maxpoints': force_list_data.get('maxPoints', 150),
                'totalforcepoints': force_list_data.get('totalForcePoints', 0),
                'nationality_id': force_list_data.get('nationality', {}).get('id'),
                'faction_id': force_list_data.get('faction', {}).get('id'),
                'commander_id': force_list_data.get('commander', {}).get('id'),
                'commandernickname': force_list_data.get('commander', {}).get('nickname'),
                'commanderhorseselected': force_list_data.get('commander', {}).get('horseoption', 0),
                'commandersr1_id': 0,
                'commandersr2_id': 0,
                'forceoption_id': force_list_data.get('faction', {}).get('forceoption_id', 0),
                'unitcount': len(force_list_data.get('units', {})),
                'charactercount': len(force_list_data.get('characters', {})),
                'artillerycount': len(force_list_data.get('artillery', {})),
                'shipcount': len(force_list_data.get('ships', {})),
                'misccount': len(force_list_data.get('misc', {}))
            }

            # Add unit components
            for i, (fid, unit) in enumerate(force_list_data.get('units', {}).items(), 1):
                save_data[f'unit_{i}_id'] = unit.get('id')
                save_data[f'unit_{i}_fid'] = unit.get('f_id')
                save_data[f'unit_{i}_nickname'] = unit.get('nickname')
                save_data[f'unit_{i}_qty'] = unit.get('qty')
                save_data[f'unit_{i}_options'] = ''

            # Add character components
            for i, (fid, character) in enumerate(force_list_data.get('characters', {}).items(), 1):
                save_data[f'character_{i}_id'] = character.get('id')
                save_data[f'character_{i}_fid'] = character.get('f_id')
                save_data[f'character_{i}_nickname'] = character.get('nickname')

            # Add artillery components
            for i, (fid, artillery) in enumerate(force_list_data.get('artillery', {}).items(), 1):
                save_data[f'artillery_{i}_id'] = artillery.get('id')
                save_data[f'artillery_{i}_fid'] = artillery.get('f_id')
                save_data[f'artillery_{i}_nickname'] = artillery.get('nickname')
                save_data[f'artillery_{i}_qty'] = artillery.get('qty')
                save_data[f'artillery_{i}_options'] = ''

            # Add ship components
            for i, (fid, ship) in enumerate(force_list_data.get('ships', {}).items(), 1):
                save_data[f'ship_{i}_id'] = ship.get('id')
                save_data[f'ship_{i}_fid'] = ship.get('f_id')
                save_data[f'ship_{i}_nickname'] = ship.get('nickname')
                save_data[f'ship_{i}_upgrades'] = ''

            # Add misc components
            for i, (fid, misc) in enumerate(force_list_data.get('misc', {}).items(), 1):
                save_data[f'misc_{i}_name'] = misc.get('name')
                save_data[f'misc_{i}_details'] = misc.get('details')
                save_data[f'misc_{i}_points'] = misc.get('points')
                save_data[f'misc_{i}_qty'] = misc.get('qty')

            new_save.save_to_db(save_data)
            metadata['unsaved_list_data'] = {
                'uuid': list_id,
                'force_name': force_list_data.get('name', 'Unknown'),
                'unit_count': len(force_list_data.get('units', {}))
            }
            event_type = 'pdf_generated_unsaved'
            event_details = {'force_name': pdf_data.get('name', 'Unknown'), 'list_data': {'uuid': list_id, 'name': force_list_data.get('name', 'Unknown')}}
        else:
            # List is saved; compare with the PDF data to track changes
            saved_list_dict = saved_list.pack_data()
            log_to_db('DEBUG', 'Saved list data', user_id=user_id, request_path=request.path, details={
                'saved_list_dict': saved_list_dict,
                'uuid': list_id
            }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)
            changes = {}
            log_to_db('DEBUG', 'Comparing name', user_id=user_id, request_path=request.path, details={
                'saved_name': saved_list_dict.get('name'),
                'pdf_name': pdf_data.get('name'),
                'uuid': list_id
            }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)
            if saved_list_dict.get('name') != pdf_data.get('name'):
                changes['name'] = {'old': saved_list_dict.get('name'), 'new': pdf_data.get('name')}
            saved_maxpoints = saved_list_dict.get('maxpoints', 0)
            pdf_maxpoints = pdf_data.get('maxpoints', 0)
            log_to_db('DEBUG', 'Comparing maxpoints', user_id=user_id, request_path=request.path, details={
                'saved_maxpoints': saved_maxpoints,
                'pdf_maxpoints': pdf_maxpoints,
                'uuid': list_id
            }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)
            if saved_maxpoints != pdf_maxpoints:
                changes['maxpoints'] = {'old': saved_maxpoints, 'new': pdf_maxpoints}
            saved_totalforcepoints = saved_list_dict.get('totalforcepoints', 0)
            pdf_totalforcepoints = pdf_data.get('totalforcepoints', 0)
            log_to_db('DEBUG', 'Comparing totalforcepoints', user_id=user_id, request_path=request.path, details={
                'saved_totalforcepoints': saved_totalforcepoints,
                'pdf_totalforcepoints': pdf_totalforcepoints,
                'uuid': list_id
            }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)
            if saved_totalforcepoints != pdf_totalforcepoints:
                changes['totalforcepoints'] = {'old': saved_totalforcepoints, 'new': pdf_totalforcepoints}
            # Compare components
            saved_units = {unit['fid']: unit for unit in saved_list_dict.get('units', [])}
            pdf_units = {unit['fid']: unit for unit in pdf_data.get('units', [])}
            component_changes = {'added': [], 'removed': [], 'updated': []}
            for fid in pdf_units:
                if fid not in saved_units:
                    component_changes['added'].append({'fid': fid, 'name': pdf_units[fid].get('nickname')})
                else:
                    unit_changes = {}
                    if pdf_units[fid].get('nickname') != saved_units[fid].get('nickname'):
                        unit_changes['nickname'] = {'old': saved_units[fid].get('nickname'), 'new': pdf_units[fid].get('nickname')}
                    if pdf_units[fid].get('qty') != saved_units[fid].get('qty'):
                        unit_changes['qty'] = {'old': saved_units[fid].get('qty'), 'new': pdf_units[fid].get('qty')}
                    if unit_changes:
                        component_changes['updated'].append({'fid': fid, 'name': pdf_units[fid].get('nickname'), 'changes': unit_changes})
            for fid in saved_units:
                if fid not in pdf_units:
                    component_changes['removed'].append({'fid': fid, 'name': saved_units[fid].get('nickname')})
            log_to_db('DEBUG', 'Component changes', user_id=user_id, request_path=request.path, details={
                'component_changes': component_changes,
                'uuid': list_id
            }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)

            event_type = 'pdf_generated'
            event_details = {
                'force_name': pdf_data.get('name', 'Unknown'),
                'field_changes': changes,
                'component_changes': component_changes
            }
            log_to_db('DEBUG', 'Event details prepared', user_id=user_id, request_path=request.path, details={
                'event_details': event_details,
                'uuid': list_id
            }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)

        pdf_generation = models.PdfGeneration(
            list_uuid=list_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            meta_data=metadata,
            success=False  # Initially set to False
        )
        models.db.session.add(pdf_generation)
        log_to_db('DEBUG', 'Added pdf_generation to session', user_id=user_id, request_path=request.path, details={
            'uuid': list_id
        }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)

        # Log usage event
        usage_event = models.UsageEvent(
            event_type=event_type,
            user_id=user_id,
            list_uuid=list_id,
            ip_address=ip_address,
            user_agent=user_agent,
            event_details=event_details
        )
        models.db.session.add(usage_event)
        log_to_db('DEBUG', 'Added usage_event to session', user_id=user_id, request_path=request.path, details={
            'uuid': list_id
        }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)

        log_to_db('INFO', 'Generating PDF', user_id=user_id, request_path=request.path, details={
            'uuid': list_id,
            'force_name': pdf_data.get('name', 'Unknown'),
            'options': metadata
        }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)

        rendered = render_template('list-pdf.html', data=pdf_data)
        log_to_db('DEBUG', 'Template rendered', user_id=user_id, request_path=request.path, details={
            'uuid': list_id
        }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)
        css = "static/assets/css/list-pdf.css"
        pdf = pdfkit.from_string(
            rendered,
            False,
            configuration=config,
            options={"enable-local-file-access": "", "page-size": "Letter"},
            css=css
        )
        log_to_db('DEBUG', 'PDF generated', user_id=user_id, request_path=request.path, details={
            'uuid': list_id
        }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id)

        # Update pdf_generation success to True after successful generation
        pdf_generation.success = True
        models.db.session.commit()

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={pdf_data["name"]}.pdf'
        return response
    except Exception as e:
        models.db.session.rollback()
        log_to_db('ERROR', f"Error in pdf_from_forcelist: {e}", user_id=user_id, request_path=request.path, details={
            'uuid': list_id if 'list_id' in locals() else 'Unknown',
            'error_type': str(type(e)),
            'force_name': pdf_data.get('name', 'Unknown') if 'pdf_data' in locals() else 'Unknown'
        }, ip_address=ip_address, user_agent=user_agent, list_uuid=list_id if 'list_id' in locals() else None)
        models.db.session.commit()
        return "An error occurred while generating the PDF. Please try again later.", 500

# Global error handler for unhandled exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    user_id = session.get('username')
    log_to_db(
        'ERROR',
        f"Unhandled exception: {e}",
        user_id=user_id,
        request_path=request.path,
        details={'error_type': str(type(e)), 'error_message': str(e)},
        ip_address=ip_address,
        user_agent=user_agent,
        list_uuid=None
    )
    models.db.session.commit()
    return jsonify({"success": False, "error": "An unexpected error occurred"}), 500

@app.errorhandler(MethodNotAllowed)
def handle_method_not_allowed(e):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    user_id = session.get('username')
    log_to_db(
        'WARNING',
        f"Method not allowed: {e}",
        user_id=user_id,
        request_path=request.path,
        details={'error_type': str(type(e)), 'error_message': str(e)},
        ip_address=ip_address,
        user_agent=user_agent,
        list_uuid=None
    )
    models.db.session.commit()
    return jsonify({"success": False, "error": "Method not allowed for this endpoint"}), 405

############### FC DATA API ROUTES ###############

def pack_universal_data():
    universal_data = {
        'nationality': models.serialize(list(models.Nationality.query.all())),
        'commanderclass': models.serialize(list(models.CommanderClass.query.all())),
        'experience': models.serialize(list(models.Experience.query.all())),
        'factionunitclass': models.serialize(list(models.FactionUnitclass.query.all())),
        'commandereffect': models.serialize(list(models.CommanderEffect.query.all())),
        'commanderfaction': models.serialize(list(models.CommanderFaction.query.all())),
        'commandernationality': models.serialize(list(models.CommanderNationality.query.all())),
        'commanderspecialrule': models.serialize(list(models.CommanderSpecialrule.query.all())),
        'factioneffect': models.serialize(list(models.FactionEffect.query.all())),
        'factionupgrade': models.serialize(list(models.FactionUpgrade.query.all())),
        'factionunit': models.serialize(list(models.FactionUnit.query.all())),
        'forceoption': models.serialize(list(models.ForceOption.query.all())),
        'forcespecialrule': models.serialize(list(models.ForceSpecialrule.query.all())),
        'specialrule': models.serialize(list(models.Specialrule.query.all())),
        'unitoption': models.serialize(list(models.UnitOption.query.all())),
        'unitspecialrule': models.serialize(list(models.UnitSpecialrule.query.all())),
        'upgrade': models.serialize(list(models.Upgrade.query.all())),
        'weaponequipment': models.serialize(list(models.WeaponEquipment.query.all()))
    }
    return universal_data

@app.route('/universal')
def get_generic_data():
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    data = pack_universal_data()
    log_to_db('INFO', 'Universal data accessed', user_id=session.get('username'), request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return jsonify(data)

@app.route('/artillery')
def get_all_artillery_data():
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    all_artillery_data = {'artillery': models.serialize(list(models.Artillery.query.all()))}
    log_to_db('INFO', 'Artillery data accessed', user_id=session.get('username'), request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return jsonify(all_artillery_data)

@app.route('/characters')
def get_all_character_data():
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    all_character_data = {
        'character': models.serialize(list(models.Character.query.all())),
        'characternationality': models.serialize(list(models.CharacterNationality.query.all())),
        'characterfaction': models.serialize(list(models.CharacterFaction.query.all())),
        'characterspecialrule': models.serialize(list(models.CharacterSpecialrule.query.all())),
        'faction': models.serialize(list(models.Faction.query.all()))
    }
    log_to_db('INFO', 'Character data accessed', user_id=session.get('username'), request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return jsonify(all_character_data)

@app.route('/commanders/<id>')
def get_commander_data(id):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    response = models.Commander.query.get_or_404(id)
    data = response.pack_data()
    log_to_db('INFO', 'Commander data accessed', user_id=session.get('username'), request_path=request.path, details={'commander_id': id}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return jsonify(data)

@app.route('/factions/<id>')
def get_faction_data(id):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    response = models.Faction.query.get_or_404(id)
    data = response.pack_data()
    log_to_db('INFO', 'Faction data accessed', user_id=session.get('username'), request_path=request.path, details={'faction_id': id}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return jsonify(data)

@app.route('/misc')
def get_all_misc_data():
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    all_misc_data = {'misc': models.serialize(list(models.Misc.query.all()))}
    log_to_db('INFO', 'Misc data accessed', user_id=session.get('username'), request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return jsonify(all_misc_data)

@app.route('/nationalities')
def get_all_nationality_data():
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    all_nationality_data = {'nationality': models.serialize(list(models.Nationality.query.all()))}
    log_to_db('INFO', 'Nationality data accessed', user_id=session.get('username'), request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return jsonify(all_nationality_data)

@app.route('/nationalities/<id>')
def get_nation_data(id):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    response = models.Nationality.query.get_or_404(id)
    data = response.pack_data()
    log_to_db('INFO', 'Nationality data accessed', user_id=session.get('username'), request_path=request.path, details={'nationality_id': id}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return jsonify(data)

@app.route('/ships')
def get_all_ship_data():
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    all_ship_data = {
        'ship': models.serialize(list(models.Ship.query.all())),
        'shipspecialrule': models.serialize(list(models.ShipSpecialrule.query.all())),
        'shipupgrade': models.serialize(list(models.ShipUpgrade.query.all()))
    }
    log_to_db('INFO', 'Ship data accessed', user_id=session.get('username'), request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return jsonify(all_ship_data)

@app.route('/ships/<id>')
def get_ship_data(id):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    response = models.Ship.query.get_or_404(id)
    data = response.pack_data()
    log_to_db('INFO', 'Ship data accessed', user_id=session.get('username'), request_path=request.path, details={'ship_id': id}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return jsonify(data)

@app.route('/units')
def get_all_unit_data():
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    all_unit_data = {'unit': models.serialize(list(models.Unit.query.all()))}
    log_to_db('INFO', 'Unit data accessed', user_id=session.get('username'), request_path=request.path, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return jsonify(all_unit_data)

@app.route('/units/<id>')
def get_unit_data(id):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent')
    response = models.Unit.query.get_or_404(id)
    data = response.pack_data()
    log_to_db('INFO', 'Unit data accessed', user_id=session.get('username'), request_path=request.path, details={'unit_id': id}, ip_address=ip_address, user_agent=user_agent, list_uuid=None)
    return jsonify(data)