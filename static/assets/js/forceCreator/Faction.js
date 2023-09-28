class Faction {

    initialize(faction_data, nationality_name) {
        Object.assign(this, faction_data);
        this.setFactionCommanderIDs();
        this.setFactionCommanderList(nationality_name);
        this.setFactionOptions();
        this.setFactionEffects();
        this.setFactionSpecialrules();
        this.setFactionUnitIDs();
        this['forceoption_id'] = 0;
    }

    // Get a list of the chosen factions's valid commander IDs
    // and add to this object as a property.
    setFactionCommanderIDs() {
        const commanderFaction = JSON.parse(sessionStorage.getItem('commanderfaction'));
        const factionCommanderIDs = [];
        for (const cf of commanderFaction) {
            if (cf.faction_id == this.id) {
                factionCommanderIDs.push(cf.commander_id);
            }
        }
        this.commanderIDs = factionCommanderIDs;
    }

    // Get a list of the chosen faction's valid commanders 
    // and add to this object as a property.
    setFactionCommanderList(nationality_name) {
        const nationCommanderList = JSON.parse(sessionStorage.getItem(`${nationality_name}_commanders`));
        const factionCommanderList = [{'id': 0, 'name': 'Who Leads Your Force...'}];
        for (const commander of nationCommanderList) {
            if (this.commanderIDs.includes(commander.id)) {
                const newCommander = {'id': commander.id, 'name': `${commander.name} (${commander.points})`};
                factionCommanderList.push(newCommander);
            }
        this.commanderList = factionCommanderList;
        }
    }

    // Get a list of the chosen factions's valid unit IDs
    // and add to this object as a property.
    setFactionUnitIDs() {
        const factionUnit = JSON.parse(sessionStorage.getItem('factionunit'));
        const factionUnitIDs = [];
        const unitClasses = {};
        for (const fu of factionUnit) {
            if (fu.faction_id == this.id) {
                const unitID = fu.unit_id;
                const unitClass = fu.factionunitclass_id;
                factionUnitIDs.push(fu.unit_id);
                unitClasses[`${unitID}`] = unitClass;
            }
        }
        // Check in Faction/Force Options for additional Unit IDs.
        if (this.factioneffects > []) {
            for (const fe of this.factioneffects) {
                if (!factionUnitIDs.includes(fe.unit_id)) {
                    factionUnitIDs.push(fe.unit_id);
                }
            }
        }
        // Check in Commander effects for additional Unit IDs.
        if (forceList.commander) {
            if (forceList.commander.commandereffects > []) {
                for (const ce of forceList.commander.commandereffects) {
                    if (!factionUnitIDs.includes(ce.unit_id)) {
                        factionUnitIDs.push(ce.unit_id);
                    }
                }
            }
        }
        this.unitIDs = factionUnitIDs;
        this.unitClass = unitClasses;
    }

    // Get a list of the chosen faction's valid unit objects 
    // and add to this object as a property.
    async setFactionUnits() {
        if (!sessionStorage.getItem('unit')) {
            const response = await axios.get(`/units`);
            sessionStorage.setItem('unit', JSON.stringify(response.data.unit));
        }
        const units = JSON.parse(sessionStorage.getItem('unit'));
        const factionUnits = [];
        for (const u of units) {
            if (this.unitIDs.includes(u.id)) {
                const newUnit = new Unit();
                Object.assign(newUnit, u);
                factionUnits.push(newUnit);
            }
        }
        this.unitList = factionUnits;
    }

    setFactionSpecialrules() {
        const forceSpecialrule = JSON.parse(sessionStorage.getItem('forcespecialrule'));
        const factionSpecialruleList = [];
        for (const fsr of forceSpecialrule) {
            if (fsr.faction_id == this.id) {
                const newFactionSpecialrule = {};
                Object.assign(newFactionSpecialrule, fsr);
                factionSpecialruleList.push(newFactionSpecialrule);
            }
        }
        this.specialrule = factionSpecialruleList;
    }

    setFactionOptions() {
        const forceOption = JSON.parse(sessionStorage.getItem('forceoption'));
        const factionOptionList = [];
        for (const fo of forceOption) {
            if (fo.faction_id == this.id) {
                const newFactionOption = {};
                Object.assign(newFactionOption, fo);
                factionOptionList.push(newFactionOption);
            }
        }
        this.option = factionOptionList;
    }

    setFactionEffects() {
        const factioneffect = JSON.parse(sessionStorage.getItem('factioneffect'));
        const factioneffects = [];
        if ((this.option).length > 0) {
            const optionIDs = []
            for (const o of this.option) {
                optionIDs.push(o.id);
            }
            for (const fe of factioneffect) {
                if (optionIDs.includes(fe.forceoption_id) || this.id == fe.faction_id) {
                    factioneffects.push(fe);
                }
            }
        }
        else {
            for (const fe of factioneffect) {
                if (this.id == fe.faction_id) {
                    factioneffects.push(fe);
                }
            }
        }
        this.factioneffects = factioneffects;
    }
}