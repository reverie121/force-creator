class Commander {

    // These functions require an 'id' property thay may not be available 
    // at initialization so they cannot go in constructor.
    initialize(commander_data, nationality_name) {
        Object.assign(this, commander_data);
        this.setCommanderEffects();
        this.setCommanderFactionIDs();
        this.setCommanderFactionList(nationality_name);
        this.setCommanderSpecialruleIDs();
        this.setCommanderSpecialruleList();
        this['specialruleChosenIDs'] = [];
    }

    setCommanderEffects() {
        const commanderEffect = JSON.parse(sessionStorage.getItem('commandereffect'));
        const commandereffects = [];
        for (const ce of commanderEffect) {
            if (ce.commander_id == this.id) {
                commandereffects.push(ce);
                // If forceList has a Faction update faction.factionUnitIDs with any that need to be added.
                if (forceList.faction > []) {
                    if (!forceList.faction.unitIDs.includes(ce.unit_id)) {
                        forceList.faction.unitIDs.push(ce.unit_id);
                    }
                    forceList.faction.setFactionUnits();
                }
            }
        }
        this.commandereffects = commandereffects;
    }

    // Get a list of the chosen commander's valid faction IDs
    // and add to this object as a property.
    setCommanderFactionIDs() {
        const commanderFaction = JSON.parse(sessionStorage.getItem('commanderfaction'));
        const commanderFactionIDs = [];
        for (const cf of commanderFaction) {
            if (cf.commander_id == this.id) {
                commanderFactionIDs.push(cf.faction_id);
            }
        }
        this.factionIDs = commanderFactionIDs;
    }

    // Get a list of the chosen commander's valid factions 
    // and add to this object as a property.
    setCommanderFactionList(nationality_name) {
        const nationFactionList = JSON.parse(sessionStorage.getItem(`${nationality_name}_factions`));
        const commanderFactionList = [{'id': 0, 'name': 'Be More Specific...'}];
        for (const faction of nationFactionList) {
            if (this.factionIDs.includes(faction.id)) {
                const newFaction = {'id': faction.id, 'name': faction.name};
                commanderFactionList.push(newFaction);
            }
        }
        this.factionList = commanderFactionList;
    }
    
    // Get a list of the chosen commander's special rule IDs
    // and add to this object as a property.
    setCommanderSpecialruleIDs() {
        const commanderSpecialrule = JSON.parse(sessionStorage.getItem('commanderspecialrule'));
        const commanderSpecialruleIDs = [];
        const commanderSpecialruleChoiceIDs = [];
        for (const csr of commanderSpecialrule) {
            if (csr.commander_id == this.id) {
                if (csr.isoption == 0) {
                    commanderSpecialruleIDs.push(csr.specialrule_id);
                } else if (csr.isoption == 1) {
                    commanderSpecialruleChoiceIDs.push(csr.specialrule_id);
                }
            }
        }
        this.specialruleIDs = commanderSpecialruleIDs;
        this.specialruleChoiceIDs = commanderSpecialruleChoiceIDs;
    }

    // Get a list of the chosen commander's special rules as objects
    // and add to this object as a property.
    setCommanderSpecialruleList() {
        const specialRule = JSON.parse(sessionStorage.getItem('specialrule'));
        const commanderSpecialruleList = [];
        const commanderSpecialruleChoiceList = [];
        for (const sr of specialRule) {
            if (this.specialruleIDs.includes(sr.id)) {
                const newSpecialrule = {};
                Object.assign(newSpecialrule, sr);
                commanderSpecialruleList.push(newSpecialrule);
            } else if (this.specialruleChoiceIDs.includes(sr.id)) {
                const newSpecialrule = {};
                Object.assign(newSpecialrule, sr);
                commanderSpecialruleChoiceList.push(newSpecialrule);
            }
        }
        this.specialrule = commanderSpecialruleList;
        this.specialruleChoice = commanderSpecialruleChoiceList;
    }
}