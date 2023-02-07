const $unitSizeRangeDisplay = $('#unit-size-range-display');
const $forceName = $('#force_name');
const $pointMax = $('#point_max');
const $selectNationality = $('#select_nation');
const $selectFaction = $('#select_faction');
const $selectCommander = $('#select_commander');
const $componentSelector = $('#component_selector');

class ForceList {
    constructor(maxPoints) {
        this.maxPoints = maxPoints;
        this.updateUnitSize();
        this.name = 'A Force Without A Name';
    }

    // Update unit size range display based on this ForceList's current maximum point value.
    updateUnitSize() {
        $unitSizeRangeDisplay.html(`<i>${Math.floor(this.maxPoints / 100) + 2} to ${(Math.floor(this.maxPoints / 100) + 1)*4} models per unit</i>`);
    }
    
    // Assign a nationality object to the force list.
    setNationality(nationality) {
        this.nationality = nationality;
        this.nationality.getNationalCommanderList();
        this.nationality.getNationalFactionList();
    }

    // Assign a commander object to the force list.
    setCommander(commander) {
        this.commander = commander;    
        $('#force-commander').show('medium', 'swing');
    }

    // Assign a faction object to the force list.
    setFaction(faction) {
        this.faction = faction;
        $('#force-faction').show('medium', 'swing');
    }

