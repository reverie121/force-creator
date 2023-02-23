from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

#################### Top Level Serialization Functions ####################
# Serialization is required for jsonification.
# These top-level functions work for all original FB-derived models.

def serialize_one(query_object):
    """ Serializes an individual query response object by turning it into a dict. """
    # TO DO: Add recursion.
    try:
        object_dict = vars(query_object)
        data = object_dict.copy()
        for key in data.keys():
            if key.startswith('_sa_'):
                data.pop(key)
    except Exception as e: print(e)
    return data

def serialize_list(query_object_list):
    """ Iterates through a list of query response objects and serializes them.
        Returns a list of dicts. """
    s_list = []
    for dict in query_object_list:
        try:
            s_dict = serialize_one(dict)
        except Exception as e: print(e)
        s_list.append(s_dict)
    return s_list

def serialize(query_response):
    """ Serializes a query response.
        Returns a dict for individual record queries.
        Returns a list of dicts for multi-record queries. """
    if type(query_response) == list:
        try:
            serialized = serialize_list(query_response)
        except Exception as e: print(e)
    else:
        try:
            serialized = serialize_one(query_response)
        except Exception as e: print(e)
    return serialized


#################### ********** ########## MODELS ########## ********** ####################

############################## User Models ##############################


class User(db.Model):
    """ User model. """

    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    @classmethod
    def register(cls, username, pwd):
        """ Register user w/hashed password & return user. """
        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")
        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8)

    @classmethod
    def authenticate(cls, username, pwd):
        """ Validate that user exists & password is correct.
        Return user if valid; else return False. """
        u = User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False
    
    def __repr__(self):
        return f'<User u: {self.username} e: {self.email} fn: {self.first_name} ln: {self.last_name}>'


############################## Force Creator Models ##############################

#################### FC Top Level Models ####################


class Nationality(db.Model):
    """ Nationality Model. """

    __tablename__ = "nationality"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    
    characternationality = db.relationship('CharacterNationality', backref='nationality')
    commandernationality = db.relationship('CommanderNationality', backref='nationality')
    commanderfaction = db.relationship(
        'CommanderFaction',
        secondary = 'faction',
        backref = 'nationality'
    )
    factionunit = db.relationship(
        'FactionUnit',
        secondary = 'faction',
        backref = 'nationality'
    )

    def pack_data(self):
        """ Create a serialized data set for a specified Nationality.
            Returns a dict containing lists of dicts of that
            Nationality's commanders, factions, and units. """
        
        nationality_data = {
            'nationality': serialize(self),
            'commander': serialize(list(self.commander)),
            'faction': serialize(list(self.faction)),
            'unit': serialize(list(self.unit)),
            'commanderfaction': serialize(list(self.commanderfaction)),
            'factionunit': serialize(list(self.factionunit))
        }

        return nationality_data

    def __repr__(self):
        return f'<Nationality {self.id} {self.name}>'


class Faction(db.Model):
    """ Faction Model. """

    __tablename__ = "faction"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)
    forcespecialrules = db.Column(db.VARCHAR)
    commandoptions = db.Column(db.VARCHAR)
    forceoptions = db.Column(db.VARCHAR)
    nationality_id = db.Column(db.Integer, db.ForeignKey(
        'nationality.id', ondelete='SET NULL'))
    maxshipdecks = db.Column(db.Integer)
    attackerrollbonus = db.Column(db.Integer)

    nationality = db.relationship('Nationality', backref='faction')
    characterfaction = db.relationship('CharacterFaction', backref='faction')
    commanderfaction = db.relationship('CommanderFaction', backref='faction')
    factionunit = db.relationship('FactionUnit', backref='faction')
    factionupgrade = db.relationship('FactionUpgrade', backref='faction')
    forceoption = db.relationship('ForceOption', backref='faction')
    forcespecialrule = db.relationship('ForceSpecialrule', backref='faction')
    factioneffect = db.relationship('FactionEffect', backref='faction')
    commander = db.relationship(
        'Commander',
        secondary = 'commanderfaction',
        backref = 'faction'
    )
    upgrade = db.relationship(
        'Upgrade',
        secondary = 'factionupgrade',
        backref = 'faction'
    )
    factionunitclass = db.relationship(
        'FactionUnitclass', 
        secondary = 'factionunit', 
        backref = 'faction'
    )

    def pack_data(self):
        """ Create a serialized data set for a specified Faction.
            Returns a dict containing lists of dicts of that Factions' data. """
        
        faction_data = {
            'faction': serialize(self),            
            'forceoption': serialize(list(self.forceoption)),
            'forcespecialrule': serialize(list(self.forcespecialrule)),
            'commander': serialize(list(self.commander)),
            'upgrade': serialize(list(self.upgrade)),
            'factionunitclass': serialize(list(self.factionunitclass))
        }

        return faction_data

    def __repr__(self):
        return f'<Faction {self.id} {self.name} ({self.nationality.name})>'


