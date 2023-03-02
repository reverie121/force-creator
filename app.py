from flask import Flask, render_template, redirect, jsonify, session, request, json
from forms import ForceSelection, AddToList, AddUserForm, LogInForm, EditUserForm
from flask_debugtoolbar import DebugToolbarExtension
import uuid

import models
import innocuous

app = Flask(__name__)

debug = DebugToolbarExtension(app)

app.config['SECRET_KEY'] = innocuous.sk
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///bp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

models.connect_db(app)
models.db.create_all()

############### ***** ############### ROUTES ############### ***** ###############

@app.route('/')
def main():
    return redirect('/creator')

@app.route('/creator')
def show_creator():
    force_selection = ForceSelection()
    add_to_list = AddToList()
    return render_template('fc.html', force_selection=force_selection, add_to_list=add_to_list)


############### ***** ########## USER ROUTES ########## ***** ###############


@app.route('/user/new', methods=['GET','POST'])
def new_user():
    """ Show a form that when submitted will register/create a user. 
    This form should accept a username, password, email, first_name, and last_name. 
    Process the registration form by adding a new user. Then redirect to user info page. """
    form = AddUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # Returned hashed password
        user = models.Account.register(username, password)
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        models.db.session.add(user)
        models.db.session.commit()
        session["username"] = user.username  # keep logged in    
        return redirect(f'/users/{user.username}')
    else:
        return render_template('user-new.html', form=form)


@app.route('/user/login', methods=['GET','POST'])
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
            return redirect(f'/users/{user.username}')
        else:
            form.password.errors = ["* Username or Password is incorrect *"]
    return render_template('user-log-in.html', form=form)


@app.route('/user/logout')
def log_out_user():
    """ Clear any information from the session and redirect to /. """
    session.pop("username")
    return redirect('/')


@app.route('/users/<username>')
def show_secrets(username):
    """ Show information about the given user. """
    user = models.Account.query.get_or_404(username)
    return render_template('user-info.html', user=user, forcelists=user.savedlist)


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """ Remove the user from the database and delete all of their feedback. 
    Clear any user information in the session and redirect to /. """
    if session.get('username') == username:
        user = models.Account.query.get_or_404(username)
        models.db.session.delete(user)
        models.db.session.commit()
        session.pop("username")    
    return redirect('/')


@app.route('/users/<username>/edit', methods=['GET','POST'])
def edit_user(username):
    """ Show a form that when submitted will edit a user account. """
    form = EditUserForm()
    if not session['username']:
        return redirect('/user/login')
    elif session['username'] != username:
        return redirect(f'/users/{username}/login')
    elif form.validate_on_submit():
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
            return redirect(f'/users/{usr}')
        else:
            form.password.errors = ["* Password is incorrect *"]
    else:
        user = models.Account.query.get_or_404(username)
        return render_template('user-edit.html', form=form, user=user)


############### ***** ########## FC USER ROUTES ########## ***** ###############

