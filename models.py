from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


#################### Serialization Functions ####################
# Serialization is required for jsonification.

def serialize_one(query_object):
    """ Serializes an individual query response object by turning it into a dict. """
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


#################### MODELS ####################


class Nationality(db.Model):
    """ Nationality Model. """

    __tablename__ = "nationality"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)

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
    nickname = db.Column(db.VARCHAR)
    points = db.Column(db.Integer)
    details = db.Column(db.Text)
    nationality_id = db.Column(db.Integer, db.ForeignKey(
        'nationality.id', ondelete='SET NULL'))
    commandrange = db.Column(db.Integer)
    commandpoints = db.Column(db.Integer)
    mainweapons = db.Column(db.VARCHAR)
    sidearms = db.Column(db.VARCHAR)
    imgfile = db.Column(db.VARCHAR)
    extrainfo = db.Column(db.VARCHAR)
    wcproduct_id = db.Column(db.Integer)

    commanderclass = db.relationship('CommanderClass', backref='commander')
    nationality = db.relationship('Nationality', backref='commander')
    commanderfaction = db.relationship('CommanderFaction', backref='commander')
    commanderspecialrule = db.relationship('CommanderSpecialrule', backref='commander')
    specialrule = db.relationship(
        'Specialrule',
        secondary = 'commanderspecialrule',
        backref = 'commander'
    )
    
    def pack_data(self):
        """ Create a serialized data set for a specified Nationality's Commanders.
            Returns a dict containing lists of dicts of that
            Nationality's Commanders' data. """
        commander_data = {
            'commander': serialize(self),            
            'commanderspecialrule': serialize(list(self.commanderspecialrule)),
            'specialrule': serialize(list(self.specialrule)),
            'faction': serialize(list(self.faction))
        }
        return commander_data

    def __repr__(self):
        return f'<Commander {self.id} {self.name} ({self.nationality.name})>'


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

    nationality = db.relationship('Nationality', backref='faction')
    commanderfaction = db.relationship('CommanderFaction', backref='faction')
    factionunit = db.relationship('FactionUnit', backref='faction')
    factionupgrade = db.relationship('FactionUpgrade', backref='faction')
    forceoption = db.relationship('ForceOption', backref='faction')
    forcespecialrule = db.relationship('ForceSpecialrule', backref='faction')
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
        """ Create a serialized data set for a specified Nationality's Factions.
            Returns a dict containing lists of dicts of that
            Nationality's Factions' data. """
        
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
            Returns a dict containing lists of dicts of
            the ship's related data. """

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
        """ Create a serialized data set for a specified Nationality's Units.
            Returns a dict containing lists of dicts of that
            Nationality's Units' data. """

        unit_data = {
            'units': serialize(self),            
            'unitoption': serialize(list(self.unitoption)),
            'unitspecialrule': serialize(list(self.unitspecialrule)),
            'upgrade': serialize(list(self.upgrade)),
            'specialrule': serialize(list(self.specialrule))
        }

        return unit_data

    def __repr__(self):
        return f'<Unit {self.id} {self.name}>'


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
    details = db.Column(db.Text)
    model = db.Column(db.VARCHAR)
    points = db.Column(db.Integer)
    uifolder = db.Column(db.VARCHAR)
    sort = db.Column(db.Integer)
    wcproduct_id = db.Column(db.Integer)

    def __repr__(self):
        return f'<Character {self.id} {self.name}>'


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

    def __repr__(self):
        return f'<CommanderSpecialrule {self.id}>'


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


class Location(db.Model):
    """ Location Model. """

    __tablename__ = "location"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    pixelloc = db.Column(db.VARCHAR)
    textalign = db.Column(db.VARCHAR)

    def __repr__(self):
        return f'<Location {self.id} {self.name}>'


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


class Specialrule(db.Model):
    """ Special ule Model. """

    __tablename__ = "specialrule"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)
    onunit = db.Column(db.Integer)
    oncommander = db.Column(db.Integer)
    onship = db.Column(db.Integer)
    onfactionopt = db.Column(db.Integer)

    commanderspecialrule = db.relationship('CommanderSpecialrule', backref='specialrule')
    shipspecialrule = db.relationship('ShipSpecialrule', backref='specialrule')
    unitspecialrule = db.relationship('UnitSpecialrule', backref='specialrule')

    def __repr__(self):
        return f'<Specialrule {self.id} {self.name}>'


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


class UnorthodoxForce(db.Model):
    """ UnorthodoxForce Model. """

    __tablename__ = "unorthodoxforce"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    commander_id = db.Column(db.Integer, db.ForeignKey(
        'commander.id', ondelete='SET NULL'))
    forceoption_id = db.Column(db.Integer, db.ForeignKey(
        'forceoption.id', ondelete='SET NULL'))
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)
    addsubtract = db.Column(db.Integer)
    unit_id = db.Column(db.Integer, db.ForeignKey(
        'unit.id', ondelete='SET NULL'))
    unitclass_id = db.Column(db.Integer)

    commander = db.relationship('Commander', backref='unorthodoxforce')
    forceoption = db.relationship('ForceOption', backref='unorthodoxforce')
    unit = db.relationship('Unit', backref='unorthodoxforce')

    def __repr__(self):
        return f'<UnorthodoxForce {self.id} {self.name}>'


class UnorthodoxOption(db.Model):
    """ UnorthodoxOption Model. """

    __tablename__ = "unorthodoxoption"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    commander_id = db.Column(db.Integer, db.ForeignKey(
        'commander.id', ondelete='SET NULL'))
    forceoption_id = db.Column(db.Integer, db.ForeignKey(
        'forceoption.id', ondelete='SET NULL'))
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)
    addsubtract = db.Column(db.Integer)
    unit_id = db.Column(db.Integer, db.ForeignKey(
        'unit.id', ondelete='SET NULL'))
    unitclass_id = db.Column(db.Integer)
    unitoption_id = db.Column(db.Integer, db.ForeignKey(
        'unitoption.id', ondelete='SET NULL'))

    commander = db.relationship('Commander', backref='unorthodoxoption')
    forceoption = db.relationship('ForceOption', backref='unorthodoxoption')
    unit = db.relationship('Unit', backref='unorthodoxoption')
    unitoption = db.relationship('UnitOption', backref='unorthodoxoption')

    def __repr__(self):
        return f'<UnorthodoxOption {self.id} {self.name}>'


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


def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)