class Commander(db.Model):
    """ Commander Model. """

    __tablename__ = "commander"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    ord = db.Column(db.Integer)
    commanderclass_id = db.Column(db.Integer, db.ForeignKey(
        'commanderclass.id', ondelete='SET NULL'))
    name = db.Column(db.VARCHAR)
    points = db.Column(db.Integer)
    details = db.Column(db.Text)
    commandrange = db.Column(db.Integer)
    commandpoints = db.Column(db.Integer)
    mainweapons = db.Column(db.VARCHAR)
    sidearms = db.Column(db.VARCHAR)
    imgfile = db.Column(db.VARCHAR)
    wcproduct_id = db.Column(db.Integer)
    unorthodoxforce = db.Column(db.VARCHAR)
    horseoption = db.Column(db.Integer)

    commanderclass = db.relationship('CommanderClass', backref='commander')
    commandernationality = db.relationship('CommanderNationality', backref='commander')
    commanderfaction = db.relationship('CommanderFaction', backref='commander')
    commanderspecialrule = db.relationship('CommanderSpecialrule', backref='commander')
    nationality = db.relationship(
        'Nationality',
        secondary = 'commandernationality',
        backref = 'commander'
    )
    specialrule = db.relationship(
        'Specialrule',
        secondary = 'commanderspecialrule',
        backref = 'commander'
    )
    
    def pack_data(self):
        """ Create a serialized data set for a specified Commander.
            Returns a dict containing lists of dicts of that Commander's data. """
        commander_data = {
            'commander': serialize(self),            
            'commanderspecialrule': serialize(list(self.commanderspecialrule)),
            'specialrule': serialize(list(self.specialrule)),
            'faction': serialize(list(self.faction))
        }
        return commander_data

    def __repr__(self):
        return f'<Commander {self.id} {self.name} ({self.nationality.name})>'


#################### FC Component Level Models ####################


class Artillery(db.Model):
    """ Artillery Model. """

    __tablename__ = "artillery"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)
    model = db.Column(db.VARCHAR)
    minimumcrew = db.Column(db.Integer)
    d10 = db.Column(db.VARCHAR)
    shootbase = db.Column(db.Integer)
    reloadmarkers = db.Column(db.Integer)
    arcfire = db.Column(db.VARCHAR)
    movepenalty = db.Column(db.VARCHAR)
    points = db.Column(db.Integer)
    sort = db.Column(db.Integer)
    wcproduct_id = db.Column(db.Integer)

    def __repr__(self):
        return f'<Artillery {self.id} {self.name}>'


