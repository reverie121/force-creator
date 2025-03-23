from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import logging
from sqlalchemy.exc import SQLAlchemyError

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

############################## ACCOUNT (User) Models ##############################


class Account(db.Model):
    """ Account model. """

    __tablename__ = "account"

    username = db.Column(db.String(30),
        primary_key=True)
    created_at = db.Column(db.DateTime, 
        default=db.func.now())
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(75), nullable=False, unique=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

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
        u = Account.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False
    
    def __repr__(self):
        return f'<Account u: {self.username} e: {self.email} fn: {self.first_name} ln: {self.last_name}>'


############################## Force Creator Models ##############################

#################### FC Save Models ####################

class SavedList(db.Model):
    """ SavedList Model. """

    __tablename__ = "savedlist"

    uuid = db.Column(db.VARCHAR, primary_key=True)
    username = db.Column(db.VARCHAR, db.ForeignKey(
        'account.username', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, 
        default=db.func.now())
    last_modified = db.Column(db.DateTime, 
        default=db.func.now())
    username = db.Column(db.VARCHAR, db.ForeignKey(
        'account.username', ondelete='CASCADE'))

    name = db.Column(db.VARCHAR)
    maxpoints = db.Column(db.Integer)
    totalforcepoints = db.Column(db.Integer)
    nationality_id = db.Column(db.Integer, db.ForeignKey(
        'nationality.id', ondelete='SET NULL'))
    faction_id = db.Column(db.Integer, db.ForeignKey(
        'faction.id', ondelete='SET NULL'))
    forceoption_id = db.Column(db.Integer, db.ForeignKey(
        'forceoption.id', ondelete='SET NULL'))
    commander_id = db.Column(db.Integer, db.ForeignKey(
        'commander.id', ondelete='SET NULL'))
    commandernickname = db.Column(db.VARCHAR)
    commanderhorseselected = db.Column(db.Integer)
    commandersr1_id = db.Column(db.Integer, db.ForeignKey(
        'specialrule.id', ondelete='SET NULL'))
    commandersr2_id = db.Column(db.Integer, db.ForeignKey(
        'specialrule.id', ondelete='SET NULL'))
    idcounter = db.Column(db.Integer)
    artillerycount = db.Column(db.Integer)
    charactercount = db.Column(db.Integer)
    shipcount = db.Column(db.Integer)
    unitcount = db.Column(db.Integer)
    misccount = db.Column(db.Integer)

    user = db.relationship('Account', backref='savedlist')

    nationality = db.relationship('Nationality', backref='savedlist')
    faction = db.relationship('Faction', backref='savedlist')
    forceoption = db.relationship('ForceOption', backref='savedlist')
    commander = db.relationship('Commander', backref='savedlist')

    artillerycomponent = db.relationship('ArtilleryComponent', backref='savedlist')
    charactercomponent = db.relationship('CharacterComponent', backref='savedlist')
    shipcomponent = db.relationship('ShipComponent', backref='savedlist')
    unitcomponent = db.relationship('UnitComponent', backref='savedlist')
    customcomponent = db.relationship('CustomComponent', backref='savedlist')

def save_to_db(self, save_data):
    """Create a new saved file instance from save data in a single transaction."""
    try:
        # Set SavedList fields
        self.name = save_data['name']
        self.maxpoints = save_data['maxpoints']
        self.totalforcepoints = save_data['totalforcepoints']
        self.nationality_id = save_data['nationality_id']
        self.faction_id = save_data['faction_id']
        if save_data.get('forceoption_id', 0) != 0:
            self.forceoption_id = save_data['forceoption_id']
        self.commander_id = save_data['commander_id']
        self.commandernickname = save_data['commandernickname']
        self.commanderhorseselected = save_data['commanderhorseselected']
        if save_data.get('commandersr1_id', 0) >= 1:
            self.commandersr1_id = save_data['commandersr1_id']
        if save_data.get('commandersr2_id', 0) >= 1:
            self.commandersr2_id = save_data['commandersr2_id']
        self.idcounter = save_data['idcounter']
        self.artillerycount = save_data['artillerycount']
        self.charactercount = save_data['charactercount']
        self.shipcount = save_data['shipcount']
        self.unitcount = save_data['unitcount']
        self.misccount = save_data['misccount']

        # Add SavedList to session
        db.session.add(self)

        # Save artillery components
        if save_data['artillerycount'] > 0:
            for n in range(save_data['artillerycount']):
                new_artillery_component = ArtilleryComponent()
                key_prefix = f'artillery_{n+1}_'
                new_artillery_component.list_uuid = str(self.uuid)
                new_artillery_component.nickname = save_data.get(f'{key_prefix}nickname', '')
                new_artillery_component.fid = save_data.get(f'{key_prefix}fid', '')
                new_artillery_component.artillery_id = save_data.get(f'{key_prefix}id')
                new_artillery_component.qty = save_data.get(f'{key_prefix}qty', 1)
                new_artillery_component.options = save_data.get(f'{key_prefix}options', '')
                db.session.add(new_artillery_component)

        # Save character components
        if save_data['charactercount'] > 0:
            for n in range(save_data['charactercount']):
                new_character_component = CharacterComponent()
                key_prefix = f'character_{n+1}_'
                new_character_component.list_uuid = str(self.uuid)
                new_character_component.nickname = save_data.get(f'{key_prefix}nickname', '')
                new_character_component.fid = save_data.get(f'{key_prefix}fid', '')
                new_character_component.character_id = save_data.get(f'{key_prefix}id')
                db.session.add(new_character_component)

        # Save ship components
        if save_data['shipcount'] > 0:
            for n in range(save_data['shipcount']):
                new_ship_component = ShipComponent()
                key_prefix = f'ship_{n+1}_'
                new_ship_component.list_uuid = str(self.uuid)
                new_ship_component.nickname = save_data.get(f'{key_prefix}nickname', '')
                new_ship_component.fid = save_data.get(f'{key_prefix}fid', '')
                new_ship_component.ship_id = save_data.get(f'{key_prefix}id')
                new_ship_component.upgrades = save_data.get(f'{key_prefix}upgrades', '')
                db.session.add(new_ship_component)

        # Save unit components
        if save_data['unitcount'] > 0:
            for n in range(save_data['unitcount']):
                new_unit_component = UnitComponent()
                key_prefix = f'unit_{n+1}_'
                new_unit_component.list_uuid = str(self.uuid)
                new_unit_component.nickname = save_data.get(f'{key_prefix}nickname', '')
                new_unit_component.fid = save_data.get(f'{key_prefix}fid', '')
                new_unit_component.unit_id = save_data.get(f'{key_prefix}id')
                new_unit_component.qty = save_data.get(f'{key_prefix}qty', 1)
                new_unit_component.options = save_data.get(f'{key_prefix}options', '')
                db.session.add(new_unit_component)

        # Save misc/custom components
        if save_data['misccount'] > 0:
            for n in range(save_data['misccount']):
                new_misc_component = CustomComponent()
                key_prefix = f'misc_{n+1}_'
                new_misc_component.list_uuid = str(self.uuid)
                new_misc_component.name = save_data.get(f'{key_prefix}name', '')
                new_misc_component.fid = save_data.get(f'{key_prefix}fid', '')
                new_misc_component.details = save_data.get(f'{key_prefix}details', '')
                new_misc_component.points = save_data.get(f'{key_prefix}points', 0)
                new_misc_component.qty = save_data.get(f'{key_prefix}qty', 1)
                db.session.add(new_misc_component)

        # Single commit for all changes
        db.session.commit()
        logging.debug(f"Successfully saved SavedList and components for UUID: {self.uuid}")

    except KeyError as e:
        db.session.rollback()
        logging.error(f"KeyError while saving list {self.uuid}: Missing key {e}")
        raise
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error while saving list {self.uuid}: {e}")
        raise
    except Exception as e:
        db.session.rollback()
        logging.error(f"Unexpected error while saving list {self.uuid}: {e}")
        raise

    return self.uuid

def pack_data(self):
    """Create a serialized data set for a saved force list with validation."""
    saved_list_data = serialize(self)
    logging.debug(f"Serialized base SavedList: {saved_list_data}")

    # Artillery components
    if saved_list_data['artillerycount'] > 0:
        artillerycomponent = serialize(list(self.artillerycomponent))
        if len(artillerycomponent) != saved_list_data['artillerycount']:
            logging.warning(f"Artillery count mismatch for {self.uuid}: expected {saved_list_data['artillerycount']}, got {len(artillerycomponent)}")
        for index, component in enumerate(artillerycomponent):
            for k, v in component.items():
                saved_list_data[f'artillery_{index + 1}_{k}'] = v
            saved_list_data[f'artillery_{index + 1}_id'] = component.get('artillery_id')
            saved_list_data.pop(f'artillery_{index + 1}_list_uuid', None)
            saved_list_data.pop(f'artillery_{index + 1}_artillery_id', None)

    # Character components
    if saved_list_data['charactercount'] > 0:
        charactercomponent = serialize(list(self.charactercomponent))
        if len(charactercomponent) != saved_list_data['charactercount']:
            logging.warning(f"Character count mismatch for {self.uuid}: expected {saved_list_data['charactercount']}, got {len(charactercomponent)}")
        for index, component in enumerate(charactercomponent):
            for k, v in component.items():
                saved_list_data[f'character_{index + 1}_{k}'] = v
            saved_list_data[f'character_{index + 1}_id'] = component.get('character_id')
            saved_list_data.pop(f'character_{index + 1}_list_uuid', None)
            saved_list_data.pop(f'character_{index + 1}_character_id', None)

    # Ship components
    if saved_list_data['shipcount'] > 0:
        shipcomponent = serialize(list(self.shipcomponent))
        if len(shipcomponent) != saved_list_data['shipcount']:
            logging.warning(f"Ship count mismatch for {self.uuid}: expected {saved_list_data['shipcount']}, got {len(shipcomponent)}")
        for index, component in enumerate(shipcomponent):
            for k, v in component.items():
                saved_list_data[f'ship_{index + 1}_{k}'] = v
            saved_list_data[f'ship_{index + 1}_id'] = component.get('ship_id')
            saved_list_data.pop(f'ship_{index + 1}_list_uuid', None)
            saved_list_data.pop(f'ship_{index + 1}_ship_id', None)

    # Unit components
    if saved_list_data['unitcount'] > 0:
        unitcomponent = serialize(list(self.unitcomponent))
        if len(unitcomponent) != saved_list_data['unitcount']:
            logging.warning(f"Unit count mismatch for {self.uuid}: expected {saved_list_data['unitcount']}, got {len(unitcomponent)}")
        for index, component in enumerate(unitcomponent):
            for k, v in component.items():
                saved_list_data[f'unit_{index + 1}_{k}'] = v
            saved_list_data[f'unit_{index + 1}_id'] = component.get('unit_id')
            saved_list_data.pop(f'unit_{index + 1}_list_uuid', None)
            saved_list_data.pop(f'unit_{index + 1}_unit_id', None)

    # Misc/custom components
    if saved_list_data['misccount'] > 0:
        customcomponent = serialize(list(self.customcomponent))
        if len(customcomponent) != saved_list_data['misccount']:
            logging.warning(f"Misc count mismatch for {self.uuid}: expected {saved_list_data['misccount']}, got {len(customcomponent)}")
        for index, component in enumerate(customcomponent):
            for k, v in component.items():
                saved_list_data[f'misc_{index + 1}_{k}'] = v

    logging.debug(f"Final packed data for {self.uuid}: {saved_list_data}")
    return saved_list_data

def __repr__(self):
    return f'<SavedList {self.uuid} {self.name}>'

class ArtilleryComponent(db.Model):
    """ArtilleryComponent Model"""
    __tablename__ = "artillerycomponent"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    list_uuid = db.Column(db.VARCHAR, db.ForeignKey('savedlist.uuid', ondelete='CASCADE'), nullable=False, index=True)
    nickname = db.Column(db.VARCHAR, nullable=True)  # Optional nickname
    fid = db.Column(db.VARCHAR, nullable=False)  # Unique force ID, required
    artillery_id = db.Column(db.Integer, db.ForeignKey('artillery.id', ondelete='SET NULL'), nullable=False)
    options = db.Column(db.VARCHAR, nullable=True)  # Optional, e.g., comma-separated IDs
    qty = db.Column(db.Integer, nullable=False, default=1)  # Required, default to 1

    artillery = db.relationship('Artillery', backref='artillerycomponent')

    def __repr__(self):
        return f'<ArtilleryComponent id={self.id} list_uuid={self.list_uuid} artillery_id={self.artillery_id}>'

class CharacterComponent(db.Model):
    """CharacterComponent Model"""
    __tablename__ = "charactercomponent"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    list_uuid = db.Column(db.VARCHAR, db.ForeignKey('savedlist.uuid', ondelete='CASCADE'), nullable=False, index=True)
    nickname = db.Column(db.VARCHAR, nullable=True)  # Optional nickname
    fid = db.Column(db.VARCHAR, nullable=False)  # Unique force ID, required
    character_id = db.Column(db.Integer, db.ForeignKey('character.id', ondelete='SET NULL'), nullable=False)

    character = db.relationship('Character', backref='charactercomponent')

    def __repr__(self):
        return f'<CharacterComponent id={self.id} list_uuid={self.list_uuid} character_id={self.character_id}>'

class ShipComponent(db.Model):
    """ShipComponent Model"""
    __tablename__ = "shipcomponent"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    list_uuid = db.Column(db.VARCHAR, db.ForeignKey('savedlist.uuid', ondelete='CASCADE'), nullable=False, index=True)
    nickname = db.Column(db.VARCHAR, nullable=True)  # Optional nickname
    fid = db.Column(db.VARCHAR, nullable=False)  # Unique force ID, required
    ship_id = db.Column(db.Integer, db.ForeignKey('ship.id', ondelete='SET NULL'), nullable=False)
    upgrades = db.Column(db.VARCHAR, nullable=True)  # Optional, e.g., comma-separated IDs

    ship = db.relationship('Ship', backref='shipcomponent')

    def __repr__(self):
        return f'<ShipComponent id={self.id} list_uuid={self.list_uuid} ship_id={self.ship_id}>'

class UnitComponent(db.Model):
    """UnitComponent Model"""
    __tablename__ = "unitcomponent"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    list_uuid = db.Column(db.VARCHAR, db.ForeignKey('savedlist.uuid', ondelete='CASCADE'), nullable=False, index=True)
    nickname = db.Column(db.VARCHAR, nullable=True)  # Optional nickname
    fid = db.Column(db.VARCHAR, nullable=False)  # Unique force ID, required
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id', ondelete='SET NULL'), nullable=False)
    options = db.Column(db.VARCHAR, nullable=True)  # Optional, e.g., comma-separated IDs
    qty = db.Column(db.Integer, nullable=False, default=1)  # Required, default to 1

    unit = db.relationship('Unit', backref='unitcomponent')

    def __repr__(self):
        return f'<UnitComponent id={self.id} list_uuid={self.list_uuid} unit_id={self.unit_id}>'

class CustomComponent(db.Model):
    """CustomComponent Model"""
    __tablename__ = "customcomponent"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    list_uuid = db.Column(db.VARCHAR, db.ForeignKey('savedlist.uuid', ondelete='CASCADE'), nullable=False, index=True)
    fid = db.Column(db.VARCHAR, nullable=False)  # Unique force ID, required
    name = db.Column(db.VARCHAR, nullable=False)  # Required name for custom item
    details = db.Column(db.Text, nullable=True)  # Optional detailed description
    points = db.Column(db.Integer, nullable=False, default=0)  # Required, default to 0
    qty = db.Column(db.Integer, nullable=False, default=1)  # Required, default to 1

    def __repr__(self):
        return f'<CustomComponent id={self.id} list_uuid={self.list_uuid} name={self.name}>'

#################### FC Top Level Models ####################


class Nationality(db.Model):
    """ Nationality Model. """

    __tablename__ = "nationality"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)
    
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
    first_year = db.Column(db.Integer)
    last_year = db.Column(db.Integer)
    details = db.Column(db.Text)
    forcespecialrules = db.Column(db.VARCHAR)
    commandoptions = db.Column(db.VARCHAR)
    forceoptions = db.Column(db.VARCHAR)
    nationality_id = db.Column(db.Integer, db.ForeignKey(
        'nationality.id', ondelete='SET NULL'))
    maxshipdecks = db.Column(db.Integer)
    artilleryallowed = db.Column(db.Integer)
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
    source = db.relationship(
        'Source',
        secondary = 'componentsource',
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
    source = db.relationship(
        'Source',
        secondary = 'componentsource',
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
    onlywithcommander = db.Column(db.Integer)
    breaklimits = db.Column(db.Integer)
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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    commander_id = db.Column(db.Integer, db.ForeignKey('commander.id', ondelete='SET NULL'))
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)
    addsubtract = db.Column(db.Integer)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    unitclass_id = db.Column(db.Integer, db.ForeignKey('factionunitclass.id'))  # Fixed from 'unitclass.id'
    unitoption_id = db.Column(db.Integer, db.ForeignKey('unitoption.id'))

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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    forceoption_id = db.Column(db.Integer, db.ForeignKey('forceoption.id', ondelete='SET NULL'))
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)
    addsubtract = db.Column(db.Integer)
    applyall = db.Column(db.Integer)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    unitclass_id = db.Column(db.Integer, db.ForeignKey('factionunitclass.id'))  # Fixed from 'unitclass.id'
    unitoption_id = db.Column(db.Integer, db.ForeignKey('unitoption.id'))
    faction_id = db.Column(db.Integer, db.ForeignKey('faction.id'))

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