    // Show force commander in build area.
    displayCommander() {
        // Empty force's commander display.
        $('#force-commander').empty()
        // Create new commander display and add to page.
        let commanderDisplay = $('<div>').addClass(['card-body bg-info', 'text-primary', 'rounded-2', 'fell']);
        let cardHeader = $('<div>').addClass(['row']);
        let nameColumn = $('<div>').addClass(['col-10']);
        let commanderName = $('<h5>').addClass(['card-title']).text(this.commander.name);     
        nameColumn.append(commanderName);
        let expandColumn = $('<div>').addClass(['col-1']);
        expandColumn.html(`
            <a href='#commander-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='commander-expand' ></i>
            </button>
        `);
        let removeColumn = $('<div>').addClass(['col-1']);
        removeColumn.html(`
            <i class='fa-solid fa-xmark text-danger' id='commander-remove'></i>
        `);
        cardHeader.append([nameColumn,expandColumn,removeColumn]);
        let cardDetails = $('<div>').addClass(['collapse']).attr('id','commander-details').html(`<hr class='border border-2 border-primary rounded-2'>`);
        let commandRow = $('<div>').addClass('row');
        let commandRange = $('<div>').addClass(['card-text', 'col-6']).html(`<b>Command Range:</b> ${this.commander.commandrange}"`);
        let commandPoints = $('<div>').addClass(['card-text', 'col-6']).html(`<b>Command Points:</b> ${this.commander.commandpoints}`);
        commandRow.append(commandRange, commandPoints);
        let mainWeapons = $('<div>').addClass(['card-text']).html('<b>Main Weapons:</b>');
        let weaponText = $('<div>').html(`${this.commander.mainweapons}`);
        mainWeapons.append(weaponText);
        cardDetails.append([commandRow, mainWeapons]);
        if (this.commander.specialrule.length > 0) {
            let specialruleCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            let specialrulesHeader = $('<div>').addClass(['row']);
            let descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mb-0'>Special Rules</h5>`);
            let specialruleExpandColumn = $('<div>').addClass(['col-1']);
            specialruleExpandColumn.html(`
                <a href='#commander-${this.id}-specialrules-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='commander-${this.id}-specialrules-expand'></i>
                </button>
            `);
            specialrulesHeader.append([descColumn, specialruleExpandColumn]);
            let specialrulessDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `commander-${this.id}-specialrules-details`)
            for (const rule of this.commander.specialrule) {
                let newRule = $('<li>').addClass('mt-1').html(`<b>${rule.name}:</b> ${rule.details}`);
                specialrulessDetails.append(newRule);
            }
            specialruleCard.append(specialrulesHeader, specialrulessDetails);
            cardDetails.append(specialruleCard);
        }
        commanderDisplay.append([cardHeader, cardDetails]);
        $('#force-commander').append(commanderDisplay);
        // Handle expanding/contracting of force's commander information.
        $('#commander-expand').on('click', () => {
            $('#commander-expand').toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        if (this.commander.specialrule.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#commander-${this.id}-specialrules-expand`).on('click', () => {
                $(`#commander-${this.id}-specialrules-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
        }
        // Handle removal of force's commander.
        $('#commander-remove').on('click', () => {
            $('#force-commander').empty().hide();
            delete this.commander;
            // If this force has a faction, re-populate commander dropdown with valid commanders.
            // Otherwise re-populate faction and commander dropdowns using the Nation's lists.
            if (this.faction) {
                populateCommanderDropdown(this.faction.commanderList)            }
            else {
                populateFactionDropdown(this.nationality.factionList);
                populateCommanderDropdown(this.nationality.commanderList);
            }
        });
    }

    // Show force faction in build area.
    displayFaction() {
        // Empty force's faction display.
        $('#force-faction').empty()
        // Create new commander display and add to page.
        let factionDisplay = $('<div>').addClass(['card-body', 'bg-info', 'text-primary', 'rounded-2', 'fell']);
        let cardHeader = $('<div>').addClass(['row']);
        let nameColumn = $('<div>').addClass(['col-10']);
        let factionName = $('<h5>').addClass(['card-title']).text(this.faction.name);    
        nameColumn.append(factionName);
        let expandColumn = $('<div>').addClass(['col-1']);
        expandColumn.html(`
            <a href='#faction-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='faction-expand' ></i>
            </button>
        `);
        let removeColumn = $('<div>').addClass(['col-1']);
        removeColumn.html(`
            <i class='fa-solid fa-xmark text-danger' id='faction-remove'></i>
        `);
        cardHeader.append([nameColumn,expandColumn,removeColumn]);
        let cardDetails = $('<div>').addClass(['collapse']).attr('id','faction-details').html(`<hr class='border border-2 border-primary rounded-2'>`);
        let details = $('<div>').addClass(['card-text']);
        if (this.faction.details) {
            details.html(`${this.faction.details}`);
        }        
        let commandOptions = $('<div>').addClass(['card-text']).html(`<b>Commander Options:</b> ${this.faction.commandoptions}`);
        cardDetails.append([details, commandOptions]);
        // If selected faction has special rules, display with a dropdown.
        if (this.faction.specialrule.length > 0) {
            let specialruleCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            let specialrulesHeader = $('<div>').addClass(['row', 'mt-2']);
            let descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mb-0'>Special Rules</h5>`);
            let specialruleExpandColumn = $('<div>').addClass(['col-1']);
            specialruleExpandColumn.html(`
                <a href='#faction-${this.id}-specialrules-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='faction-${this.id}-specialrules-expand'></i>
                </button>
            `);
            specialrulesHeader.append([descColumn, specialruleExpandColumn]);
            let specialrulessDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `faction-${this.id}-specialrules-details`)
            for (const rule of this.faction.specialrule) {
                let newRule = $('<li>').addClass('mt-1').html(`${rule.details}`);
                specialrulessDetails.append(newRule);
            }
            specialruleCard.append(specialrulesHeader, specialrulessDetails);
            cardDetails.append(specialruleCard);
        }
        // If selected faction has options, display with a dropdown.
        if (this.faction.option.length > 0) {
            let optionsCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            let factionOptionsHeader = $('<div>').addClass(['row', 'mt-2']);
            let descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mb-0'>Faction Options</h5>`);
            let optionExpandColumn = $('<div>').addClass(['col-1']);
            optionExpandColumn.html(`
                <a href='#faction-${this.id}-options-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='faction-${this.id}-options-expand'></i>
                </button>
            `);
            factionOptionsHeader.append([descColumn, optionExpandColumn]);
            let unitOptionsDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `faction-${this.id}-options-details`)
            for (const o of this.faction.option) {
                let newOption = $('<div>').addClass('mt-1').html(`<input type='checkbox' class='form-check-input' id='faction-${this.faction.id}-option-${o.id}'> <b>${o.name}</b>`);
                let optionDetails = $('<div>').html(`${o.details}`);
                newOption.append(optionDetails);
                unitOptionsDetails.append(newOption);
            }
            optionsCard.append(factionOptionsHeader, unitOptionsDetails);
            cardDetails.append(optionsCard);
        }
        factionDisplay.append([cardHeader, cardDetails]);
        $('#force-faction').append(factionDisplay);
        // Handle expanding/contracting of force's commander information.
        $('#faction-expand').on('click', () => {
            $('#faction-expand').toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        if (this.faction.option.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#faction-${this.id}-options-expand`).on('click', () => {
                $(`#faction-${this.id}-options-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });            
        }
        if (this.faction.specialrule.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#faction-${this.id}-specialrules-expand`).on('click', () => {
                $(`#faction-${this.id}-specialrules-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
        }
        // Handle removal of force's faction.
        $('#faction-remove').on('click', () => {
            $('#force-faction').empty().hide();
            delete this.faction;
            // If this force has a commander, re-populate faction dropdown with valid factions.
            // Otherwise re-populate faction and commander dropdowns using the Nation's lists.
            if (this.commander) {
                populateFactionDropdown(this.commander.factionList)            }
            else {
                populateFactionDropdown(this.nationality.factionList);
                populateCommanderDropdown(this.nationality.commanderList);
            }
        });
    }
}


class Artillery {
    constructor(item) {
        Object.assign(this, item);
    }

    display() {
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']);
        const cardBody = $('<div>').addClass(['card-body']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col-8']);
        const itemName = $('<h5>').addClass(['card-title']).text(this.name);    
        nameColumn.append(itemName);
        const pointColumn = $('<div>').addClass(['col-2']).html(`${this.points} pts`);
        const expandColumn = $('<div>').addClass(['col-1']);
        expandColumn.html(`
            <a href='#misc-${this.id}-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='misc-${this.id}-expand'></i>
            </button>
            `);
            const addColumn = $('<div>').addClass(['col-1']);
        addColumn.html(`<i class='fa-solid fa-plus'></i>`)
        cardHeader.append([nameColumn,pointColumn, expandColumn, addColumn]);
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `misc-${this.id}-details`).html(`
            <hr class='border border-2 border-primary rounded-2'>
            <div class='row'>
                <div class='col-7'>
                    <b>Dice:</b> ${this.d10}
                </div>
                <div class='col-5'>
                    <b>Crew</b>: ${this.minimumcrew}
                </div>
            </div>
            <div class='row'>
                <div class='col-7'>
                <b>Arc of Fire</b>: ${this.arcfire}
                </div>
                <div class='col-5'>
                <b>Shoot Base</b>: ${this.shootbase}
                </div>
            </div>
            <div class='row'>
                <div class='col-7'>
                <b>Movement Penalty</b>: ${this.movepenalty}
                </div>
                <div class='col-5'>
                <b>Reload Markers</b>: ${this.reloadmarkers}
                </div>
            </div>
        
        `);
        cardBody.append(cardHeader, cardDetails);
        newItem.append(cardBody);
        $('#menu-item-container').append(newItem);
        // Handle expanding/contracting of item information.
        $(`#misc-${this.id}-expand`).on('click', () => {
            $(`#misc-${this.id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
    }
}

class Character {
    constructor(item) {
        Object.assign(this, item);
    }

    display() {
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']);
        const cardBody = $('<div>').addClass(['card-body']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col-8']);
        const itemName = $('<h5>').addClass(['card-title']).text(this.name.slice(11));    
        nameColumn.append(itemName);
        const pointColumn = $('<div>').addClass(['col-2']).html(`${this.points} pts`);
        const expandColumn = $('<div>').addClass(['col-1']);
        if (this.details) {
            expandColumn.html(`
                <a href='#misc-${this.id}-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='misc-${this.id}-expand'></i>
                </button>
                `);
        }
        const addColumn = $('<div>').addClass(['col-1']);
        addColumn.html(`<i class='fa-solid fa-plus' ></i>`);
        cardHeader.append([nameColumn,pointColumn, expandColumn, addColumn]);
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `misc-${this.id}-details`).html(`<hr class='border border-2 border-primary rounded-2'>`);
        if (this.details) {
            const itemDetails = $('<div>').addClass(['card-text']).html(`${this.details}`);
            cardDetails.append(itemDetails);
        }
        cardBody.append(cardHeader, cardDetails);
        newItem.append(cardBody);
        $('#menu-item-container').append(newItem);
        // Handle expanding/contracting of item information.
        $(`#misc-${this.id}-expand`).on('click', () => {
            $(`#misc-${this.id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
    }
}

class Commander {

    // These functions require an 'id' property thay may not be available 
    // at initialization so they cannot go in constructor.
    initialize(nationality_name) {
        this.setCommanderFactionIDs();
        this.setCommanderFactionList(nationality_name);
        this.setCommanderSpecialruleIDs();
        this.setCommanderSpecialruleList();
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
        for (const csr of commanderSpecialrule) {
            if (csr.commander_id == this.id) {
                commanderSpecialruleIDs.push(csr.specialrule_id);
            }
        }
        this.specialruleIDs = commanderSpecialruleIDs;
    }

    // Get a list of the chosen commander's special rules as objects
    // and add to this object as a property.
    setCommanderSpecialruleList() {
        const specialRule = JSON.parse(sessionStorage.getItem('specialrule'));
        const commanderSpecialruleList = [];
        for (const sr of specialRule) {
            if (this.specialruleIDs.includes(sr.id)) {
                const newSpecialrule = {};
                Object.assign(newSpecialrule, sr);
                commanderSpecialruleList.push(newSpecialrule);
            }
        }
        this.specialrule = commanderSpecialruleList;
    }
}

class Faction {

    initialize(nationality_name) {
        this.setFactionCommanderIDs();
        this.setFactionCommanderList(nationality_name);
        this.setFactionSpecialrules();
        this.setFactionOptions();
        this.setFactionUnitIDs();
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
                let unitID = fu.unit_id;
                let unitClass = fu.factionunitclass_id;
                factionUnitIDs.push(fu.unit_id);
                unitClasses[`${unitID}`] = unitClass;
            }
        }
        this.unitIDs = factionUnitIDs;
        this.unitClass = unitClasses;
    }

    // Get a list of the chosen faction's valid unit objects 
    // and add to this object as a property.
    async setFactionUnits() {
        if (!sessionStorage.getItem('unit')) {
            let response = await axios.get(`/units`);
            sessionStorage.setItem('unit', JSON.stringify(response.data.unit));
        }
        let units = JSON.parse(sessionStorage.getItem('unit'));
        let factionUnits = [];
        for (const u of units) {
            if (this.unitIDs.includes(u.id)) {
                let newUnit = new Unit();
                Object.assign(newUnit, u);
                factionUnits.push(newUnit);
            }
        }
        this.unitList = factionUnits;
    }

    setFactionSpecialrules() {
        let forceSpecialrule = JSON.parse(sessionStorage.getItem('forcespecialrule'));
        let factionSpecialruleList = [];
        for (const fsr of forceSpecialrule) {
            if (fsr.faction_id == this.id) {
                let newFactionSpecialrule = {};
                Object.assign(newFactionSpecialrule, fsr);
                factionSpecialruleList.push(newFactionSpecialrule);
            }
        }
        this.specialrule = factionSpecialruleList;
    }

    setFactionOptions() {
        let forceOption = JSON.parse(sessionStorage.getItem('forceoption'));
        let factionOptionList = [];
        for (const fo of forceOption) {
            if (fo.faction_id == this.id) {
                let newFactionOption = {};
                Object.assign(newFactionOption, fo);
                factionOptionList.push(newFactionOption);
            }
        }
        this.option = factionOptionList;
    }
}

class Ship {
    constructor(item) {
        Object.assign(this, item);
        this.setShipSpecialruleIDs();
        this.setShipSpecialrules();
        this.setShipUpgrades();
    }

    setShipSpecialruleIDs() {
        const shipSpecialrule = JSON.parse(sessionStorage.getItem('shipspecialrule'));
        const shipSpecialruleIDs = [];
        for (const ssr of shipSpecialrule) {
            if (ssr.ship_id == this.id) {
                shipSpecialruleIDs.push(ssr.specialrule_id);
            }
        }
        this.specialRuleIDs = shipSpecialruleIDs;
    }

    setShipSpecialrules() {
        const specialrule = JSON.parse(sessionStorage.getItem('specialrule'));
        const specialruleList = [];
        for (const sr of specialrule) {
            if (this.specialRuleIDs.includes(sr.id)) {
                const newRule = {};
                Object.assign(newRule, sr);
                specialruleList.push(newRule);
            }
        }
        this.specialrule = specialruleList;
    }

    setShipUpgrades() {
        const shipUpgrade = JSON.parse(sessionStorage.getItem('shipupgrade'));
        const shipUpgrades = [];
        for (const su of shipUpgrade) {
            if (su.ship_id == this.id) {
                const newUpgrade = {};
                Object.assign(newUpgrade, su);
                shipUpgrades.push(newUpgrade);
            }
        }
        this.upgrade = shipUpgrades;
    }

    display() {
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']);
        const cardBody = $('<div>').addClass(['card-body']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col-8']);
        const itemName = $('<h5>').addClass(['card-title']).text(this.name);    
        nameColumn.append(itemName);
        const pointColumn = $('<div>').addClass(['col-2']).html(`${this.points} pts`);
        const expandColumn = $('<div>').addClass(['col-1']);
        expandColumn.html(`
            <a href='#ship-${this.id}-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='ship-${this.id}-expand'></i>
            </button>
            `);
        const addColumn = $('<div>').addClass(['col-1']);
        addColumn.html(`<i class='fa-solid fa-plus' ></i>`);
        cardHeader.append([nameColumn,pointColumn, expandColumn, addColumn]);
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `ship-${this.id}-details`).html(`<hr class='border border-2 border-primary rounded-2'>`);
        const leftBox = $('<div>').addClass('col-8').html(`
            <div><b>Size:</b> ${this.size}</div>
            <div><b>Draft:</b> ${this.draft}</div>
            <div><b>Speed:</b> ${this.topspeed}</div>
            <div><b>Windward:</b> ${this.windward}</div>
            <div><b>Turn:</b> ${this.turn}</div>
            <div><b>Sail Settings:</b> ${this.sailssettings}</div>
        `);
        if (this.swivels > 0 || this.cannons > 0) {
            const deckPlan = $('<div>');
            const dpHeader = $('<div>').addClass('row');
            const labelColumn = $('<div>').addClass(`col-${(7-this.size)}`)
            const headerLabel = $('<div>').html('<b>Deck</b>');
            labelColumn.append(headerLabel);
            const n_of_cols = 12 / this.size;
            const dataColumn = $('<div>').addClass(`col-${(5+this.size)}`);
            const headerColumns = $('<div>').addClass('row');
            for (let i = 0; i < this.size; i++) {
                const newColumn = $('<div>').addClass(`col-${n_of_cols}`).html(`<b>${i+1}</b>`);
                headerColumns.append(newColumn);
            }
            dataColumn.append(headerColumns);
            dpHeader.append(labelColumn, dataColumn);
            if (this.cannons > 0) {
                const gunsLabel = $('<div>').html('Guns');
                labelColumn.append(gunsLabel);
                const gunsData = $('<div>').addClass('row');
                const gunsPerDeck = this.cannonsdecks.split('/');
                for (let i = 0; i < this.size; i++) {
                    const newColumn = $('<div>').addClass(`col-${n_of_cols}`).html(`${gunsPerDeck[i]}`);
                    gunsData.append(newColumn);
                }
                dataColumn.append(gunsData);
            }
            if (this.swivels > 0) {
                const swivelsLabel = $('<div>').html('Swivels');
                labelColumn.append(swivelsLabel);
                const swivelsData = $('<div>').addClass('row');
                const swivelsPerDeck = this.swivelsdecks.split('/');
                for (let i = 0; i < this.size; i++) {
                    const newColumn = $('<div>').addClass(`col-${n_of_cols}`).html(`${swivelsPerDeck[i]}`);
                    swivelsData.append(newColumn);
                }
                dataColumn.append(swivelsData);
            }

            deckPlan.append(dpHeader);
            leftBox.append(deckPlan);
        }
        const rightBox = $('<div>').addClass('col-4');
        const hull = $('<div>').html('<b>Hull</b>');
        for (let i = 0; i < this.hullfortitude; i++) {
            const newDiv = $('<div>');
            if (i == (this.hullfortitude - 1)) {
                newDiv.append(`${this.hullfortitude - i}`);
            }
            else {
                for (let n = 0; n < this.hullintegrity; n++) {
                    newDiv.append(`${this.hullfortitude - i} `);
                }
            }
            hull.append(newDiv);
            rightBox.append(hull);
        }
        if (this.riggingfortitude > 0) {
            const rigging = $('<div>').addClass('mt-2').html('<b>Rigging</b>');
            for (let i = 0; i < this.riggingfortitude; i++) {
                const newDiv = $('<div>');
                if (i == (this.riggingfortitude - 1)) {
                    newDiv.append(`${this.riggingfortitude - i}`);
                }
                else {
                    for (let n = 0; n < this.riggingintegrity; n++) {
                        newDiv.append(`${this.riggingfortitude - i} `);
                    }
                }
                rigging.append(newDiv);
                rightBox.append(rigging);

            }
        }
        const topBox = $('<div>').addClass('row');
        topBox.append(leftBox,rightBox);
        cardDetails.append(topBox);
        if (this.specialrule.length > 0) {
            const specialrulesCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const shipSpecialrulesHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mt-1 mb-0'>Traits</h5>`);
            const specialruleExpandColumn = $('<div>').addClass(['col-1']);
            specialruleExpandColumn.html(`
                <a href='#ship-${this.id}-specialrules-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='ship-${this.id}-specialrules-expand'></i>
                </button>
            `);
            shipSpecialrulesHeader.append([descColumn, specialruleExpandColumn]);
            const shipSpecialrulesDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `ship-${this.id}-specialrules-details`)
            for (const sr of this.specialrule) {
                const newSpecialrule = $('<li>').html(`<b>${sr.name}:</b> ${sr.details}`);
                shipSpecialrulesDetails.append(newSpecialrule);
            }
            specialrulesCard.append(shipSpecialrulesHeader, shipSpecialrulesDetails);
            cardDetails.append(specialrulesCard);
        }
        if (this.upgrade.length > 0) {
            const upgradeCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const upgradeHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mt-1 mb-0'>Upgrades</h5>`);
            const upgradeExpandColumn = $('<div>').addClass(['col-1']);
            upgradeExpandColumn.html(`
                <a href='#ship-${this.id}-upgrades-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='ship-${this.id}-upgrades-expand'></i>
                </button>
            `);
            upgradeHeader.append([descColumn, upgradeExpandColumn]);
            const shipUpgradeDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `ship-${this.id}-upgrades-details`)
            for (const u of this.upgrade) {
                const newUpgrade = $('<li>').html(`<b>${u.name}</b> (${u.pointcost} pts)`);
                const upgradeDetails = $('<div>').html(`${u.details}`);
                newUpgrade.append(upgradeDetails);
                shipUpgradeDetails.append(newUpgrade);
            }
            upgradeCard.append(upgradeHeader, shipUpgradeDetails);
            cardDetails.append(upgradeCard);
        }
        cardBody.append(cardHeader, cardDetails);
        newItem.append(cardBody);
        const model = this.model.toLowerCase().replace(/\s+/g, '');
        $(`#${model}-container`).append(newItem);
        // Handle expanding/contracting of item information.
        $(`#ship-${this.id}-expand`).on('click', () => {
            $(`#ship-${this.id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        if (this.specialrule.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#ship-${this.id}-specialrules-expand`).on('click', () => {
                $(`#ship-${this.id}-specialrules-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });            
        }
        if (this.upgrade.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#ship-${this.id}-upgrades-expand`).on('click', () => {
                $(`#ship-${this.id}-upgrades-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
        }
    }
}


class Nationality {
    constructor(nationality) {
        Object.assign(this, nationality);
    }
    // Retrieve a list of a specific Nation's Commanders 
    // with id and name from session storage for dropdown.
    getNationalCommanderList() {
        console.debug(`Getting commander list from session storage for ${this.name}.`);
        const commandersData = JSON.parse(sessionStorage.getItem(`${this.name}_commanders`));
        const nationalCommanderList = [{'id': 0, 'name': 'Who Leads Your Force...'}];
        for (const commander of commandersData) {
            const newCommander = {'id': commander.id, 'name': `${commander.name} (${commander.points})`};
            nationalCommanderList.push(newCommander);
        }
        this.commanderList = nationalCommanderList;
    }
    // Retrieve a list of a specific Nation's Factions 
    // with id and name from session storage for dropdown.
    getNationalFactionList() {
        console.debug(`Getting faction list from session storage for ${this.name}.`);
        const factionsData = JSON.parse(sessionStorage.getItem(`${this.name}_factions`));
        const nationalFactionList = [{'id': 0, 'name': 'Be More Specific...'}];
        for (const faction of factionsData) {
            const newFaction = {'id': faction.id, 'name': faction.name};
            nationalFactionList.push(newFaction);
        }
        this.factionList = nationalFactionList
    }
}


class Unit {
    constructor(item) {
        Object.assign(this, item);
        this.setUnitSpecialruleIDs();
        this.setUnitSpecialrules();
        this.setUnitOptions();
    }

    setUnitSpecialruleIDs() {
        const unitSpecialrule = JSON.parse(sessionStorage.getItem('unitspecialrule'));
        const unitSpecialruleIDs = [];
        for (const usr of unitSpecialrule) {
            if (usr.unit_id == this.id) {
                unitSpecialruleIDs.push(usr.specialrule_id);
            }
        }
        this.specialRuleIDs = unitSpecialruleIDs;
    }

    setUnitSpecialrules() {
        const specialrule = JSON.parse(sessionStorage.getItem('specialrule'));
        const specialruleList = [];
        for (const sr of specialrule) {
            if (this.specialRuleIDs.includes(sr.id)) {
                const newRule = {};
                Object.assign(newRule, sr);
                specialruleList.push(newRule);
            }
        }
        this.specialrule = specialruleList;
    }

    setUnitOptions() {
        const unitOption = JSON.parse(sessionStorage.getItem('unitoption'));
        const unitOptions = [];
        for (const uo of unitOption) {
            if (uo.unit_id == this.id) {
                const newOption = {};
                Object.assign(newOption, uo);
                unitOptions.push(newOption);
            }
        }
        this.option = unitOptions;
    }

    display() {
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']);
        const cardBody = $('<div>').addClass(['card-body']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col-8']);
        const itemName = $('<h5>').addClass(['card-title']).text(this.name);    
        nameColumn.append(itemName);
        const pointColumn = $('<div>').addClass(['col-2']).html(`${this.points} pts`);
        const expandColumn = $('<div>').addClass(['col-1']);
        expandColumn.html(`
            <a href='#misc-${this.id}-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='misc-${this.id}-expand'></i>
            </button>
            `);
            const addColumn = $('<div>').addClass(['col-1']);
        addColumn.html(`<i class='fa-solid fa-plus' ></i>`);
        cardHeader.append([nameColumn,pointColumn, expandColumn, addColumn]);
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `misc-${this.id}-details`).html(`
            <hr class='border border-2 border-primary rounded-2'>
            <div class='row'>
                <div class='col-4'>
                    <b>Fight:</b> ${this.fightskill} / ${this.fightsave}
                </div>
                <div class='col-4'>
                    <b>Shoot:</b> ${this.shootskill} / ${this.shootsave}
                </div>
                <div class='col-4'>
                    <b>Resolve:</b> ${this.resolve}
                </div>
            </div>
            <div class='mt-1'>
                <b>Main Weapons</b>:
                <div class='mt-0'>${this.mainweapons}</div>
            </div>
        `);
        if (this.sidearms) {
            const sidearms = $('<div>').addClass('mt-1').html(`<b>Sidearms</b>: ${this.sidearms}`);
            cardDetails.append(sidearms);
        }
        if (this.equipment) {
            const equipment = $('<div>').addClass('mt-1').html(`<b>Equiment</b>: ${this.equipment}`);
            cardDetails.append(equipment);
        }
        if (this.option.length > 0) {
            const optionsCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const unitOptionsHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mb-0'>Unit Options</h5>`);
            const optionExpandColumn = $('<div>').addClass(['col-1']);
            optionExpandColumn.html(`
                <a href='#unit-${this.id}-options-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='unit-${this.id}-options-expand'></i>
                </button>
            `);
            unitOptionsHeader.append([descColumn, optionExpandColumn]);
            const unitOptionsDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `unit-${this.id}-options-details`)
            for (const o of this.option) {
                let newOption = $('<li>').addClass('mt-1').html(`${o.details}`);
                unitOptionsDetails.append(newOption);
            }
            optionsCard.append(unitOptionsHeader, unitOptionsDetails);
            cardDetails.append(optionsCard);
        }
        if (this.specialrule.length > 0) {
            const specialruleCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const specialrulesHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mb-0'>Special Rules</h5>`);
            const specialruleExpandColumn = $('<div>').addClass(['col-1']);
            specialruleExpandColumn.html(`
                <a href='#unit-${this.id}-specialrules-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='unit-${this.id}-specialrules-expand'></i>
                </button>
            `);
            specialrulesHeader.append([descColumn, specialruleExpandColumn]);
            const specialrulessDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `unit-${this.id}-specialrules-details`)
            for (const rule of this.specialrule) {
                const newRule = $('<li>').addClass('mt-1').html(`<b>${rule.name}:</b> ${rule.details}`);
                specialrulessDetails.append(newRule);
            }
            specialruleCard.append(specialrulesHeader, specialrulessDetails);
            cardDetails.append(specialruleCard);
        }
        cardBody.append(cardHeader, cardDetails);
        newItem.append(cardBody);
        if (!forceList.faction) {
            $('#menu-item-container').append(newItem);
        }
        else if (forceList.faction.unitClass[`${this.id}`] == 1) {
            $('#core-units').append(newItem);
        }
        else if (forceList.faction.unitClass[`${this.id}`] == 2) {
            $('#support-units').append(newItem);
        }
        // Handle expanding/contracting of item information.
        $(`#misc-${this.id}-expand`).on('click', () => {
            $(`#misc-${this.id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        if (this.option.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#unit-${this.id}-options-expand`).on('click', () => {
                $(`#unit-${this.id}-options-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });            
        }
        if (this.specialrule.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#unit-${this.id}-specialrules-expand`).on('click', () => {
                $(`#unit-${this.id}-specialrules-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
        }
        }
}


class Misc {
    constructor(item) {
        Object.assign(this, item);
    }

    display() {
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']);
        const cardBody = $('<div>').addClass(['card-body']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col-8']);
        const itemName = $('<h5>').addClass(['card-title']).text(this.name);    
        nameColumn.append(itemName);
        const pointColumn = $('<div>').addClass(['col-2']).html(`${this.points} pts`);
        const expandColumn = $('<div>').addClass(['col-1']);
        if (this.details) {
            expandColumn.html(`
                <a href='#misc-${this.id}-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='misc-${this.id}-expand'></i>
                </button>
                `);
        }
        const addColumn = $('<div>').addClass(['col-1']);
        addColumn.html(`<i class='fa-solid fa-plus' ></i>`);
        cardHeader.append([nameColumn,pointColumn, expandColumn, addColumn]);
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `misc-${this.id}-details`).html(`<hr class='border border-2 border-primary rounded-2'>`);
        if (this.details) {
            const itemDetails = $('<div>').addClass(['card-text']).html(`<b>Details:</b> ${this.details}`);
            cardDetails.append(itemDetails);
        }

        cardBody.append(cardHeader, cardDetails);
        newItem.append(cardBody);
        $('#menu-item-container').append(newItem);
        // Handle expanding/contracting of item information.
        $(`#misc-${this.id}-expand`).on('click', () => {
            $(`#misc-${this.id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
    }

}


// ************************* END of Class Definitions *************************


// Create new ForceList object to use throughout process.
const forceList = new ForceList(150);

// Make axios request for data required by all users 
// and add data to session storage.
async function requestUniversalData() {
    console.debug('Requesting universal data.');
    const response = await axios.get('/universal');
    sessionStorage.setItem('nationality', JSON.stringify(response.data.nationality));
    sessionStorage.setItem('commanderclass', JSON.stringify(response.data.commanderclass));
    sessionStorage.setItem('experience', JSON.stringify(response.data.experience));
    sessionStorage.setItem('factionunit', JSON.stringify(response.data.factionunit));
    sessionStorage.setItem('factionunitclass', JSON.stringify(response.data.factionunitclass));
    sessionStorage.setItem('commanderfaction', JSON.stringify(response.data.commanderfaction));
    sessionStorage.setItem('commanderspecialrule', JSON.stringify(response.data.commanderspecialrule));
    sessionStorage.setItem('factionupgrade', JSON.stringify(response.data.factionupgrade));
    sessionStorage.setItem('forceoption', JSON.stringify(response.data.forceoption));
    sessionStorage.setItem('forcespecialrule', JSON.stringify(response.data.forcespecialrule));
    sessionStorage.setItem('specialrule', JSON.stringify(response.data.specialrule));
    sessionStorage.setItem('unitoption', JSON.stringify(response.data.unitoption));
    sessionStorage.setItem('unitspecialrule', JSON.stringify(response.data.unitspecialrule));
    sessionStorage.setItem('upgrade', JSON.stringify(response.data.upgrade));
    return
}

// Add Nation data from axios request to session storage.
function storeFactionsAndCommanders(axiosResponse) {
    const nationality = axiosResponse.data.nationality;
    const commanders = axiosResponse.data.commander;
    const factions = axiosResponse.data.faction;
    console.debug(`Adding nation data to session storage for ${nationality.name}.`);
    sessionStorage.setItem(nationality.name,JSON.stringify(axiosResponse.data));
    sessionStorage.setItem(`${nationality.name}_commanders`,JSON.stringify(commanders));
    sessionStorage.setItem(`${nationality.name}_factions`,JSON.stringify(factions));
}

// Retrieve a Nationality list with id and name from session storage for dropdown.
function getNationData() {
    console.debug('Getting nation data from session storage.');
    const nationalityData = JSON.parse(sessionStorage.getItem('nationality'));
    const nationList = [{'id': 0, 'name': 'Who Do You Fight For...'}];
    for (const nation of nationalityData) {
        const newNation = { 'id': nation.id, 'name': nation.name };
        nationList.push(newNation);
    }
    return nationList;
}

// Empty Faction dropdown and refill with options from input variable.
function populateFactionDropdown(factionList) {
    $selectFaction.empty();
    factionList.forEach(function(e, i){
        $selectFaction.append($('<option></option>').val(e.id).text(e.name)); 
     });
}

// Empty Commander dropdown and refill with options from input variable.
function populateCommanderDropdown(commanderList) {
    $selectCommander.empty();
    commanderList.forEach(function(e, i){
        $selectCommander.append($('<option></option>').val(e.id).text(e.name)); 
     });
}


// ************************* PAGE EVENT HANDLERS *************************


// When the page has loaded request universal data if not already in session
// and populate Nation selector from stored data.
$(window).ready(async function() {
    if (sessionStorage.getItem('nationality') == null) {
        await requestUniversalData();
    }
    const nationList = getNationData();
    nationList.forEach(function(nation, i){
        if (nation.id != 7) {
            $selectNationality.append($('<option></option>').val(nation.id).text(nation.name)); 
        }
    });
    $('#force-name').text(forceList.name);
    $('#main-area').show('slow','swing');
});

// Change the Force's Title in response to user input. *****
$forceName.on('keyup', () => {
    if (!$forceName.val()) {
        $('#force-name').text('A Force Without A Name');
    } else {
        $('#force-name').text($forceName.val());
    }
    forceList.name = $forceName.val();
})

$pointMax.on('keyup', () => {
    forceList.maxPoints = $pointMax.val();
    forceList.updateUnitSize();
});

// Handle Nationality selector dropdown.
$selectNationality.on('change', async function(e) {
    // Remove the placeholder option as needed.
    if ($selectNationality[0][0].name == 'Who Do You Fight For...') {
        $selectNationality[0][0].remove();
    }
    // Get newly selected Nationality option name as a string.
    const selected_nationality = $selectNationality.children("option").filter(":selected").text();
    // If selected Nation option is not already in sesstion storage,
    // send request for data and add to session storage.
    if (sessionStorage.getItem(selected_nationality) == null) {
        const response = await axios.get(`/nationalities/${$selectNationality.val()}`);
        storeFactionsAndCommanders(response);
    }
    // Get selected Nationality data from session.
    const nationalityData = JSON.parse(sessionStorage.getItem(`${selected_nationality}`));
    // Create new Nationality instance and assign it to ForceList object.
    const forceNationality = new Nationality(nationalityData.nationality);
    forceList.setNationality(forceNationality);
    // Populate Faction and Commander dropdowns.
    populateFactionDropdown(forceList.nationality.factionList);
    populateCommanderDropdown(forceList.nationality.commanderList);
    // Show display in UI.
    $('#welcome-area').hide('fast', 'swing');
    $('#build-area').show('slow', 'swing');    
});

// Handle Commander Selector dropdown.
$selectCommander.on('change', function() {
    // Remove the placeholder option as needed.
    if ($selectCommander[0][0].name == 'Be More Specific...') {
        $selectCommander[0][0].remove();
    }
    const nationalCommanderList = JSON.parse(sessionStorage.getItem(`${forceList.nationality.name}_commanders`));
    const selectedCommander = nationalCommanderList.find(commander => commander.id == $selectCommander.val());
    let forceCommander = new Commander();
    Object.assign(forceCommander, selectedCommander);
    forceCommander.initialize(forceList.nationality.name);
    forceList.setCommander(forceCommander);
    forceList.displayCommander();
    if (!forceList.faction) {
        populateFactionDropdown(forceList.commander.factionList);
    }
});

// Handle Faction Selector dropdown.
$selectFaction.on('change', async function() {
    // Remove the placeholder option as needed.
    if ($selectFaction[0][0].name == 'Who Leads Your Force...') {
        $selectFaction[0][0].remove();
    }
    const nationalFactionList = JSON.parse(sessionStorage.getItem(`${forceList.nationality.name}_factions`));
    const selectedFaction = nationalFactionList.find(faction => faction.id == $selectFaction.val());
    let forceFaction = new Faction(forceList.nationality.name);
    Object.assign(forceFaction, selectedFaction);
    forceFaction.initialize(forceList.nationality.name);
    forceList.setFaction(forceFaction);
    await forceList.faction.setFactionUnits();
    forceList.displayFaction();
    if (!forceList.commander) {
        populateCommanderDropdown(forceList.faction.commanderList);
    }
});

// Handle menu component (artillery, characters, units, etc) dropdown.
$componentSelector.on('change', async function(e) {
    // Get string identifier for component type.
    const selected = $componentSelector.val();
    if (sessionStorage.getItem(`${selected}`) == null) {
        if (selected == 'artillery' || selected == 'misc') {
            var response = await axios.get(`/${selected}`);
        }
        else {
            var response = await axios.get(`/${selected}s`);
        }
        if (selected == 'ship') {
            sessionStorage.setItem(`shipspecialrule`, JSON.stringify(response.data['shipspecialrule']));
            sessionStorage.setItem(`shipupgrade`, JSON.stringify(response.data['shipupgrade']));
        }
        sessionStorage.setItem(`${selected}`, JSON.stringify(response.data[selected]));
    }
    if ($selectFaction.val() > 0 && selected == 'unit') {
        var componentData = forceList.faction.unitList;
    }
    else {
        var componentData = JSON.parse(sessionStorage.getItem(`${selected}`));
    }
    $('#menu').empty();
    if (selected == 'ship') {
        const canoa = $('<div>').addClass(['collapse rounded-2', 'force-selector-field','p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'canoa-container').html(`<span class='fell fs-5'>Canoa</span>`);
        const longboat = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'longboat-container').html(`<span class='fell fs-5'>Longboat</span>`);
        const piragua = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'piragua-container').html(`<span class='fell fs-5'>Piragua</span>`);
        const bark = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'bark-container').html(`<span class='fell fs-5'>Bark</span>`);
        const bermudaSloop = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'bermudasloop-container').html(`<span class='fell fs-5'>Bermuda Sloop</span>`);
        const tartana = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'tartana-container').html(`<span class='fell fs-5'>Tartana</span>`);
        const sloop = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'sloop-container').html(`<span class='fell fs-5'>Sloop</span>`);
        const corvette = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'corvette-container').html(`<span class='fell fs-5'>Corvette</span>`);
        const fluyt = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'fluyt-container').html(`<span class='fell fs-5'>Fluyt</span>`);
        const brigantine = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'brigantine-container').html(`<span class='fell fs-5'>Brigantine</span>`);
        const lightFrigate = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'lightfrigate-container').html(`<span class='fell fs-5'>Light Frigate</span>`);
        const galleon = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'galleon-container').html(`<span class='fell fs-5'>Galleon</span>`);
        const sixthRateFrigate = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', '6thratefrigate-container').html(`<span class='fell fs-5'>6th Rate Frigate</span>`);
        $('#menu').append(canoa,longboat,piragua,bark,bermudaSloop,tartana,sloop,corvette,fluyt,brigantine,lightFrigate,galleon,sixthRateFrigate);
        canoa.show('medium', 'swing');
        longboat.show('medium', 'swing');
        piragua.show('medium', 'swing');
        bark.show('medium', 'swing');
        bermudaSloop.show('medium', 'swing');
        tartana.show('medium', 'swing');
        sloop.show('medium', 'swing');
        corvette.show('medium', 'swing');
        fluyt.show('medium', 'swing');
        brigantine.show('medium', 'swing');
        lightFrigate.show('medium', 'swing');
        galleon.show('medium', 'swing');
        sixthRateFrigate.show('medium', 'swing');
    }
    else if (selected == 'unit') {
        if (forceList.faction) {
            const core = $('<div>').addClass(['collapse rounded-2', 'force-selector-field','p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'core-units').html(`<span class='fell fs-5'>Core Units</span>`);
            const support = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'support-units').html(`<span class='fell fs-5'>Support Units</span>`);
            $('#menu').append(core,support);
            core.show('medium', 'swing');
            support.show('medium', 'swing');
        }
        else {
            const allUnits = $('<div>').addClass(['collapse rounded-2', 'force-selector-field','p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'menu-item-container');
            $('#menu').append(allUnits);
            allUnits.show('medium', 'swing');
        }
    }
    else {
        const menuItemContainer = $('<div>').addClass(['collapse rounded-2', 'force-selector-field','p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'menu-item-container');
        $('#menu').append(menuItemContainer);
        menuItemContainer.show('medium', 'swing');
    }
    for (const item of componentData) {
        if (selected == 'artillery') {
            var menuItem = new Artillery(item);
        }
        else if (selected == 'character') {
            var menuItem = new Character(item);
        }
        else if (selected == 'ship') {
            var menuItem = new Ship(item);
        }
        else if (selected == 'unit') {
            var menuItem = new Unit(item);
        }
        else if (selected == 'misc') {
            var menuItem = new Misc(item);
        }
        menuItem.display();
    }
});