class Character(db.Model):
    """ Character Model. """

    __tablename__ = "character"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    points = db.Column(db.Integer)
    wcproduct_id = db.Column(db.Integer)
    charactertype = db.Column(db.Integer)
    unitrestrictions = db.Column(db.String)
    extraabilities = db.Column(db.String)
    commandpoints = db.Column(db.Integer)
    commandrange = db.Column(db.Integer)
    commandpointconditions = db.Column(db.String)
    nonatives = db.Column(db.Integer)
    certainnations = db.Column(db.Integer)
    certainfactions = db.Column(db.Integer)
    certaincommanders = db.Column(db.Integer)

    characternationality = db.relationship('CharacterNationality', backref='character')
    characterfaction = db.relationship('CharacterFaction', backref='character')
    characterspecialrule = db.relationship('CharacterSpecialrule', backref='character')
    nationality = db.relationship(
        'Nationality',
        secondary = 'characternationality',
        backref = 'character'
    )
    faction = db.relationship(
        'Faction',
        secondary = 'characterfaction',
        backref = 'character'
    )
    specialrule = db.relationship(
        'Specialrule',
        secondary = 'characterspecialrule',
        backref = 'character'
    )

    def pack_data(self):
        """ Create a serialized data set for this Character. """

        character_data = {
            'character': serialize(self),            
            'nationality': serialize(list(self.nationality)),
            'faction': serialize(list(self.faction)),
            'specialrule': serialize(list(self.specialrule))
        }

        return character_data

    def __repr__(self):
        return f'<Unit {self.id} {self.name}>'

    def __repr__(self):
        return f'<Character {self.id} {self.name}>'


class Ship(db.Model):
    """ Ship Model. """

    __tablename__ = "ship"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    model = db.Column(db.VARCHAR)
    points = db.Column(db.Integer)
    topspeed = db.Column(db.VARCHAR)
    windward = db.Column(db.VARCHAR)
    turn = db.Column(db.VARCHAR)
    draft = db.Column(db.Integer)
    size = db.Column(db.Integer)
    cannons = db.Column(db.Integer)
    cannonsdecks = db.Column(db.VARCHAR)
    swivels = db.Column(db.Integer)
    swivelsdecks = db.Column(db.VARCHAR)
    hullfortitude = db.Column(db.Integer)
    hullintegrity = db.Column(db.Integer)
    riggingfortitude = db.Column(db.Integer)
    riggingintegrity = db.Column(db.Integer)
    sailssettings = db.Column(db.VARCHAR)
    traits = db.Column(db.VARCHAR)
    wcproduct_id = db.Column(db.Integer)

    shipspecialrule = db.relationship('ShipSpecialrule', backref='ship')
    shipupgrade = db.relationship('ShipUpgrade', backref='ship')
    specialrule = db.relationship(
        'Specialrule',
        secondary = 'shipspecialrule',
        backref = 'ship'
    )

    def pack_data(self):
        """ Create a serialized data set for a Ship.
            Returns a dict containing lists of dicts of the Ship's related data. """

        ship_data = {
            'ship': serialize(self),            
            'shipspecialrule': serialize(list(self.shipspecialrule)),
            'specialrule': serialize(list(self.specialrule)),
            'shipupgrade': serialize(list(self.shipupgrade))

        }

        return ship_data

    def __repr__(self):
        return f'<Ship {self.id} {self.name}>'


class Unit(db.Model):
    """ Unit Model. """

    __tablename__ = "unit"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    points = db.Column(db.Integer)
    details = db.Column(db.Text)
    nationality_id = db.Column(db.Integer, db.ForeignKey(
        'nationality.id', ondelete='CASCADE'))
    experience_id = db.Column(db.Integer, db.ForeignKey(
        'experience.id', ondelete='CASCADE'))
    mainweapons = db.Column(db.VARCHAR)
    sidearms = db.Column(db.VARCHAR)
    fightskill = db.Column(db.Integer)
    fightsave = db.Column(db.Integer)
    shootskill = db.Column(db.Integer)
    shootsave = db.Column(db.Integer)
    resolve = db.Column(db.Integer)
    equipment = db.Column(db.VARCHAR)
    imgfile = db.Column(db.VARCHAR)
    extrainfo = db.Column(db.VARCHAR)
    wcproduct_id = db.Column(db.Integer)

    nationality = db.relationship('Nationality', backref='unit')
    experience = db.relationship('Experience', backref='unit')
    factionunit = db.relationship('FactionUnit', backref='unit')
    unitoption = db.relationship('UnitOption', backref='unit')
    unitspecialrule = db.relationship('UnitSpecialrule', backref='unit')
    upgrade = db.relationship('Upgrade', backref='unit')
    factionunitclass = db.relationship(
        'FactionUnitclass', 
        secondary = 'factionunit', 
        backref='unit'
    )
    specialrule = db.relationship(
        'Specialrule',
        secondary = 'unitspecialrule',
        backref = 'unit'
    )
    
    def pack_data(self):
        """ Create a serialized data set for a Unit.
            Returns a dict containing lists of dicts of the Unit's related data. """

        unit_data = {
            'unit': serialize(self),            
            'unitoption': serialize(list(self.unitoption)),
            'unitspecialrule': serialize(list(self.unitspecialrule)),
            'upgrade': serialize(list(self.upgrade)),
            'specialrule': serialize(list(self.specialrule))
        }

        return unit_data

    def __repr__(self):
        return f'<Unit {self.id} {self.name}>'