@app.route('/lists/save', methods=['POST'])
def save_forcelist():
    """ Save a ForceList to database. """
    save_data = request.get_json()
    print(save_data)
    # Newly saved lists will not have a uuid.
    if not 'uuid' in save_data:
        new_save = models.SavedList()
        new_uuid = uuid.uuid4()

        # This will be a class method.
        new_save.uuid = str(new_uuid)
        new_save.name = save_data['name']
        new_save.maxpoints = save_data['maxpoints']
        new_save.nationality_id = save_data['nationality_id']
        new_save.faction_id = save_data['faction_id']
        if save_data['forceoption_id'] > 0:
            new_save.forceoption_id = save_data['forceoption_id']
        new_save.commander_id = save_data['commander_id']
        new_save.commandernickname = save_data['commandernickname']
        new_save.commanderhorseoption = save_data['commanderhorseoption']
        if save_data['commandersr1_id'] >= 1:        
            new_save.commandersr1_id = save_data['commandersr1_id']
        if save_data['commandersr2_id'] >= 1:
            new_save.commandersr2_id = save_data['commandersr2_id']
        new_save.idcounter = save_data['idcounter']
        new_save.artillerycount = save_data['artillerycount']
        new_save.charactercount = save_data['charactercount']
        new_save.shipcount = save_data['shipcount']
        new_save.unitcount = save_data['unitcount']
        new_save.misccount = save_data['misccount']

        models.db.session.add(new_save)
        models.db.session.commit()    

        if save_data['artillerycount'] > 0:
            for n in range(0,save_data['artillerycount']):
                new_artillery_component = models.ArtilleryComponent()
                new_artillery_component.list_uuid = str(new_uuid)
                new_artillery_component.nickname = save_data[f'artillery_{n+1}_nickname']
                new_artillery_component.fid = save_data[f'artillery_{n+1}_fid']
                new_artillery_component.artillery_id = save_data[f'artillery_{n+1}_id']
                new_artillery_component.qty = save_data[f'artillery_{n+1}_qty']
                new_artillery_component.options = save_data[f'artillery_{n+1}_options']
                models.db.session.add(new_artillery_component)
                models.db.session.commit()

        if save_data['charactercount'] > 0:
            for n in range(0,save_data['charactercount']):
                new_character_component = models.CharacterComponent()
                new_character_component.list_uuid = str(new_uuid)
                new_character_component.nickname = save_data[f'character_{n+1}_nickname']
                new_character_component.fid = save_data[f'character_{n+1}_fid']
                new_character_component.character_id = save_data[f'character_{n+1}_id']
                models.db.session.add(new_character_component)
                models.db.session.commit()

        if save_data['shipcount'] > 0:
            for n in range(0,save_data['shipcount']):
                new_ship_component = models.ShipComponent()
                new_ship_component.list_uuid = str(new_uuid)
                new_ship_component.nickname = save_data[f'ship_{n+1}_nickname']
                new_ship_component.fid = save_data[f'ship_{n+1}_fid']
                new_ship_component.ship_id = save_data[f'ship_{n+1}_id']
                new_ship_component.upgrades = save_data[f'ship_{n+1}_upgrades']
                models.db.session.add(new_ship_component)
                models.db.session.commit()

        if save_data['unitcount'] > 0:
            for n in range(0,save_data['unitcount']):
                new_unit_component = models.UnitComponent()
                new_unit_component.list_uuid = str(new_uuid)
                new_unit_component.nickname = save_data[f'unit_{n+1}_nickname']
                new_unit_component.fid = save_data[f'unit_{n+1}_fid']
                new_unit_component.unit_id = save_data[f'unit_{n+1}_id']
                new_unit_component.qty = save_data[f'unit_{n+1}_qty']
                new_unit_component.options = save_data[f'unit_{n+1}_options']
                models.db.session.add(new_unit_component)
                models.db.session.commit()

        if save_data['misccount'] > 0:
            for n in range(0,save_data['misccount']):
                new_misc_component = models.CustomComponent()
                new_misc_component.list_uuid = str(new_uuid)
                new_misc_component.name = save_data[f'misc_{n+1}_name']
                new_misc_component.fid = save_data[f'misc_{n+1}_fid']
                new_misc_component.details = save_data[f'misc_{n+1}_details']
                new_misc_component.points = save_data[f'misc_{n+1}_points']
                new_misc_component.qty = save_data[f'misc_{n+1}_qty']
                models.db.session.add(new_misc_component)
                models.db.session.commit()

    return new_save.uuid

@app.route('/lists/<uuid>', methods=['GET'])
def show_forcelist(uuid):
    """ Show a ForceList retrieved from the database. """

    force_selection = ForceSelection()
    add_to_list = AddToList()

    response = models.SavedList.query.get_or_404(uuid)
    data = json.dumps(response.pack_data())
    return render_template('fc.html', force_selection=force_selection, add_to_list=add_to_list, data=data)    

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
