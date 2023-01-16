from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Artillery(db.Model):
    """Artillery."""

    __tablename__ = "commander"

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
    uifolder = db.Column(db.VARCHAR)
    sort = db.Column(db.Integer)
    wcproduct_id = db.Column(db.Integer)

    def __repr__(self):
        return f'<Artillery {self.id} {self.name}>'


class Commander(db.Model):
    """Commander."""

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

    def __repr__(self):
        return f'<Commander {self.id} {self.name} ({self.nationality.name})>'


class CommanderClass(db.Model):
    """Commander class."""

    __tablename__ = "commanderclass"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)

    def __repr__(self):
        return f'<CommanderClass {self.id} {self.name}>'


class CommanderFaction(db.Model):
    """Commander faction."""

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
    """Commander special rule."""

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
    """Experience."""

    __tablename__ = "experience"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)

    def __repr__(self):
        return f'<Experience {self.id} {self.name}>'


class Faction(db.Model):
    """Faction."""

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

    def __repr__(self):
        return f'<Faction {self.id} {self.name} ({self.nationality.name})>'


class FactionUnit(db.Model):
    """Faction unit."""

    __tablename__ = "factionunit"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    faction_id = db.Column(db.Integer, db.ForeignKey(
        'faction.id', ondelete='CASCADE'))
    factionunitclass = db.Column(db.Integer, db.ForeignKey(
        'factionunitclass.id', ondelete='CASCADE'))
    unit_id = db.Column(db.Integer, db.ForeignKey(
        'unit.id', ondelete='CASCADE'))
    details = db.Column(db.Text)

    def __repr__(self):
        return f'<FactionUnit {self.id}>'


class FactionUnitClass(db.Model):
    """Faction unit class."""

    __tablename__ = "factionunitclass"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    details = db.Column(db.Text)

    def __repr__(self):
        return f'<FactionUnitClass {self.id} {self.name} {self.details}>'


class FactionUpgrade(db.Model):
    """Faction upgrade."""

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
    """Force option."""

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
    """Force special rule."""

    __tablename__ = "forcespecialrule"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    faction_id = db.Column(db.Integer, db.ForeignKey(
        'faction.id', ondelete='CASCADE'))
    details = db.Column(db.Text)
    addsubstract = db.Column(db.Integer)

    def __repr__(self):
        return f'<ForceSpecialrule {self.id}>'


class Location(db.Model):
    """Location."""

    __tablename__ = "location"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)
    pixelloc = db.Column(db.VARCHAR)
    textalign = db.Column(db.VARCHAR)

    def __repr__(self):
        return f'<Location {self.id} {self.name}>'


class Nationality(db.Model):
    """Nationality."""

    __tablename__ = "nationality"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.VARCHAR)

    def __repr__(self):
        return f'<Nationality {self.id} {self.name}>'


class Ship(db.Model):
    """Ship."""

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
    sailsettings = db.Column(db.VARCHAR)
    traits = db.Column(db.VARCHAR)
    wcproduct_id = db.Column(db.Integer)

    upgrade = db.relationship(
        'Upgrade',
        secondary = 'shipupgrade',
        backref = 'ship'
    )    

    def __repr__(self):
        return f'<Ship {self.id} {self.name}>'


class ShipSpecialrule(db.Model):
    """Ship special rule."""

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
    """Ship upgrade."""

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
    """Special rule."""

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

    commander = db.relationship(
        'Commander',
        secondary = 'commanderspecialrule',
        backref = 'specialrule'
    )
    force = db.relationship(
        'Force',
        secondary = 'forcespecialrule',
        backref = 'specialrule'
    )
    ship = db.relationship(
        'Ship',
        secondary = 'shipspecialrule',
        backref = 'specialrule'
    )
    unit = db.relationship(
        'Unit',
        secondary = 'unitspecialrule',
        backref = 'specialrule'
    )

    def __repr__(self):
        return f'<Specialrule {self.id} {self.name}>'


class Unit(db.Model):
    """Unit."""

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

    def __repr__(self):
        return f'<Unit {self.id} {self.name}>'


class UnitOption(db.Model):
    """Unit option."""

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
    """Unit special rule."""

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
    """Unorthodox force."""

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

    def __repr__(self):
        return f'<UnorthodoxForce {self.id} {self.name}>'


class UnorthodoxOption(db.Model):
    """Unorthodox option."""

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

    def __repr__(self):
        return f'<UnorthodoxOption {self.id} {self.name}>'


class Upgrade(db.Model):
    """Upgrade."""

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

    def __repr__(self):
        return f'<Upgrade {self.id} {self.name}>'


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)