class Misc(db.Model):
    """ Misc Model. """

    __tablename__ = "misc"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)
    model = db.Column(db.VARCHAR)
    d10 = db.Column(db.VARCHAR)
    points = db.Column(db.Integer)
    uifolder = db.Column(db.VARCHAR)
    sort = db.Column(db.Integer)
    wcproduct_id = db.Column(db.Integer)

    def __repr__(self):
        return f'<Misc {self.id} {self.name}>'


#################### FC Supplemental Table Models ####################

class CommanderClass(db.Model):
    """ CommanderClass Model.
        Provides id names (Standard/Historic/Legendary) """

    __tablename__ = "commanderclass"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)

    def __repr__(self):
        return f'<CommanderClass {self.id} {self.name}>'

class CommanderEffect(db.Model):
    """ CommanderEffect Model.
        Effects changes to ForceList based on Commander selection."""

    __tablename__ = "commandereffect"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    commander_id = db.Column(db.Integer, db.ForeignKey(
        'commander.id', ondelete='SET NULL'))
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)
    addsubtract = db.Column(db.Integer)
    unit_id = db.Column(db.Integer, db.ForeignKey(
        'unit.id'))
    unitclass_id = db.Column(db.Integer, db.ForeignKey(
        'unitclass.id'))
    unitoption_id = db.Column(db.Integer, db.ForeignKey(
        'unitoption.id'))

    def __repr__(self):
        return f'<CommanderEffect {self.id}>'

class Experience(db.Model):
    """ Experience Model. """

    __tablename__ = "experience"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)

    def __repr__(self):
        return f'<Experience {self.id} {self.name}>'

class FactionEffect(db.Model):
    """ FactionEffect Model.
        Effects changes to ForceList based on Faction option selection."""

    __tablename__ = "factioneffect"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    forceoption_id = db.Column(db.Integer, db.ForeignKey(
        'forceoption.id', ondelete='SET NULL'))
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)
    addsubtract = db.Column(db.Integer)
    applyall = db.Column(db.Integer)
    unit_id = db.Column(db.Integer, db.ForeignKey(
        'unit.id'))
    unitclass_id = db.Column(db.Integer, db.ForeignKey(
        'unitclass.id'))
    unitoption_id = db.Column(db.Integer, db.ForeignKey(
        'unitoption.id'))
    faction_id = db.Column(db.Integer, db.ForeignKey('faction.id'))

    def __repr__(self):
        return f'<CommanderEffect {self.id}>'

class FactionUnitclass(db.Model):
    """ FactionUnitClass Model.
        Provides id names (Core/Support) """

    __tablename__ = "factionunitclass"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)

    def __repr__(self):
        return f'<FactionUnitclass {self.id} {self.name} {self.details}>'

class Specialrule(db.Model):
    """ Specialrule Model. """

    __tablename__ = "specialrule"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)

    characterspecialrule = db.relationship('CharacterSpecialrule', backref='specialrule')
    commanderspecialrule = db.relationship('CommanderSpecialrule', backref='specialrule')
    shipspecialrule = db.relationship('ShipSpecialrule', backref='specialrule')
    unitspecialrule = db.relationship('UnitSpecialrule', backref='specialrule')

    def __repr__(self):
        return f'<Specialrule {self.id} {self.name}>'

