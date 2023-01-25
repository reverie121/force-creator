from flask import Flask, render_template, redirect, jsonify
from forms import ForceSelection, AddToList

import models
import innocuous

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///bp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

models.connect_db(app)
models.db.create_all()

app.config['SECRET_KEY'] = innocuous.sk

######################### ROUTES #########################

@app.route('/')
def main():
    return redirect('/creator')

@app.route('/creator')
def show_creator():
    force_selection = ForceSelection(select_nation='english')
    add_to_list = AddToList(component_type='units')
    return render_template('fc.html', force_selection=force_selection, add_to_list=add_to_list)

#################### API Routes ####################

def pack_generic_data():    
    generic_data = {
        'nationality': models.serialize(list(models.Nationality.query.all())),
        'commanderclass': models.serialize(list(models.CommanderClass.query.all())),
        'experience': models.serialize(list(models.Experience.query.all())),
        'factionunitclass': models.serialize(list(models.FactionUnitclass.query.all())),
        # The following data is sent selectively with Commander, Unit, and Faction queries
        'commanderspecialrule': models.serialize(list(models.CommanderSpecialrule.query.all())),
        'factionupgrade': models.serialize(list(models.FactionUpgrade.query.all())),
        'forceoption': models.serialize(list(models.ForceOption.query.all())),
        'forcespecialrule': models.serialize(list(models.ForceSpecialrule.query.all())),
        'specialrule': models.serialize(list(models.Specialrule.query.all())),
        'unitoption': models.serialize(list(models.UnitOption.query.all())),
        'unitspecialrule': models.serialize(list(models.UnitSpecialrule.query.all())),
        'upgrade': models.serialize(list(models.Upgrade.query.all()))
    }  
    return generic_data

@app.route('/generic')
def get_generic_data():
    data = pack_generic_data()
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
        'character': models.serialize(list(models.Character.query.all()))
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