class Source(db.Model):
    """ Source Model. """

    __tablename__ = "source"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    year_of_publication = db.Column(db.Integer)
    print_url = db.Column(db.VARCHAR)
    digital_url = db.Column(db.VARCHAR)

    componentsource = db.relationship('ComponentSource', backref='source')

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

class WeaponEquipment(db.Model):
    """ WeaponEquipment Model. """

    __tablename__ = "weaponequipment"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)
    rules = db.Column(db.VARCHAR)
    pointcost = db.Column(db.Integer)
    pointsperunit = db.Column(db.Integer)

#################### FC Connective Table Models ####################

class CharacterFaction(db.Model):
    """ CharacterFaction Model.
        Connects Character and Faction Models."""

    __tablename__ = "characterfaction"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    character_id = db.Column(db.Integer, db.ForeignKey(
        'character.id', ondelete='CASCADE'), nullable=False)
    faction_id = db.Column(db.Integer, db.ForeignKey(
        'faction.id', ondelete='CASCADE'), nullable=False)

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
        'character.id', ondelete='CASCADE'), nullable=False)
    nationality_id = db.Column(db.Integer, db.ForeignKey(
        'nationality.id', ondelete='CASCADE'), nullable=False)

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
        'character.id', ondelete='CASCADE'), nullable=False)
    specialrule_id = db.Column(db.Integer, db.ForeignKey(
        'specialrule.id', ondelete='CASCADE'), nullable=False)

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
    commander_id = db.Column(db.Integer, db.ForeignKey('commander.id', ondelete='CASCADE'), nullable=False)
    nationality_id = db.Column(db.Integer, db.ForeignKey('nationality.id', ondelete='CASCADE'), nullable=False)
    primary_nationality = db.Column(db.BOOLEAN)

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

class ComponentSource(db.Model):
    """ ComponentSource Model.
        Connects Component Model to
        Faction and Commander Models. """
    
    __tablename__ = "componentsource"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    source_id = db.Column(db.Integer, db.ForeignKey(
        'source.id', ondelete='CASCADE'))
    faction_id = db.Column(db.Integer, db.ForeignKey(
        'faction.id', ondelete='CASCADE'))
    commander_id = db.Column(db.Integer, db.ForeignKey(
        'commander.id', ondelete='CASCADE'))


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
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id', ondelete='CASCADE'))
    unit_qty_req = db.Column(db.Integer)
    req_mounted_commander = db.Column(db.Integer)
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
        'ship.id', ondelete='SET NULL'))
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
        'ship.id', ondelete='SET NULL'))
    pointcost = db.Column(db.Integer)
    post1700 = db.Column(db.Integer)

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