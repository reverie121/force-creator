class Character {
    constructor(item) {
        Object.assign(this, item);
        this.setCharacterNationalityIDs();
        this.setCharacterNationalityList();
        this.setCharacterFactionIDs();
        this.setCharacterFactionList();
        this.setCharacterSpecialruleIDs();
        this.setCharacterSpecialruleList();
        this.nickname = this.name
    }

    // Get a list of the character's valid Nationality IDs
    // and add to this object as a property.
    setCharacterNationalityIDs() {
        const characterNationality = JSON.parse(sessionStorage.getItem('characternationality'));
        const characterNationalityIDs = [];
        for (const cf of characterNationality) {
            if (cf.character_id == this.id) {
                characterNationalityIDs.push(cf.nationality_id);
            }
        }
        this.nationalityIDs = characterNationalityIDs;
    }

    // Get a list of the chosen characters's valid Nationalities
    // and add to this object as a property.
    setCharacterNationalityList() {
        const nationalityList = JSON.parse(sessionStorage.getItem(`nationality`));
        const characterNationalityList = [];
        for (const nationality of nationalityList) {
            if (this.nationalityIDs.includes(nationality.id)) {
                const newNationality = {'id': nationality.id, 'name': nationality.name};
                characterNationalityList.push(newNationality);
            }
        }
        this.nationalityList = characterNationalityList;
    }

    // Get a list of the character's valid faction IDs
    // and add to this object as a property.
    setCharacterFactionIDs() {
        const characterFaction = JSON.parse(sessionStorage.getItem('characterfaction'));
        const characterFactionIDs = [];
        for (const cf of characterFaction) {
            if (cf.character_id == this.id) {
                characterFactionIDs.push(cf.faction_id);
            }
        }
        this.factionIDs = characterFactionIDs;
    }

    // Get a list of the characters's valid factions
    // and add to this object as a property.
    setCharacterFactionList() {
        const factionList = JSON.parse(sessionStorage.getItem(`faction`));
        const characterFactionList = [];
        for (const faction of factionList) {
            if (this.factionIDs.includes(faction.id)) {
                const newFaction = {'id': faction.id, 'name': faction.name};
                characterFactionList.push(newFaction);
            }
        }
        this.factionList = characterFactionList;
    }
    
    // Get a list of the Character's specialrule IDs
    // and add to this object as a property.
    setCharacterSpecialruleIDs() {
        const characterSpecialrule = JSON.parse(sessionStorage.getItem('characterspecialrule'));
        const characterSpecialruleIDs = [];
        for (const csr of characterSpecialrule) {
            if (csr.character_id == this.id) {
                characterSpecialruleIDs.push(csr.specialrule_id);
            }
        }
        this.specialruleIDs = characterSpecialruleIDs;
    }

    // Get a list of the Character's special rules as objects
    // and add to this object as a property.
    setCharacterSpecialruleList() {
        const specialRule = JSON.parse(sessionStorage.getItem('specialrule'));
        const characterSpecialruleList = [];
        for (const sr of specialRule) {
            if (this.specialruleIDs.includes(sr.id)) {
                const newSpecialrule = {};
                Object.assign(newSpecialrule, sr);
                characterSpecialruleList.push(newSpecialrule);
            }
        }
        this.specialrule = characterSpecialruleList;
    }

    // Display method for Characters on menu side.
    display() {
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']).attr('id',`character-${this.id}`);
        const cardBody = $('<div>').addClass(['card-body display-card-body']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col']);
        const itemName = $('<h5>').addClass(['card-title']).text(this.name);    
        nameColumn.append(itemName);
        const pointColumn = $('<div>').addClass(['col-auto']).html(`${this.points} pts`);
        const expandColumn = $('<div>').addClass(['col-auto']);
        expandColumn.html(`
                <a href='#character-${this.id}-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='character-${this.id}-expand'></i>
                </a>
                `);
        const addColumn = $('<div>').addClass(['col-auto']).html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-plus' id='character-${this.id}-add'></i>
            </a>
            `);
        cardHeader.append([nameColumn,pointColumn, expandColumn, addColumn]);
        // Beginning of Card Details.
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `character-${this.id}-details`).html(`<hr class='border border-2 border-primary rounded-2'>`);
        // Beginning of Nationality/Faction restrictions for Character.
        const forceRestrictions = $('<div>').addClass('mt-1');
        if (this.nonatives) {
            const noNatives = $('<div>').addClass('text-secondary').html('This Character is available to all Factions, except for Native American Factions.');
            forceRestrictions.append(noNatives);
        }
        else {
            if (this.certainnations) {
                const certainNations = $('<div>');
                if ((this.nationalityList).length == 1) {
                    const nationality = this.nationalityList[0];
                    const nationsList = $('<div>').addClass('text-secondary').html(`This Character is available to the following Nation: ${nationality.name}.`);
                    certainNations.append(nationsList);
                }
                else {
                    const nationsList = $('<div>').addClass('text-secondary').html(`This Character is available to the following Nations:`);
                    for (const [i, nationality] of this.nationalityList.entries()) {
                        if (i+1 == this.nationalityList.length) {
                            const newNationality = ` and ${nationality.name}.`;
                            nationsList.append(newNationality);
                        }
                        else {
                            const newNationality = ` ${nationality.name},`;
                            nationsList.append(newNationality);
                        }
                    }
                    certainNations.append(nationsList);
                }
                forceRestrictions.append(certainNations);
            }
            if (this.certainfactions) {
                const certainFactions = $('<div>');
                if ((this.factionList).length == 1) {
                    const faction = this.factionList[0];
                    const factionsList = $('<div>').addClass('text-secondary').html(`This Character is available to the following Faction: ${faction.name}`);
                    certainFactions.append(factionsList);
                }
                else {
                    const factionsList = $('<div>').addClass('text-secondary').html(`This Character is available to the following Factions:`);
                    for (const [i, faction] of this.factionList.entries()) {
                        if (i+1 == this.factionList.length) {
                            const newFaction = ` and ${faction.name}.`;
                            factionsList.append(newFaction);
                        }
                        else {
                            const newFaction = ` ${faction.name},`;
                            factionsList.append(newFaction);
                        }
                    }
                    certainFactions.append(factionsList);
                }
                forceRestrictions.append(certainFactions);
            }
            if (this.certainnations == 0 && this.certainfactions == 0) {
                const allFactions = $('<div>').addClass('text-secondary').html('This Character is available to all Factions.');
                forceRestrictions.append(allFactions);
            }
        }
        cardDetails.append(forceRestrictions);
        // Beginning of command point data for Character.
        if (this.commandpoints > 0) {
            const commandPointData = $('<div>');
            const pointsRange = $('<div>').addClass('row');
            const commandPoints = $('<div>').addClass('col-6').html(`Command Points: ${this.commandpoints}`);
            const commandRange = $('<div>').addClass('col-6').html(`Command Range: ${this.commandrange}"`);
            pointsRange.append(commandPoints,commandRange);
            commandPointData.append(pointsRange);
            if (this.commandpointconditions) {
                const commandPointConditions = $('<div>').html(this.commandpointconditions);
                commandPointData.append(commandPointConditions);
            }
            cardDetails.append(commandPointData);
        }
        // Beginning of Unit/Commander restrictions for Character.
        if (this.unitrestrictions) {
            const itemrestrictions = $('<div>').addClass(['m-0 p-0 mt-2']).html(`<b>Unit Restrictions:</b><p>${this.unitrestrictions}</p>`);
            cardDetails.append(itemrestrictions);
        }
        // Beginning of extra abilities for Character
        if (this.extraabilities) {
            const additionalRules = $('<div>').addClass(['m-0 p-0']).html(`<b>Additional Rules:</b>${this.extraabilities}`);
            cardDetails.append(additionalRules);
        }
        // Beginning of special rules for Character.
        if (this.specialrule.length > 0) {
            const specialruleCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const specialrulesHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mb-0'>Special Rules</h5>`);
            const specialruleExpandColumn = $('<div>').addClass(['col-1']);
            specialruleExpandColumn.html(`
                <a href='#character-${this.id}-specialrules-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='character-${this.id}-specialrules-expand'></i>
                </a>
            `);
            specialrulesHeader.append([descColumn, specialruleExpandColumn]);
            const specialrulesDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `character-${this.id}-specialrules-details`)
            for (const rule of this.specialrule) {
                const newRule = $('<li>').addClass('mt-1').html(`<b>${rule.name}:</b> ${rule.details}`);
                specialrulesDetails.append(newRule);
            }
            specialruleCard.append(specialrulesHeader, specialrulesDetails);
            cardDetails.append(specialruleCard);
        }
        // End of Character information
        cardBody.append(cardHeader, cardDetails);
        newItem.append(cardBody);
        // Add Character to appropriate div of menu display.
        if (this.charactertype == 1) {
            $('#fighting-man-characters').append(newItem);
        }
        else if (this.charactertype == 2) {
            $('#hostage-advisor-characters').append(newItem);
        }
        // Handle expanding/contracting of item information.
        $(`#character-${this.id}-expand`).parent().on('click', () => {
            $(`#character-${this.id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        if (this.specialrule.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#character-${this.id}-specialrules-expand`).parent().on('click', () => {
                $(`#character-${this.id}-specialrules-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
        }
        // Handle button for adding Character to ForceList.
        $(`#character-${this.id}-add`).parent().on('click', (e) => {
            e.preventDefault();
            const characterToAdd = new Character(this);
            forceList.addCharacter(characterToAdd);
        });
    }
}