from flask import Flask, render_template, redirect, jsonify, session, request, json, make_response, url_for, flash
from forms import AddToList, AddUserForm, LogInForm, EditUserForm, ContactForm
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

app.config['SECRET_KEY'] = config.SECRET_KEY
app.debug = False

db_conn_str = config.DATABASE_URI
if config.IS_LOCAL == 0:
    db_conn_str = db_conn_str.replace("postgres", "postgresql")
app.config['SQLALCHEMY_DATABASE_URI'] = db_conn_str
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

import models
from models import db

models.connect_db(app)
migrate = Migrate(app, db)

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

############### ROUTES ###############

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
            except Exception as e:
                flash(f'Error sending message: {str(e)}', 'danger')

            return redirect(url_for('contact'))
        else:
            logging.debug("Form validation failed: %s", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {field}: {error}", 'danger')
    return render_template('contact.html', form=form, recaptcha_site_key=config.RECAPTCHA_SITE_KEY)

############### USER ROUTES ###############

@app.route('/user/new', methods=['GET', 'POST'])
def new_user():
    form = AddUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
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
            session["username"] = user.username
            flash('User registered successfully!', 'success')
            return redirect(f'/users/{user.username}')
        except IntegrityError as e:
            models.db.session.rollback()
            flash('An error occurred. The username might already be taken. Please try a different username.', 'danger')
            logging.error(f"IntegrityError during user registration: {str(e)}")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    return render_template('user-new.html', form=form)

@app.route('/user/login', methods=['GET', 'POST'])
def log_in_user():
    form = LogInForm()
    if form.validate_on_submit():
        usr = form.username.data
        pwd = form.password.data
        user = models.Account.authenticate(usr, pwd)
        if user:
            session["username"] = user.username
            flash('Login successful!', 'success')
            return redirect(f'/users/{user.username}')
        else:
            flash("* Username or Password is incorrect *", 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    return render_template('user-log-in.html', form=form)

@app.route('/user/logout')
def log_out_user():
    session.pop("username", None)
    flash('You have been logged out successfully.', 'success')
    return redirect('/user/login')

@app.route('/users/<username>')
def show_secrets(username):
    user = models.Account.query.get_or_404(username)
    savedListData = [save.pack_data() for save in user.savedlist]
    jsonListData = json.dumps(savedListData)
    return render_template('user-info.html', user=user, savedlists=user.savedlist, listdata=jsonListData)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    if session.get('username') != username:
        flash('You are not authorized to delete this account.', 'danger')
        return redirect('/')
    user = models.Account.query.get_or_404(username)
    models.db.session.delete(user)
    models.db.session.commit()
    session.pop("username", None)
    flash('Your account has been deleted successfully.', 'success')
    return redirect('/user/new')

@app.route('/users/<username>/edit', methods=['GET', 'POST'])
def edit_user(username):
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
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    return render_template('user-edit.html', form=form, user=user)

############### FC USER ROUTES ###############

@app.route('/lists/save', methods=['POST'])
def save_forcelist():
    save_data = request.get_json()
    logging.debug(f"Session: {session}")
    logging.debug(f"Save data: {save_data}")
    list_uuid = None

    try:
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
                # Explicitly delete related components
                for component in saved_list.artillerycomponent:
                    models.db.session.delete(component)
                for component in saved_list.charactercomponent:
                    models.db.session.delete(component)
                for component in saved_list.shipcomponent:
                    models.db.session.delete(component)
                for component in saved_list.unitcomponent:
                    models.db.session.delete(component)
                for component in saved_list.customcomponent:
                    models.db.session.delete(component)
                saved_list_dict = models.serialize(saved_list)
                models.db.session.delete(saved_list)
                models.db.session.commit()
                # Create new save with same UUID
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
        return list_uuid, 200
    except Exception as e:
        logging.error(f"Save failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/lists/<uuid>', methods=['GET'])
def show_forcelist(uuid):
    add_to_list = AddToList()
    response = models.SavedList.query.get_or_404(uuid)
    data = json.dumps(response.pack_data())
    return render_template('list-edit.html', add_to_list=add_to_list, data=data)

@app.route('/lists/<uuid>/delete', methods=['GET'])
def del_forcelist(uuid):
    saved_list = models.SavedList.query.get_or_404(uuid)
    saved_list_dict = models.serialize(saved_list)
    if saved_list_dict['username'] == session.get("username"):
        models.db.session.delete(saved_list)
        models.db.session.commit()
        return redirect(f'/users/{session["username"]}')
    else:
        return redirect(f'/lists/{uuid}')

@app.route('/lists/pdf', methods=['POST'])
def pdf_from_forcelist():
    cpanel_path = os.path.expanduser('~/bin/wkhtmltopdf')
    config = pdfkit.configuration(wkhtmltopdf=cpanel_path) if os.path.exists(cpanel_path) else None
    
    force_list_data = request.get_json()
    pdf_data = prepPdfData(force_list_data)
    rendered = render_template('list-pdf.html', data=pdf_data)
    css = "static/assets/css/list-pdf.css"
    try:
        pdf = pdfkit.from_string(
            rendered,
            False,
            configuration=config if config else None,
            options={"enable-local-file-access": "", "page-size": "Letter"},
            css=css
        )
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={pdf_data["name"]}.pdf'
        return response
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        return f"Error generating PDF: {e}", 500

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
    data = pack_universal_data()
    return jsonify(data)

@app.route('/artillery')
def get_all_artillery_data():
    all_artillery_data = {'artillery': models.serialize(list(models.Artillery.query.all()))}
    return jsonify(all_artillery_data)

@app.route('/characters')
def get_all_character_data():
    all_character_data = {
        'character': models.serialize(list(models.Character.query.all())),
        'characternationality': models.serialize(list(models.CharacterNationality.query.all())),
        'characterfaction': models.serialize(list(models.CharacterFaction.query.all())),
        'characterspecialrule': models.serialize(list(models.CharacterSpecialrule.query.all()))
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
    all_misc_data = {'misc': models.serialize(list(models.Misc.query.all()))}
    return jsonify(all_misc_data)

@app.route('/nationalities')
def get_all_nationality_data():
    all_nationality_data = {'nationality': models.serialize(list(models.Nationality.query.all()))}
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
    all_unit_data = {'unit': models.serialize(list(models.Unit.query.all()))}
    return jsonify(all_unit_data)

@app.route('/units/<id>')
def get_unit_data(id):
    response = models.Unit.query.get_or_404(id)
    data = response.pack_data()
    return jsonify(data)