class Upgrade(db.Model):
    """ Upgrade Model. """

    __tablename__ = "upgrade"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    unit_id = db.Column(db.Integer, db.ForeignKey(
        'unit.id', ondelete='SET NULL'))
    bonustext = db.Column(db.VARCHAR)
    pointcost = db.Column(db.Integer)
    experienceupg = db.Column(db.Integer)

    factionupgrade = db.relationship('FactionUpgrade', backref='upgrade')

    def __repr__(self):
        return f'<Upgrade {self.id} {self.name}>'

#################### FC Connective Table Models ####################

class CharacterFaction(db.Model):
    """ CharacterFaction Model.
        Connects Character and Faction Models."""

    __tablename__ = "characterfaction"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    character_id = db.Column(db.Integer, db.ForeignKey(
        'character.id', ondelete='CASCADE'))
    faction_id = db.Column(db.Integer, db.ForeignKey(
        'faction.id', ondelete='CASCADE'))

    def __repr__(self):
        return f'<CharacterFaction {self.id}>'

class CharacterNationality(db.Model):
    """ CharacterNationality Model.
        Connects Character and Nationality Models."""

    __tablename__ = "characternationality"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    character_id = db.Column(db.Integer, db.ForeignKey(
        'character.id', ondelete='CASCADE'))
    nationality_id = db.Column(db.Integer, db.ForeignKey(
        'nationality.id', ondelete='CASCADE'))

    def __repr__(self):
        return f'<CharacterNationality {self.id}>'

class CharacterSpecialrule(db.Model):
    """ CharacterSpecialrule Model.
        Connects Character and Specialrule Models."""

    __tablename__ = "characterspecialrule"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    character_id = db.Column(db.Integer, db.ForeignKey(
        'character.id', ondelete='CASCADE'))
    specialrule_id = db.Column(db.Integer, db.ForeignKey(
        'specialrule.id', ondelete='CASCADE'))

    def __repr__(self):
        return f'<CharacterSpecialrule {self.id}>'

class CommanderFaction(db.Model):
    """ CommanderFaction Model.
        Connects Commander and Faction Models."""

    __tablename__ = "commanderfaction"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    commander_id = db.Column(db.Integer, db.ForeignKey(
        'commander.id', ondelete='CASCADE'))
    faction_id = db.Column(db.Integer, db.ForeignKey(
        'faction.id', ondelete='CASCADE'))

    def __repr__(self):
        return f'<CommanderFaction {self.id}>'

class CommanderNationality(db.Model):
    """ CommanderNationality Model.
        Connects Commander and Nationality Models."""

    __tablename__ = "commandernationality"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    commander_id = db.Column(db.Integer, db.ForeignKey(
        'commander.id', ondelete='CASCADE'))
    nationality_id = db.Column(db.Integer, db.ForeignKey(
        'nationality.id', ondelete='CASCADE'))
    primary_nationality = db.Column(db.Integer)

    def __repr__(self):
        return f'<CommanderNationality {self.id}>'

class CommanderSpecialrule(db.Model):
    """ CommanderSpecialRule Model.
        Connects Commander and Specialrule Models"""

    __tablename__ = "commanderspecialrule"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    commander_id = db.Column(db.Integer, db.ForeignKey(
        'commander.id', ondelete='CASCADE'))
    specialrule_id = db.Column(db.Integer, db.ForeignKey(
        'specialrule.id', ondelete='CASCADE'))
    isoption = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<CommanderSpecialrule {self.id}>'

class FactionUnit(db.Model):
    """ FactionUnit Model.
        Connects Faction and Unit Models.
        Also connects FactionUnitclass Model. """

    __tablename__ = "factionunit"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    faction_id = db.Column(db.Integer, db.ForeignKey(
        'faction.id', ondelete='CASCADE'))
    factionunitclass_id = db.Column(db.Integer, db.ForeignKey(
        'factionunitclass.id', ondelete='CASCADE'))
    unit_id = db.Column(db.Integer, db.ForeignKey(
        'unit.id', ondelete='CASCADE'))
    details = db.Column(db.Text)

    factionunitclass = db.relationship('FactionUnitclass', backref='factionunit')

    def __repr__(self):
        return f'<FactionUnit {self.id}>'

