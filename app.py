from flask import Flask, render_template, redirect, jsonify, session, request, json, make_response, url_for, flash
from forms import AddToList, AddUserForm, LogInForm, EditUserForm, ContactForm
# from flask_debugtoolbar import DebugToolbarExtension
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

app = Flask(__name__)

# Set the SECRET_KEY from config.py (loaded from .env)
app.config['SECRET_KEY'] = config.SECRET_KEY

app.debug = False
# debug = DebugToolbarExtension(app)
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# If not local, then string replace postgres to postgresql
db_conn_str = config.DATABASE_URI
if config.IS_LOCAL == 0:
    db_conn_str = db_conn_str.replace("postgres", "postgresql")

app.config['SQLALCHEMY_DATABASE_URI'] = db_conn_str
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

# Import models and db after app is configured
import models
from models import db  # Import db from models

# Connect db to app
models.connect_db(app)
# models.db.create_all()

# Initialize Flask-Migrate with app and db
migrate = Migrate(app, db)

# Logging setup
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

############### ***** ############### ROUTES ############### ***** ###############

@app.route('/')
def main():
    return redirect('/new')

@app.route('/new')
def show_creator():
    add_to_list = AddToList()
    return render_template('fc.html', add_to_list=add_to_list)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        logging.debug("Form data: %s", form.data)
        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            message = form.message.data
            recaptcha_response = form.recaptcha_response.data

            # Validate reCAPTCHA
            recaptcha_verify_url = 'https://www.google.com/recaptcha/api/siteverify'
            recaptcha_data = {
                'secret': config.RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response,
                'remoteip': request.remote_addr
            }
            recaptcha_result = requests.post(recaptcha_verify_url, data=recaptcha_data).json()
            logging.debug("reCAPTCHA result: %s", recaptcha_result)

            if not recaptcha_result.get('success'):
                flash('reCAPTCHA verification failed. Please try again.', 'error')
                return redirect(url_for('contact'))

            # Send email to yourself
            msg = MIMEText(f"Name: {name}\nEmail: {email}\nMessage: {message}")
            msg['Subject'] = 'New Contact Form Submission from ForceCreator'
            msg['From'] = config.EMAIL_ADDRESS  # Must match the authenticated email account
            msg['To'] = config.EMAIL_ADDRESS
            msg['Reply-To'] = email  # Allow replying to the user's email

            try:
                with smtplib.SMTP('mi3-ts107.a2hosting.com', 587) as server:
                    server.starttls()
                    server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
                    server.send_message(msg)
                flash('Your message has been sent successfully!', 'success')
            except Exception as e:
                flash(f'Error sending message: {str(e)}', 'danger')

            return redirect(url_for('contact'))
        else:
            # Log and display validation errors
            logging.debug("Form validation failed: %s", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {field}: {error}", 'danger')

    return render_template('contact.html', form=form, recaptcha_site_key=config.RECAPTCHA_SITE_KEY)

############### ***** ########## USER ROUTES ########## ***** ###############


@app.route('/user/new', methods=['GET', 'POST'])
def new_user():
    """ Show a form that when submitted will register/create a user. 
    This form should accept a username, password, email, first_name, and last_name. 
    Process the registration form by adding a new user. Then redirect to user info page. """
    form = AddUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        # Check for duplicate email before proceeding
        if models.Account.query.filter_by(email=email).first():
            flash('That email is already registered. Please use a different email or log in.', 'danger')
            return render_template('user-new.html', form=form)
        
        try:
            user = models.Account.register(username, password)
            user.email = email
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            models.db.session.add(user)
            models.db.session.commit()
            session["username"] = user.username  # keep logged in
            flash('User registered successfully!', 'success')
            return redirect(f'/users/{user.username}')
        except IntegrityError as e:
            models.db.session.rollback()
            flash('An error occurred. The username might already be taken. Please try a different username.', 'danger')
            logging.error(f"IntegrityError during user registration: {str(e)}")
    else:
        # Flash validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    return render_template('user-new.html', form=form)


@app.route('/user/login', methods=['GET', 'POST'])
def log_in_user():
    """ Show a form that when submitted will login a user. 
    This form should accept a username and a password. 
    Process the login form, ensuring the user is 
    authenticated and going to /secret if so. """
    form = LogInForm()
    if form.validate_on_submit():
        usr = form.username.data
        pwd = form.password.data
        # authenticate will return a user or False
        user = models.Account.authenticate(usr, pwd)
        if user:
            session["username"] = user.username  # keep logged in
            flash('Login successful!', 'success')
            return redirect(f'/users/{user.username}')
        else:
            flash("* Username or Password is incorrect *", 'danger')
    else:
        # Flash validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    return render_template('user-log-in.html', form=form)


@app.route('/user/logout')
def log_out_user():
    """ Clear any information from the session and redirect to /. """
    session.pop("username", None)  # Use None as default to avoid KeyError
    flash('You have been logged out successfully.', 'success')
    return redirect('/user/login')


@app.route('/users/<username>')
def show_secrets(username):
    """ Show information about the given user. """
    user = models.Account.query.get_or_404(username)
    savedListData = []
    for save in user.savedlist:
        savedListData.append(save.pack_data())
    jsonListData = json.dumps(savedListData)
    return render_template('user-info.html', user=user, savedlists=user.savedlist, listdata=jsonListData)


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """ Remove the user from the database and delete all of their feedback. 
    Clear any user information in the session and redirect to /. """
    if session.get('username') != username:
        flash('You are not authorized to delete this account.', 'danger')
        return redirect('/')
    user = models.Account.query.get_or_404(username)
    models.db.session.delete(user)
    models.db.session.commit()
    session.pop("username", None)  # Use None as default to avoid KeyError
    flash('Your account has been deleted successfully.', 'success')
    return redirect('/user/new')


@app.route('/users/<username>/edit', methods=['GET', 'POST'])
def edit_user(username):
    """ Show a form that when submitted will edit a user account. """
    if 'username' not in session:
        flash('Please log in to edit your account.', 'danger')
        return redirect('/user/login')
    if session['username'] != username:
        flash('You are not authorized to edit this account.', 'danger')
        return redirect(f'/users/{session["username"]}')
    
    form = EditUserForm()
    user = models.Account.query.get_or_404(username)
    
    if form.validate_on_submit():
        usr = session['username']
        pwd = form.password.data
        # authenticate will return a user or False
        user = models.Account.authenticate(usr, pwd)
        if user:
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data
            models.db.session.add(user)
            models.db.session.commit()
            flash('Account updated successfully!', 'success')
            return redirect(f'/users/{usr}')
        else:
            flash("* Password is incorrect *", 'danger')
    else:
        # Flash validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    
    return render_template('user-edit.html', form=form, user=user)

############### ***** ########## FC USER ROUTES ########## ***** ###############

@app.route('/lists/save', methods=['POST'])
def save_forcelist():
    save_data = request.get_json()
    # Corrected logging syntax: specify the log level
    logging.debug(f"Session: {session}")
    logging.debug(f"Save data: {save_data}")
    list_uuid = None

    if 'username' not in session:
        logging.debug("User not logged in, creating new save.")
        new_save = models.SavedList()
        new_uuid = uuid.uuid4()
        new_save.uuid = str(new_uuid)
        list_uuid = new_save.save_to_db(save_data)
    else:
        logging.debug("User logged in, checking conditions.")
        current_username = session["username"]
        if 'uuid' in save_data and save_data.get('username') == current_username:
            logging.debug("Updating existing save for logged-in user.")
            saved_list = models.SavedList.query.get_or_404(save_data['uuid'])
            saved_list_dict = models.serialize(saved_list)
            models.db.session.delete(saved_list)
            models.db.session.commit()
            new_save = models.SavedList()
            new_save.uuid = save_data['uuid']
            new_save.created_at = saved_list_dict['created_at']
            new_save.username = current_username
            list_uuid = new_save.save_to_db(save_data)
        else:
            logging.debug("Creating new save for logged-in user.")
            new_save = models.SavedList()
            new_uuid = uuid.uuid4()
            new_save.uuid = str(new_uuid)
            new_save.username = current_username
            list_uuid = new_save.save_to_db(save_data)

    return list_uuid

@app.route('/lists/<uuid>', methods=['GET'])
def show_forcelist(uuid):
    """ Show a ForceList retrieved from the database. """

    add_to_list = AddToList()
    response = models.SavedList.query.get_or_404(uuid)
    data = json.dumps(response.pack_data())
    return render_template('list-edit.html', add_to_list=add_to_list, data=data)    

@app.route('/lists/<uuid>/delete', methods=['GET'])
def del_forcelist(uuid):
    """ Delete a ForceList (only if user owns it). """

    saved_list = models.SavedList.query.get_or_404(uuid)
    saved_list_dict = models.serialize(saved_list)
    if saved_list_dict['username'] == session["username"]:
            models.db.session.delete(saved_list)
            models.db.session.commit()
            return redirect(f'/users/{session["username"]}')

    else:
        return redirect(f'/lists/{uuid}')

@app.route('/lists/pdf', methods=['POST'])
def pdf_from_forcelist():
    """ Creates a pdf from a posted ForceList object. """
    # Check if we're on cPanel (or remote) by looking for an environment variable or path
    cpanel_path = os.path.expanduser('~/bin/wkhtmltopdf')
    # Use configuration only if the custom path exists (remote case)
    if os.path.exists(cpanel_path):
        config = pdfkit.configuration(wkhtmltopdf=cpanel_path)
    else:
        config = None  # Local will use system PATH
    
    # Get ForceList object from post request
    force_list_data = request.get_json()
    # Remove unrequired data and reformat as needed for pdf
    pdf_data = prepPdfData(force_list_data)
    # Render HTML from the pdf template passing in the pdf data
    rendered = render_template('list-pdf.html', data=pdf_data)
    # Create a PDF from the rendered HTML
    css = "static/assets/css/list-pdf.css"
    try:
        # Pass config only if it was set (remote), otherwise use default
        if config:
            pdf = pdfkit.from_string(
                rendered, 
                False, 
                configuration=config,
                options={"enable-local-file-access": "", "page-size": "Letter"},
                css=css
            )
        else:
            pdf = pdfkit.from_string(
                rendered, 
                False, 
                options={"enable-local-file-access": "", "page-size": "Letter"},
                css=css
            )
        # Send out PDF as a response
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={pdf_data["name"]}.pdf'
        return response
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return f"Error generating PDF: {e}", 500

############### ***** ########## FC DATA API ROUTES ########## ***** ###############

def pack_universal_data():   
    universal_data = {
        'nationality': models.serialize(list(models.Nationality.query.all())),
        'commanderclass': models.serialize(list(models.CommanderClass.query.all())),
        'experience': models.serialize(list(models.Experience.query.all())),
        'factionunitclass': models.serialize(list(models.FactionUnitclass.query.all())),
        # The following data is sent selectively with Character, Commander, Unit, and Faction queries
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
    data = pack_universal_data()
    return jsonify(data)



@app.route('/artillery')
def get_all_artillery_data():
    all_artillery_data = {
        'artillery': models.serialize(list(models.Artillery.query.all()))
    }
    return jsonify(all_artillery_data)


@app.route('/characters')
def get_all_character_data():
    all_character_data = {
        'character': models.serialize(list(models.Character.query.all())),
        'characternationality': models.serialize(list(models.CharacterNationality.query.all())),
        'characterfaction': models.serialize(list(models.CharacterFaction.query.all())),
        'characterspecialrule': models.serialize(list(models.CharacterSpecialrule.query.all())),
        'faction': models.serialize(list(models.Faction.query.all()))
    }
    return jsonify(all_character_data)


@app.route('/commanders/<id>')
def get_commander_data(id):
    response = models.Commander.query.get_or_404(id)
    data = response.pack_data()
    return jsonify(data)

    
@app.route('/factions/<id>')
def get_faction_data(id):
    response = models.Faction.query.get_or_404(id)
    data = response.pack_data()
    return jsonify(data)


@app.route('/misc')
def get_all_misc_data():
    all_misc_data = {
        'misc': models.serialize(list(models.Misc.query.all()))
    }
    return jsonify(all_misc_data)


@app.route('/nationalities')
def get_all_nationality_data():
    all_nationality_data = {
        'nationality': models.serialize(list(models.Nationality.query.all()))
    }
    return jsonify(all_nationality_data)


@app.route('/nationalities/<id>')
def get_nation_data(id):
    response = models.Nationality.query.get_or_404(id)
    data = response.pack_data()
    return jsonify(data)


@app.route('/ships')
def get_all_ship_data():
    all_ship_data = {
        'ship': models.serialize(list(models.Ship.query.all())),
        'shipspecialrule': models.serialize(list(models.ShipSpecialrule.query.all())),
        'shipupgrade': models.serialize(list(models.ShipUpgrade.query.all()))
    }
    return jsonify(all_ship_data)


@app.route('/ships/<id>')
def get_ship_data(id):
    response = models.Ship.query.get_or_404(id)
    data = response.pack_data()
    return jsonify(data)


@app.route('/units')
def get_all_unit_data():
    all_unit_data = {
        'unit': models.serialize(list(models.Unit.query.all()))
    }
    return jsonify(all_unit_data)


@app.route('/units/<id>')
def get_unit_data(id):
    response = models.Unit.query.get_or_404(id)
    data = response.pack_data()
    return jsonify(data)