class FactionUpgrade(db.Model):
    """ FactionUpgrade Model.
        Connects Faction and Upgrade Models. """

    __tablename__ = "factionupgrade"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    faction_id = db.Column(db.Integer, db.ForeignKey(
        'faction.id', ondelete='CASCADE'))
    upgrade_id = db.Column(db.Integer, db.ForeignKey(
        'upgrade.id', ondelete='CASCADE'))

    def __repr__(self):
        return f'<FactionUpgrade {self.id} {self.name}>'

class ForceOption(db.Model):
    """ ForceOption Model.
        Provides supporting data for Faction Model. """

    __tablename__ = "forceoption"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)
    faction_id = db.Column(db.Integer, db.ForeignKey(
        'faction.id', ondelete='CASCADE'))

    def __repr__(self):
        return f'<ForceOption {self.id} {self.name}>'

class ForceSpecialrule(db.Model):
    """ ForceSpecialrule Model.
        Provides supporting data for Faction Model. """

    __tablename__ = "forcespecialrule"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    faction_id = db.Column(db.Integer, db.ForeignKey(
        'faction.id', ondelete='CASCADE'))
    details = db.Column(db.Text)
    addsubtract = db.Column(db.Integer)

    def __repr__(self):
        return f'<ForceSpecialrule {self.id}>'

class ShipSpecialrule(db.Model):
    """ ShipSpecialrule Model.
        Connects Ship and Specialrule Models. """

    __tablename__ = "shipspecialrule"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    ship_id = db.Column(db.Integer, db.ForeignKey(
        'ship.id', ondelete='CASCADE'))
    specialrule_id = db.Column(db.Integer, db.ForeignKey(
        'specialrule.id', ondelete='CASCADE'))
    namecustomadd = db.Column(db.VARCHAR)
    details = db.Column(db.Text)

    def __repr__(self):
        return f'<ShipSpecialrule {self.id}>'

class ShipUpgrade(db.Model):
    """ ShipUpgrade Model.
        Provides supporting data for Ship Model. """

    __tablename__ = "shipupgrade"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)
    ship_id = db.Column(db.Integer, db.ForeignKey(
        'ship.id', ondelete='CASCADE'))
    pointcost = db.Column(db.Integer)

    def __repr__(self):
        return f'<ShipUpgrade {self.id}>'

class UnitOption(db.Model):
    """ UnitOption Model.
        Provides supporting data for Unit Model. """

    __tablename__ = "unitoption"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)
    unit_id = db.Column(db.Integer, db.ForeignKey(
        'unit.id', ondelete='SET NULL'))
    pointcost = db.Column(db.Integer)
    perxmodels = db.Column(db.Integer)
    pointsperunit = db.Column(db.Integer)
    experienceupg = db.Column(db.Integer)
    applyall = db.Column(db.Integer)
    limited = db.Column(db.Integer)
    addsubtractweaponequipment = db.Column(db.Integer)
    weaponequipment_id = db.Column(db.Integer)

    def __repr__(self):
        return f'<UnitOption {self.id} {self.name}>'

class UnitSpecialrule(db.Model):
    """ UnitSpecialrule Model.
        Connects Unit and Specialrule Models. """

    __tablename__ = "unitspecialrule"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    unit_id = db.Column(db.Integer, db.ForeignKey(
        'unit.id', ondelete='CASCADE'))
    specialrule_id = db.Column(db.Integer, db.ForeignKey(
        'specialrule.id', ondelete='CASCADE'))
    namecustomadd = db.Column(db.VARCHAR)
    details = db.Column(db.Text)

    def __repr__(self):
        return f'<UnitSpecialrule {self.id}>'

#################### ********** ########## END of MODELS ########## ********** ####################

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)