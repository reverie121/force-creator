const $unitSizeRangeDisplay = $('#unit-size-range-display');
const $forceName = $('#force_name');
const $pointMax = $('#point_max');
const $selectNationality = $('#select_nation');
const $selectFaction = $('#select_faction');
const $selectCommander = $('#select_commander');
const $componentSelector = $('#component_selector');

// ########## ********** ########## PRIMARY FC CLASS ########## ********** ##########

class ForceList {
    constructor(maxPoints) {
        this.maxPoints = maxPoints;
        this.updateUnitSize();
        this.name = 'A Force Without A Name';
        this.units = {};
        this.characters = {};
        this.ships = {};
        this.artillery = {};
        this.misc = {};
        this.idCounter = 0
        this.coreCount = 0;
        this.supportCount = 0;
        this.fightingCount = 0;
        this.civilianCount = 0;
        this.totalForcePoints = 0;
        $('#force-name').text(this.name);
        $('#point-total-display').text(this.totalForcePoints);
        $('#point-max-display').text(this.maxPoints);
    }

    updateMaxPoints() {
        this.maxPoints = $pointMax.val();
        this.updateUnitSize();
        this.setUnitsToRange();
        $('#point-max-display').text(`${this.maxPoints}`);
    }
    
    updateTotalForcePoints() {
        if (this.commander) {
            this.totalForcePoints = this.commander.points;
        }
        else {
            this.totalForcePoints = 0;
        }
        this.updateAllArtilleryCost();
        this.updateAllCharactersCost();
        this.updateAllShipsCost();
        this.updateAllUnitsCost();
        this.totalForcePoints = this.totalForcePoints + this.allUnitsCost + this.allArtilleryCost + this.allShipsCost + this.allCharactersCost;
        $('#point-total-display').text(`${this.totalForcePoints}`);
    }

    // Reset ForceList object.
    resetForceList() {
        delete this.faction;
        delete this.commander;
        this.resetForceComponents();
    }

    resetForceComponents() {
        delete this.characters;
        delete this.artillery;
        delete this.ships;
        delete this.misc;
        this.characters = {};
        this.ships = {};
        this.artillery = {};
        this.misc = {};
        this.idCounter = 0    
        this.resetForceUnits();
        this.updateCharacterTypeCount();
        this.updateTotalForcePoints();
    }

    resetForceUnits() {
        delete this.units;
        this.emptyUnits();
        this.units = {};
        this.updateUnitClassCount();
    }

    // Empty build area completely.
    emptyBuildArea() {
        $('#force-faction').empty().hide();
        $('#force-commander').empty().hide();
        $('#force-core-units').empty().hide();
        $('#force-support-units').empty().hide();
        $('#force-fighting-characters').empty().hide();
        $('#force-civilian-characters').empty().hide();
        $('#force-artillery').empty().hide();
        $('#force-ships').empty().hide();
        $('#force-misc').empty().hide();
    }

    getSelectedOptions(property) {
        const idList = [];
        for (const k of property) {
            if (k.selected == 1) {
                idList.push(k.id);
            }
        }
        return idList;
    }

    saveList() {
        const newSave = {};
        newSave['maxpoints'] = this.maxPoints;
        newSave['nationality_id'] = this.nationality.id;
        newSave['faction_id'] = this.faction.id;
        newSave['commander_id'] = this.commander.id;
        if (this.faction.option != []) {
            const selectedOptions = this.getSelectedOptions(this.faction.option);
            newSave['faction_option'] = selectedOptions[0] || 0;
        }
        if (this.commander.specialruleChoice != []) {
            const selectedRules = []
            for (const sr of this.commander.specialrule) {
                if (sr['selected'] == 1) {
                    selectedRules.push(sr.id);
                }
            }
            newSave['commanderSpecialruleChoices'] = selectedRules;
        }
        if (Object.keys(this.artillery).length > 0) {
            let count = 0;
            for (const f_id in this.artillery) {
                count ++;
                newSave[`artillery_${count}_id`] = this.artillery[`${f_id}`].id;
                newSave[`artillery_${count}_qty`] = this.artillery[`${f_id}`].qty;
            }
            newSave[`artillerycount`] = count;
        }
        if (Object.keys(this.characters).length > 0) {
            let count = 0;
            for (const f_id in this.characters) {
                count ++;
                newSave[`character_${count}_id`] = this.characters[`${f_id}`].id;
            }
            newSave[`charactercount`] = count;
        }
        if (Object.keys(this.ships).length > 0) {
            let count = 0;
            for (const f_id in this.ships) {
                count ++;
                newSave[`ship_${count}_id`] = this.ships[`${f_id}`].id;
                const selectedOptions = this.getSelectedOptions(this.ships[`${f_id}`]['upgrade']);
                newSave[`ship_${count}_options`] = selectedOptions;
            }
            newSave[`shipcount`] = count;
        }
        if (Object.keys(this.units).length > 0) {
            let count = 0;
            for (const f_id in this.units) {
                count ++;
                newSave[`unit_${count}_id`] = this.units[`${f_id}`].id;
                newSave[`unit_${count}_qty`] = this.units[`${f_id}`].qty;
                const selectedOptions = this.getSelectedOptions(this.units[`${f_id}`]['option']);
                newSave[`unit_${count}_options`] = selectedOptions;            }
            newSave[`unitcount`] = count;
        }
        this.save = newSave;
    }

    // Assign a nationality object to the force list.
    setNationality(nationality) {
        this.nationality = nationality;
        this.nationality.getNationalCommanderList();
        this.nationality.getNationalFactionList();
    }

    // Assign a commander object to the force list.
    setCommander(commander) {
        this.handleCommanderUnitClassChanges(-1);
        this.commander = commander;
        this.updateTotalForcePoints();
        if (!this.faction || !this.faction.commanderIDs.includes(commander.id)) {
            delete this.faction;
            this.resetForceUnits();
            this.updateTotalForcePoints();
            $('#force-faction').hide('medium', 'swing');
            populateFactionDropdown(this.commander.factionList);
        }
        this.handleCommanderUnitClassChanges(1);
        $('#force-commander').show('medium', 'swing');
        this.resetForceComponents();
        resetComponentSelector();
    }

    handleCommanderUnitClassChanges(plusOrMinusOne) {
        if (this.commander && this.faction) {
            // if ((this.commander.commandereffects).length > 0) {
            if (this.commander.commandereffects != []) {
                    if (plusOrMinusOne == 1) {
                    console.debug('Adding Commander unitclass changes.')
                } else if (plusOrMinusOne == -1) {
                    console.debug('Removing Commander unitclass changes.')
                }
                for (const effect of this.commander.commandereffects) {
                    if (effect.addsubtract == plusOrMinusOne && !effect.unitoption_id) {
                        this.faction.unitClass[`${effect.unit_id}`] = effect.unitclass_id
                    }
                }
            }
        }
    }

    handleCommanderSpecialruleChoice(plusOrMinusOne, specialrule_id) {
        // When checking/selecting a Special Rule...
        if (plusOrMinusOne == 1) {
            console.debug('Adding Special Rule to Commander.');
            for (const sr of this.commander.specialruleChoice) {
                if (sr.id == specialrule_id) {
                    sr['selected'] = 1;
                    const newRule = $('<li>').addClass('mt-1').attr('id',`fl-commander-sr-${sr.id}`).html(`<b>${sr.name}:</b> ${sr.details}`);
                    newRule.hide();
                    $('#fl-commander-specialrules').append(newRule);
                    newRule.show('medium','swing');
                }
            }
        // When unchecking/unselecting an option...
        } else if (plusOrMinusOne == -1) {
            console.debug('Removing Special Rule from Commander.');
            for (const sr of this.commander.specialruleChoice) {
                if (sr.id == specialrule_id) {
                    sr['selected'] = 0;
                    $(`#fl-commander-sr-${sr.id}`).hide('medium','swing')
                    setTimeout(() => {
                        $(`#fl-commander-sr-${sr.id}`).remove();
                    }, 500)
                }
            }
        }
    }

    // Assign a faction object to the force list.
    setFaction(faction) {
        this.faction = faction;
        if (!this.commander || !this.commander.factionIDs.includes(faction.id)) {
            delete this.commander;
            this.resetForceUnits();
            this.updateTotalForcePoints();
            $('#force-commander').hide('medium', 'swing');
            populateCommanderDropdown(this.faction.commanderList);
        }
        this.handleCommanderUnitClassChanges(1);
        $('#force-faction').show('medium', 'swing');
        this.resetForceComponents();
        resetComponentSelector();
    }

    // For when Faction/Force Option boxes are clicked.
    handleFactionOption(plusOrMinusOne, forceoption_id) {
        // When checking/selecting an option...
        if (plusOrMinusOne == 1) {
            // Unselect other options if any are selected. There should only ever be one selected.
            for (const o of this.faction.option) {
                if ($(`#faction-${this.faction.id}-option-${o.id}`).prop('checked') && o.id != forceoption_id) {
                    console.debug(`Removing Faction option changes for ${o.name}.`);
                    $(`#faction-${this.faction.id}-option-${o.id}`).prop('checked', false);
                    // Change unit classes where needed for faction option.
                    for (const effect of this.faction.factioneffects) {
                        if (effect.addsubtract == -1 && !effect.unitoption_id && effect.forceoption_id == forceoption_id) {
                            this.faction.unitClass[`${effect.unit_id}`] = effect.unitclass_id;
                        }       
                    }
                    // Change unit classes where needed for previously checked faction option.
                    for (const effect of this.faction.factioneffects) {
                        if (effect.addsubtract == -1 && !effect.unitoption_id && effect.forceoption_id == o.id) {
                            this.faction.unitClass[`${effect.unit_id}`] = effect.unitclass_id;
                        }
                    }
                }
            }
        }
        // Change unit classes where needed for faction option.
        for (const effect of this.faction.factioneffects) {
            if (effect.addsubtract == plusOrMinusOne && !effect.unitoption_id && effect.forceoption_id == forceoption_id) {
                this.faction.unitClass[`${effect.unit_id}`] = effect.unitclass_id;
            }
        }
        // Set Faction/Force Option['selected'] for each Option based on which boxes are now checked.
        for (const o of this.faction.option) {
            if ($(`#faction-${this.faction.id}-option-${o.id}`).prop('checked')) {
                o.selected = 1;
            }
            else {
                o.selected = 0;
            }
        }
        this.resetForceComponents();
        resetComponentSelector();
    }

    // Show force commander in build area.
    displayCommander() {
        // Empty and show force's commander display.
        $('#force-commander').empty();
        // Create new commander display and add to page.
        const commanderDisplay = $('<div>').addClass(['card-body', 'bg-info', 'text-primary', 'rounded-1', 'fell']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col-10']);
        const commanderName = $('<h5>').addClass(['card-title']).text(this.commander.name);     
        nameColumn.append(commanderName);
        const expandColumn = $('<div>').addClass(['col-1']);
        expandColumn.html(`
            <a href='#commander-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='commander-expand' ></i>
            </a>
        `);
        const removeColumn = $('<div>').addClass(['col-1']);
        removeColumn.html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-xmark text-primary' id='commander-remove'></i>
            </a>
        `);
        cardHeader.append([nameColumn,expandColumn,removeColumn]);
        const cardDetails = $('<div>').addClass(['collapse']).attr('id','commander-details').html(`<hr class='border border-2 border-primary rounded-2'>`);
        const commandRow = $('<div>').addClass('row');
        const commandRange = $('<div>').addClass(['card-text', 'col-6']).html(`<b>Command Range:</b> ${this.commander.commandrange}"`);
        const commandPoints = $('<div>').addClass(['card-text', 'col-6']).html(`<b>Command Points:</b> ${this.commander.commandpoints}`);
        commandRow.append(commandRange, commandPoints);
        const mainWeapons = $('<div>').addClass(['card-text']).html('<b>Main Weapons:</b>');
        const weaponText = $('<div>').html(`${this.commander.mainweapons}`);
        mainWeapons.append(weaponText);
        cardDetails.append([commandRow, mainWeapons]);
        // Display Commander Special Rules
        if (this.commander.specialrule.length > 0 || this.commander.specialruleChoice.length > 0) {
            const specialruleCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const specialrulesHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mb-0'>Special Rules</h5>`);
            const specialruleExpandColumn = $('<div>').addClass(['col-1']);
            specialruleExpandColumn.html(`
                <a href='#commander-${this.id}-specialrules-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='commander-${this.id}-specialrules-expand'></i>
                </a>
            `);
            specialrulesHeader.append([descColumn, specialruleExpandColumn]);
            const specialrulesDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `commander-${this.id}-specialrules-details`)
            const specialrules = $('<ul>').addClass('mb-1').attr('id',`fl-commander-specialrules`);
            for (const rule of this.commander.specialrule) {
                const newRule = $('<li>').addClass('mt-1').html(`<b>${rule.name}:</b> ${rule.details}`);
                specialrules.append(newRule);
            }
            specialrulesDetails.append(specialrules);
            // Display Special Rule choices for Standard type Commanders.
            if (this.commander.specialruleChoice.length > 0) {
                let num = 1
                if (this.commander.name.startsWith('Seasoned')) {
                    num = 2
                }
                const choices = $('<div>').html(`<span class='text-secondary mt-0'>May choose ${num} Special Rules from this list:</span>`);
                for (const rule of this.commander.specialruleChoice) {
                    rule['selected'] = 0;
                    const newRule = $('<div>').addClass('container mt-1').html(`<input type='checkbox' class='form-check-input' id='fl-commander-sr-choice-${rule.id}'> <b>${rule.name}:</b> ${rule.details}`);
                    choices.append(newRule);
                }
                specialrulesDetails.append(choices);
            }
            specialruleCard.append(specialrulesHeader, specialrulesDetails);
            cardDetails.append(specialruleCard);
        }
        commanderDisplay.append([cardHeader, cardDetails]);
        $('#force-commander').append(commanderDisplay);
        // Handle expanding/contracting of force's commander information.
        $('#commander-expand').parent().on('click', () => {
            $('#commander-expand').toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        if (this.commander.specialrule.length > 0 || this.commander.specialruleChoice.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#commander-${this.id}-specialrules-expand`).parent().on('click', () => {
                $(`#commander-${this.id}-specialrules-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
        }
        if (this.commander.specialruleChoice.length > 0) {
            // Handle expanding/contracting of item information.
            for (const sr of this.commander.specialruleChoice) {
                $(`#fl-commander-sr-choice-${sr.id}`).on('click',(e) => {
                    if ($(`#fl-commander-sr-choice-${sr.id}`).prop('checked')) {
                        this.handleCommanderSpecialruleChoice(1,sr.id);
                    } else {
                        this.handleCommanderSpecialruleChoice(-1,sr.id);
                    }
                });
            }
        }
        // Handle removal of force's commander.
        $('#commander-remove').parent().on('click', () => {
            $('#force-commander').hide('medium', 'swing');
            setTimeout(() => {
                $('#force-commander').empty()
            }, 500)
            this.handleCommanderUnitClassChanges(-1);
            delete this.commander;
            this.resetForceUnits();
            this.updateTotalForcePoints();
            // If this force has a faction, re-populate commander dropdown with valid commanders.
            // Otherwise re-populate faction and commander dropdowns using the Nation's lists.
            if (this.faction) {
                populateCommanderDropdown(this.faction.commanderList)
            }
            else {
                populateFactionDropdown(this.nationality.factionList);
                populateCommanderDropdown(this.nationality.commanderList);
            }
            resetComponentSelector();
        });
    }

    // Show force faction in build area.
    displayFaction() {
        // Empty force's faction display.
        $('#force-faction').empty();
        // Create new commander display and add to page.
        const factionDisplay = $('<div>').addClass(['card-body', 'bg-info', 'text-primary', 'rounded-1', 'fell']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col-10']);
        const factionName = $('<h5>').addClass(['card-title']).text(this.faction.name);    
        nameColumn.append(factionName);
        const expandColumn = $('<div>').addClass(['col-1']);
        expandColumn.html(`
            <a href='#faction-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='faction-expand' ></i>
            </a>
        `);
        const removeColumn = $('<div>').addClass(['col-1']);
        removeColumn.html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-xmark text-primary' id='faction-remove'> </i>
            </a>
        `);
        cardHeader.append([nameColumn,expandColumn,removeColumn]);
        const cardDetails = $('<div>').addClass(['collapse']).attr('id','faction-details').html(`<hr class='border border-2 border-primary rounded-2'>`);
        const details = $('<div>').addClass(['card-text']);
        if (this.faction.details) {
            details.html(`${this.faction.details}`);
        }        
        const commandOptions = $('<div>').addClass(['card-text']).html(`<b>Commander Options:</b> ${this.faction.commandoptions}`);
        cardDetails.append([details, commandOptions]);
        // If selected faction has special rules, display with a dropdown.
        if (this.faction.specialrule.length > 0) {
            const specialruleCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const specialrulesHeader = $('<div>').addClass(['row', 'mt-2']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mb-0'>Special Rules</h5>`);
            const specialruleExpandColumn = $('<div>').addClass(['col-1']);
            specialruleExpandColumn.html(`
                <a href='#faction-${this.id}-specialrules-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='faction-${this.id}-specialrules-expand'></i>
                </a>
            `);
            specialrulesHeader.append([descColumn, specialruleExpandColumn]);
            const specialrulesDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `faction-${this.id}-specialrules-details`)
            for (const rule of this.faction.specialrule) {
                const newRule = $('<li>').addClass('mt-1').html(`${rule.details}`);
                specialrulesDetails.append(newRule);
            }
            specialruleCard.append(specialrulesHeader, specialrulesDetails);
            cardDetails.append(specialruleCard);
        }
        // If selected faction has options, display with a dropdown.
        if (this.faction.option.length > 0) {
            const optionsCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const factionOptionsHeader = $('<div>').addClass(['row', 'mt-2']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mb-0'>Faction Options</h5>`);
            const optionExpandColumn = $('<div>').addClass(['col-1']);
            optionExpandColumn.html(`
                <a href='#faction-${this.id}-options-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='faction-${this.id}-options-expand'></i>
                </a>
            `);
            factionOptionsHeader.append([descColumn, optionExpandColumn]);
            const unitOptionsDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `faction-${this.id}-options-details`)
            for (const o of this.faction.option) {
                // Set Faction/Force option['selected'] to 0 for 'unselected' when Faction is displayed.
                o['selected'] = 0;
                const newOption = $('<div>').addClass('mt-1').html(`<input type='checkbox' class='form-check-input' id='faction-${this.faction.id}-option-${o.id}'> <b>${o.name}</b>`);
                const optionDetails = $('<div>').html(`${o.details}`);
                newOption.append(optionDetails);
                unitOptionsDetails.append(newOption);
            }
            optionsCard.append(factionOptionsHeader, unitOptionsDetails);
            cardDetails.append(optionsCard);
        }
        factionDisplay.append([cardHeader, cardDetails]);
        $('#force-faction').append(factionDisplay);
        // Handle expanding/contracting of force's faction information.
        $('#faction-expand').parent().on('click', () => {
            $('#faction-expand').toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        if (this.faction.option.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#faction-${this.id}-options-expand`).parent().on('click', () => {
                $(`#faction-${this.id}-options-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
            for (const o of this.faction.option) {
                $(`#faction-${this.faction.id}-option-${o.id}`).on('click',() => {
                    // Handle method for Faction/Force Option wants the Option id and 1/-1 for checked/unchecked.
                    if ($(`#faction-${this.faction.id}-option-${o.id}`).prop('checked')) {
                        this.handleFactionOption(1,o.id);
                    } else {
                        this.handleFactionOption(-1,o.id);
                    }
                });
            }
        }
        if (this.faction.specialrule.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#faction-${this.id}-specialrules-expand`).parent().on('click', () => {
                $(`#faction-${this.id}-specialrules-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
        }
        // Handle removal of force's faction.
        $('#faction-remove').parent().on('click', () => {
            $('#force-faction').hide('medium','swing');
            setTimeout(() => {
                $('#force-faction').empty()
            }, 500)
            delete this.faction;
            this.resetForceUnits();
            this.updateTotalForcePoints();
            // If this force has a commander, re-populate faction dropdown with valid factions.
            // Otherwise re-populate faction and commander dropdowns using the Nation's lists.
            if (this.commander) {
                populateFactionDropdown(this.commander.factionList)            }
            else {
                populateFactionDropdown(this.nationality.factionList);
                populateCommanderDropdown(this.nationality.commanderList);
            }
            resetComponentSelector();
        });
    }

    // Generates a unique ForceList id number to attach to a new component
    // by incrementing a counter property.
    generateId() {
        this.idCounter ++;
        return `f_id_${this.idCounter}`;
    }

    addArtillery(newArtillery) {
        newArtillery['f_id'] = this.generateId();
        newArtillery['qty'] = 1;
        newArtillery['totalCost'] = newArtillery.points * newArtillery.qty;
        this.artillery[`${newArtillery.f_id}`] = newArtillery;
        this.updateTotalForcePoints();
        this.displayArtillery(this.artillery[`${newArtillery.f_id}`]);
    }

    removeArtillery(f_id) {
        delete this.artillery[`${f_id}`];
        this.updateTotalForcePoints();
    }

    updateArtilleryCost(f_id) {
        this.artillery[`${f_id}`].totalCost = this.artillery[`${f_id}`].points * this.artillery[`${f_id}`].qty;
        this.updateTotalForcePoints();
        $(`#fl-${f_id}-qty`).html(this.artillery[`${f_id}`].qty);
        $(`#fl-${f_id}-total-cost`).html(this.artillery[`${f_id}`].totalCost);
    }

    updateAllArtilleryCost() {
        let allArtilleryCost = 0;
        const artillery = this.artillery;
        for (const f_id in artillery) {
            allArtilleryCost = allArtilleryCost + this.artillery[`${f_id}`].totalCost;
        }
        this.allArtilleryCost = allArtilleryCost;
    }

    // Takes a ForceList's artillery group's unique identifier with a positive or
    // negative integer and adjusts the artillery qty.
    adjustArtilleryQty(f_id,adj) {
        if (this.artillery[`${f_id}`].qty + adj < 1) {
            return
        }
        else {
            this.artillery[`${f_id}`].qty = this.artillery[`${f_id}`].qty + adj;
            this.updateArtilleryCost(f_id);
        }
    }

    displayArtillery(artillery) {
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']).attr('id',`fl-${artillery.f_id}`);
        const cardBody = $('<div>').addClass(['card-body']);
        const cardHeader = $('<div>').addClass(['container-fluid']);
        const topRow = $('<div>').addClass(['row mb-0 gy-0'])
        const nameColumn = $('<div>').addClass(['col-10']);
        const itemName = $('<h5>').addClass(['card-title']).text(artillery.name);    
        nameColumn.append(itemName);
        const expandColumn = $('<div>').addClass(['col-1']).html(`
            <a href='#fl-${artillery.f_id}-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='fl-${artillery.f_id}-expand'></i>
            </a>
            `);
        const removeColumn = $('<div>').addClass(['col-1']).html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-xmark text-primary' id='fl-${artillery.f_id}-remove'></i>
            </a>
            `)
        topRow.append([nameColumn,expandColumn,removeColumn]);
        const secondRow = $('<div>').addClass(['row mb-0 gy-0'])
        const pointsEach = $('<div>').addClass(['col-4 d-flex align-items-end']).html(`<span class='text-secondary fs-5' id='fl-${artillery.f_id}-points'>${artillery.points}</span>&nbsp;pts ea`);
        const pointAdjuster = $('<div>').addClass(['col-4 d-flex align-items-end justify-content-center']);
            const subtractModel = $('<span>').html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-minus text-secondary align-self-center' id='fl-${artillery.f_id}-subtract-model'></i>
            </a>
            `)
            const modelQty = $(`<span id='fl-${artillery.f_id}-qty'>`).addClass(['fs-5 ms-2 me-2']).html(`${artillery.qty}`);
            const addModel = $('<span>').html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-plus text-secondary align-self-center' id='fl-${artillery.f_id}-add-model'></i>
            </a>
            `)
            pointAdjuster.append(subtractModel,modelQty,addModel);
        const pointsArtillery = $('<div>').addClass(['col-4 d-flex align-items-end justify-content-end text-primary fs-5']).html(`<span class='text-secondary' id='fl-${artillery.f_id}-total-cost'>${artillery.totalCost}</span>&nbsp;pts`);
        secondRow.append(pointsEach,pointAdjuster,pointsArtillery);
        cardHeader.append([topRow, secondRow]);
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `fl-${artillery.f_id}-details`).html(`
            <hr class='border border-2 border-primary rounded-2'>
            <div class='row'>
                <div class='col-7'>
                    <b>Dice:</b> ${artillery.d10}
                </div>
                <div class='col-5'>
                    <b>Crew</b>: ${artillery.minimumcrew}
                </div>
            </div>
            <div class='row'>
                <div class='col-7'>
                <b>Arc of Fire</b>: ${artillery.arcfire}
                </div>
                <div class='col-5'>
                <b>Shoot Base</b>: ${artillery.shootbase}
                </div>
            </div>
            <div class='row'>
                <div class='col-7'>
                <b>Movement Penalty</b>: ${artillery.movepenalty}
                </div>
                <div class='col-5'>
                <b>Reload Markers</b>: ${artillery.reloadmarkers}
                </div>
            </div>
        
        `);
        cardBody.append(cardHeader, cardDetails);
        newItem.append(cardBody);
        if (Object.keys(this.artillery).length == 1) {
            const componentName = $('<div>').addClass('fell text-primary fs-5').text('Artillery');
            $('#force-artillery').prepend(componentName);
            $('#force-artillery').show('medium','swing');
        }
        newItem.hide();
        $('#force-artillery').append(newItem);
        newItem.show('medium','swing');
        // Handle expanding/contracting of item information.
        $(`#fl-${artillery.f_id}-expand`).parent().on('click', () => {
            $(`#fl-${artillery.f_id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        // Handle minus button to subtract artillery piece from group.
        $(`#fl-${artillery.f_id}-subtract-model`).on('click', () => {
            this.adjustArtilleryQty(artillery.f_id,-1);
        });
        // Handle plus button to add artillery piece to group.
        $(`#fl-${artillery.f_id}-add-model`).on('click', () => {
            this.adjustArtilleryQty(artillery.f_id,1);
        });
        // Handle removal of artillery from ForceList.
        $(`#fl-${artillery.f_id}-remove`).parent().on('click', () => {
            this.removeArtillery(artillery.f_id);
            $(`#fl-${artillery.f_id}`).hide('medium','swing');
            setTimeout(() => {
                $(`#fl-${artillery.f_id}`).remove();
                if (Object.keys(this.artillery).length == 0) {
                    $(`#force-artillery`).hide('medium','swing');
                    setTimeout(() => {
                        $(`#force-artillery`).empty();
                    }, 500)
                }
            }, 500)
        });
    }

    // Updates the ForceList's fightingCount and civilianCount properties by iterating through
    // an arrays of ForceList.characters and counting the 1/2 ['charactertype'] values.
    updateCharacterTypeCount() {
        this.fightingCount = 0;
        this.civilianCount = 0;
        const charactersArray = Object.values(this.characters);
        charactersArray.forEach((character) => {
            if (character['charactertype'] == 1) {
                this.fightingCount ++
            }
            else if (character['charactertype'] == 2) {
                this.civilianCount ++
            }
        })
    }

    checkForCharacter(id) {
        const charactersArray = Object.values(this.characters);
        // If this character is already present in the ForceList, return false to prevent adding a second.
        for (const character of charactersArray) {
            if (id == character.id && id != 39) { // Disclude Praying Indian
                return false
            }
        }
        return true
    }

    addCharacter(newCharacter) {
        if (this.checkForCharacter(newCharacter.id)) {
            newCharacter['f_id'] = this.generateId()
            this.characters[`${newCharacter.f_id}`] = newCharacter
            this.updateCharacterTypeCount();
            this.updateTotalForcePoints();
            this.displayCharacter(this.characters[`${newCharacter.f_id}`]);
        }
    }

    removeCharacter(f_id) {
        delete this.characters[`${f_id}`];
        this.updateCharacterTypeCount();
        this.updateTotalForcePoints();
    }

    updateAllCharactersCost() {
        let allCharactersCost = 0;
        const characters = this.characters;
        for (const f_id in characters) {
            allCharactersCost = allCharactersCost + this.characters[`${f_id}`].points;
        }
        this.allCharactersCost = allCharactersCost;
    }

    displayCharacter(character) {
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']).attr('id',`fl-${character.f_id}`);
        const cardBody = $('<div>').addClass(['card-body']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col-8']);
        const itemName = $('<h5>').addClass(['card-title']).text(character.name);    
        nameColumn.append(itemName);
        const pointColumn = $('<div>').addClass(['col-2']).html(`${character.points} pts`);
        const expandColumn = $('<div>').addClass(['col-1']);
        expandColumn.html(`
                <a href='#fl-${character.f_id}-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='fl-${character.f_id}-expand'></i>
                </a>
                `);
        const removeColumn = $('<div>').addClass(['col-1']).html(`
        <a href='#/' role='button'>
            <i class='fa-solid fa-xmark text-primary' id='fl-${character.f_id}-remove'></i>
        </a>
        `) 
        cardHeader.append([nameColumn,pointColumn, expandColumn, removeColumn]);
        // Beginning of Card Details.
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `fl-${character.f_id}-details`).html(`<hr class='border border-2 border-primary rounded-2'>`);
        // Beginning of Nationality/Faction restrictions for Character.
        const forceRestrictions = $('<div>').addClass('mt-1');
        if (character.nonatives) {
            const noNatives = $('<div>').addClass('text-secondary').html('This Character is available to all Factions, except for Native American Factions.');
            forceRestrictions.append(noNatives);
        }
        else {
            if (character.certainnations) {
                const certainNations = $('<div>');
                if ((character.nationalityList).length == 1) {
                    const nationality = character.nationalityList[0];
                    const nationsList = $('<div>').addClass('text-secondary').html(`This Character is available to the following Nation: ${nationality.name}.`);
                    certainNations.append(nationsList);
                }
                else {
                    const nationsList = $('<div>').addClass('text-secondary').html(`This Character is available to the following Nations:`);
                    for (const [i, nationality] of character.nationalityList.entries()) {
                        if (i+1 == character.nationalityList.length) {
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
            if (character.certainfactions) {
                const certainFactions = $('<div>');
                if ((character.factionList).length == 1) {
                    const faction = character.factionList[0];
                    const factionsList = $('<div>').addClass('text-secondary').html(`This Character is available to the following Faction: ${faction.name}`);
                    certainFactions.append(factionsList);
                }
                else {
                    const factionsList = $('<div>').addClass('text-secondary').html(`This Character is available to the following Factions:`);
                    for (const [i, faction] of character.factionList.entries()) {
                        if (i+1 == character.factionList.length) {
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
            if (character.certainnations == 0 && character.certainfactions == 0) {
                const allFactions = $('<div>').addClass('text-secondary').html('This Character is available to all Factions.');
                forceRestrictions.append(allFactions);
            }
        }
        cardDetails.append(forceRestrictions);
        // Beginning of command point data for Character.
        if (character.commandpoints > 0) {
            const commandPointData = $('<div>');
            const pointsRange = $('<div>').addClass('row');
            const commandPoints = $('<div>').addClass('col-6').html(`Command Points: ${character.commandpoints}`);
            const commandRange = $('<div>').addClass('col-6').html(`Command Range: ${character.commandrange}"`);
            pointsRange.append(commandPoints,commandRange);
            commandPointData.append(pointsRange);
            if (character.commandpointconditions) {
                const commandPointConditions = $('<div>').html(character.commandpointconditions);
                commandPointData.append(commandPointConditions);
            }
            cardDetails.append(commandPointData);
        }
        // Beginning of Unit/Commander restrictions for Character.
        if (character.unitrestrictions) {
            const itemrestrictions = $('<div>').addClass(['m-0 p-0 mt-2']).html(`<b>Unit Restrictions:</b><p>${character.unitrestrictions}</p>`);
            cardDetails.append(itemrestrictions);
        }
        // Beginning of extra abilities for Character
        if (character.extraabilities) {
            const additionalRules = $('<div>').addClass(['m-0 p-0']).html(`<b>Additional Rules:</b>${character.extraabilities}`);
            cardDetails.append(additionalRules);
        }
        // Beginning of special rules for Character.
        if (character.specialrule.length > 0) {
            const specialruleCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const specialrulesHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mb-0'>Special Rules</h5>`);
            const specialruleExpandColumn = $('<div>').addClass(['col-1']);
            specialruleExpandColumn.html(`
                <a href='#fl-${character.f_id}-specialrules-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='fl-${character.f_id}-specialrules-expand'></i>
                </a>
            `);
            specialrulesHeader.append([descColumn, specialruleExpandColumn]);
            const specialrulesDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `fl-${character.f_id}-specialrules-details`)
            for (const rule of character.specialrule) {
                const newRule = $('<li>').addClass('mt-1').html(`<b>${rule.name}:</b> ${rule.details}`);
                specialrulesDetails.append(newRule);
            }
            specialruleCard.append(specialrulesHeader, specialrulesDetails);
            cardDetails.append(specialruleCard);
        }
        // End of Character information
        cardBody.append(cardHeader, cardDetails);
        newItem.append(cardBody);
        // Add Character to appropriate display.
        newItem.hide()
        if (character.charactertype == 1) {
            if (this.fightingCount == 1) {
                const containerName = $('<div>').addClass('fell text-primary fs-5').text('Fighting Men & Women');
                $('#force-fighting-characters').prepend(containerName);
                $('#force-fighting-characters').show('medium','swing');
            }
            $('#force-fighting-characters').append(newItem);
        }
        else if (character.charactertype == 2) {
            if (this.civilianCount == 1) {
                const containerName = $('<div>').addClass('fell text-primary fs-5').text('Hostages & Advisors');
                $('#force-civilian-characters').prepend(containerName);
                $('#force-civilian-characters').show('medium','swing');
            }$('#force-civilian-characters').append(newItem);
        }
        newItem.show('medium','swing')
        // Handle expanding/contracting of item information.
        $(`#fl-${character.f_id}-expand`).parent().on('click', () => {
            $(`#fl-${character.f_id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        // Handle removal of Character from ForceList.
        $(`#fl-${character.f_id}-remove`).parent().on('click', () => {
            let thisCharacterType;
            if (character.charactertype == 1) {
                thisCharacterType = 'fighting';
            }
            else if (character.charactertype == 2) {
                thisCharacterType = 'civilian';
            }
            this.removeCharacter(character.f_id);
            $(`#fl-${character.f_id}`).hide('medium','swing');
            setTimeout(() => {
                $(`#fl-${character.f_id}`).remove();
                if (this[`${thisCharacterType}Count`] == 0) {
                    $(`#force-${thisCharacterType}-characters`).hide('medium','swing');
                    setTimeout(() => {
                        $(`#force-${thisCharacterType}-characters`).empty();
                    }, 500)
                }
            }, 500)
        });
    }

    addShip(newShip) {
        newShip['f_id'] = this.generateId()
        newShip['upgradeCost'] = 0;
        newShip['totalCost'] = newShip.points;
        this.ships[`${newShip.f_id}`] = newShip
        this.updateTotalForcePoints();
        this.displayShip(this.ships[`${newShip.f_id}`]);
    }

    removeShip(f_id) {
        delete this.ships[`${f_id}`];
        this.updateTotalForcePoints();
    }

    updateShipCost(f_id) {
        this.ships[`${f_id}`].totalCost = this.ships[`${f_id}`].points + this.ships[`${f_id}`].upgradeCost;
        this.updateTotalForcePoints();
        $(`#fl-${f_id}-total-cost`).html(this.ships[`${f_id}`].totalCost);
    }

    updateAllShipsCost() {
        let allShipsCost = 0;
        const ships = this.ships;
        for (const f_id in ships) {
            allShipsCost = allShipsCost + this.ships[`${f_id}`].totalCost;
        }
        this.allShipsCost = allShipsCost;
    }

    handleShipUpgrade(f_id, u) {
        if ($(`#fl-${f_id}-upgrade-${u.id}`).prop('checked')) {
            u.selected = 1;
            this.ships[`${f_id}`].upgradeCost += u.pointcost;
            this.updateShipCost(f_id);
            $(`#fl-${f_id}-cost`).html(`${this.ships[`${f_id}`].totalCost} pts`);
            if (u.name.startsWith('Streamlined Hull')) {
                this.ships[`${f_id}`].draft += 1;
                $(`#fl-${f_id}-draft`).html(`${this.ships[`${f_id}`].draft}`)
            }
            else if (u.name.startsWith('Improved Rig')) {
                this.ships[`${f_id}`].topspeed += 1;
                $(`#fl-${f_id}-speed`).html(`${this.ships[`${f_id}`].topspeed}`)
            }
        }
        else {
            u.selected = 0;
            this.ships[`${f_id}`].upgradeCost -= u.pointcost;
            this.updateShipCost(f_id);
            $(`#fl-${f_id}-cost`).html(`${this.ships[`${f_id}`].totalCost} pts`);
            if (u.name.startsWith('Streamlined Hull')) {
                this.ships[`${f_id}`].draft -= 1;
                $(`#fl-${f_id}-draft`).html(`${this.ships[`${f_id}`].draft}`)
            }                        
            else if (u.name.startsWith('Improved Rig')) {
                this.ships[`${f_id}`].topspeed -= 1;
                $(`#fl-${f_id}-speed`).html(`${this.ships[`${f_id}`].topspeed}`)
            }
        }
    }

    displayShip(ship) {
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']).attr('id',`fl-${ship.f_id}`);
        const cardBody = $('<div>').addClass(['card-body']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col-8']);
        const itemName = $('<input>').addClass(['h5 card-title border-0 bg-info text-primary']).attr({'type':'text','id':`fl-${ship.f_id}-nickname`,'value':`${ship.nickname}`});    
        // const itemName = $('<h5>').addClass(['card-title']).text(ship.name);    
        nameColumn.append(itemName);
        const pointColumn = $('<div>').addClass(['col-2']).html(`${ship.points} pts`).attr('id',`fl-${ship.f_id}-cost`);
        const expandColumn = $('<div>').addClass(['col-1']);
        expandColumn.html(`
            <a href='#fl-${ship.f_id}-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='fl-${ship.f_id}-expand'></i>
            </a>
            `);
        const removeColumn = $('<div>').addClass(['col-1']).html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-xmark' id='fl-${ship.f_id}-remove'></i>
            </a>
            `);
        cardHeader.append([nameColumn,pointColumn, expandColumn, removeColumn]);
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `fl-${ship.f_id}-details`).html(`<hr class='border border-2 border-primary rounded-2'>`);
        const leftBox = $('<div>').addClass('col-8').html(`
            <div>${ship.name}</div>
            <div><b>Size:</b> ${ship.size}</div>
            <div><b>Draft:</b> <span id='fl-${ship.f_id}-draft'>${ship.draft}</span></div>
            <div><b>Speed:</b> <span id='fl-${ship.f_id}-speed'>${ship.topspeed}</span>"</div>
            <div><b>Windward:</b> ${ship.windward}</div>
            <div><b>Turn:</b> ${ship.turn}</div>
            <div><b>Sail Settings:</b> ${ship.sailssettings}</div>
        `);
        if (ship.swivels > 0 || ship.cannons > 0) {
            const deckPlan = $('<div>');
            const dpHeader = $('<div>').addClass('row');
            const labelColumn = $('<div>').addClass(`col-${(7-ship.size)}`)
            const headerLabel = $('<div>').html('<b>Deck</b>');
            labelColumn.append(headerLabel);
            const n_of_cols = 12 / ship.size;
            const dataColumn = $('<div>').addClass(`col-${(5+ship.size)}`);
            const headerColumns = $('<div>').addClass('row');
            for (let i = 0; i < ship.size; i++) {
                const newColumn = $('<div>').addClass(`col-${n_of_cols}`).html(`<b>${i+1}</b>`);
                headerColumns.append(newColumn);
            }
            dataColumn.append(headerColumns);
            dpHeader.append(labelColumn, dataColumn);
            if (ship.cannons > 0) {
                const gunsLabel = $('<div>').html('Guns');
                labelColumn.append(gunsLabel);
                const gunsData = $('<div>').addClass('row');
                const gunsPerDeck = ship.cannonsdecks.split('/');
                for (let i = 0; i < ship.size; i++) {
                    const newColumn = $('<div>').addClass(`col-${n_of_cols}`).html(`${gunsPerDeck[i]}`);
                    gunsData.append(newColumn);
                }
                dataColumn.append(gunsData);
            }
            if (ship.swivels > 0) {
                const swivelsLabel = $('<div>').html('Swivels');
                labelColumn.append(swivelsLabel);
                const swivelsData = $('<div>').addClass('row');
                const swivelsPerDeck = ship.swivelsdecks.split('/');
                for (let i = 0; i < ship.size; i++) {
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
        for (let i = 0; i < ship.hullfortitude; i++) {
            const newDiv = $('<div>');
            if (i == (ship.hullfortitude - 1)) {
                newDiv.append(`${ship.hullfortitude - i}`);
            }
            else {
                for (let n = 0; n < ship.hullintegrity; n++) {
                    newDiv.append(`${ship.hullfortitude - i} `);
                }
            }
            hull.append(newDiv);
            rightBox.append(hull);
        }
        if (ship.riggingfortitude > 0) {
            const rigging = $('<div>').addClass('mt-2').html('<b>Rigging</b>');
            for (let i = 0; i < ship.riggingfortitude; i++) {
                const newDiv = $('<div>');
                if (i == (ship.riggingfortitude - 1)) {
                    newDiv.append(`${ship.riggingfortitude - i}`);
                }
                else {
                    for (let n = 0; n < ship.riggingintegrity; n++) {
                        newDiv.append(`${ship.riggingfortitude - i} `);
                    }
                }
                rigging.append(newDiv);
                rightBox.append(rigging);
            }
        }
        const topBox = $('<div>').addClass('row');
        topBox.append(leftBox,rightBox);
        cardDetails.append(topBox);
        if (ship.specialrule.length > 0) {
            const specialrulesCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const shipSpecialrulesHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mt-1 mb-0'>Traits</h5>`);
            const specialruleExpandColumn = $('<div>').addClass(['col-1']);
            specialruleExpandColumn.html(`
                <a href='#fl-${ship.f_id}-specialrules-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='fl-${ship.f_id}-specialrules-expand'></i>
                </a>
            `);
            shipSpecialrulesHeader.append([descColumn, specialruleExpandColumn]);
            const shipSpecialrulesDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `fl-${ship.f_id}-specialrules-details`)
            for (const sr of ship.specialrule) {
                const newSpecialrule = $('<li>').html(`<b>${sr.name}:</b> ${sr.details}`);
                shipSpecialrulesDetails.append(newSpecialrule);
            }
            specialrulesCard.append(shipSpecialrulesHeader, shipSpecialrulesDetails);
            cardDetails.append(specialrulesCard);
        }
        if (ship.upgrade.length > 0) {
            const upgradeCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const upgradeHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mt-1 mb-0'>Upgrades</h5>`);
            const upgradeExpandColumn = $('<div>').addClass(['col-1']);
            upgradeExpandColumn.html(`
                <a href='#fl-${ship.f_id}-upgrades-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='fl-${ship.f_id}-upgrades-expand'></i>
                </a>
            `);
            upgradeHeader.append([descColumn, upgradeExpandColumn]);
            const shipUpgradeDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `fl-${ship.f_id}-upgrades-details`)
            for (const u of ship.upgrade) {
                u['selected'] = 0;
                const newUpgrade = $('<div>').addClass('mt-1').html(`<input type='checkbox' class='form-check-input' id='fl-${ship.f_id}-upgrade-${u.id}'> <b>${u.name}</b> (${u.pointcost} pts)`);
                const upgradeDetails = $('<div>').html(`${u.details}`);
                newUpgrade.append(upgradeDetails);
                shipUpgradeDetails.append(newUpgrade);
            }
            upgradeCard.append(upgradeHeader, shipUpgradeDetails);
            cardDetails.append(upgradeCard);
        }
        cardBody.append(cardHeader, cardDetails);
        newItem.append(cardBody);
        if (Object.keys(this.ships).length == 1) {
            const componentName = $('<div>').addClass('fell text-primary fs-5').text('Ships');
            $('#force-ships').prepend(componentName);
            $('#force-ships').show('medium','swing');
        }
        newItem.hide();
        $(`#force-ships`).append(newItem);
        newItem.show('medium','swing');
        // Handle expanding/contracting of item information.
        $(`#fl-${ship.f_id}-expand`).parent().on('click', () => {
            $(`#fl-${ship.f_id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        // Handle updates to nickname.
        $(`#fl-${ship.f_id}-nickname`).on('keyup', () => {
            this.ships[`${ship.f_id}`]['nickname'] = $(`#fl-${ship.f_id}-nickname`).val();
        });
        if (ship.specialrule.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#fl-${ship.f_id}-specialrules-expand`).parent().on('click', () => {
                $(`#fl-${ship.f_id}-specialrules-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });            
        }
        if (ship.upgrade.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#fl-${ship.f_id}-upgrades-expand`).parent().on('click', () => {
                $(`#fl-${ship.f_id}-upgrades-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
            // Handle checking/unchecking upgrades.
            for (const u of ship.upgrade) {
                $(`#fl-${ship.f_id}-upgrade-${u.id}`).on('click',() => {
                    this.handleShipUpgrade(ship.f_id, u);
                })
            }
        }
        // Handle removal of Ship from ForceList.
        $(`#fl-${ship.f_id}-remove`).parent().on('click', () => {
            this.removeShip(ship.f_id);
            $(`#fl-${ship.f_id}`).hide('medium','swing');
            setTimeout(() => {
                $(`#fl-${ship.f_id}`).remove();
                if (Object.keys(this.ships).length == 0) {
                    $(`#force-ships`).hide('medium','swing');
                    setTimeout(() => {
                        $(`#force-ships`).empty();
                    }, 500)
                }
            }, 500)
        });
    }

    // Updates the ForceList's coreCount and supportCount properties by iterating through
    // an arrays of ForceList.units and counting the core/support ['class'] values.
    updateUnitClassCount() {
        this.coreCount = 0;
        this.supportCount = 0;
        const unitsArray = Object.values(this.units);
        unitsArray.forEach((element) => {
            if (element['class'] == 'core') {
                this.coreCount ++
            }
            else if (element['class'] == 'support') {
                this.supportCount ++
            }
        })
    }

    addUnit(newUnit) {
        newUnit['f_id'] = this.generateId();
        newUnit['qty'] = this.unitMin;
        newUnit['modelsCost'] = newUnit.points * newUnit.qty;
        newUnit['perUnitCost'] = 0;
        newUnit['totalUnitCost'] = newUnit.modelsCost + newUnit.perUnitCost;
        if (this.faction.unitClass[`${newUnit.id}`] == 1) {
            newUnit['class'] = 'core';
        }
        else if (this.faction.unitClass[`${newUnit.id}`] == 2) {
            newUnit['class'] = 'support';
        }
        // Apply faction options that affect unit options.
        for (const o of this.faction.option) {
            if (o.selected == 1) {
                for (const fe of this.faction.factioneffects) {
                    if (fe.unitoption_id && fe.forceoption_id == o.id) {
                        // Add unit options to specific unit as appropriate based on faction option selected.
                        if (fe.unit_id == newUnit.id) {
                            const unitoptions = JSON.parse(sessionStorage.getItem('unitoption'));
                            for (const unitoption of unitoptions) {
                                if (unitoption.id == fe.unitoption_id) {
                                    newUnit.option.push(unitoption);
                                }
                            }
                        }
                        // Add unit options to general unit as appropriate based on faction option selected.
                        else if (!fe.unit_id) {
                            const unitoptions = JSON.parse(sessionStorage.getItem('unitoption'));
                            if (!fe.unitclass_id) {
                                for (const unitoption of unitoptions) {
                                    if (unitoption.id == fe.unitoption_id) {
                                        newUnit.option.push(unitoption);
                                    }
                                }
                            }
                            else if (fe.unitclass_id == 1 && newUnit.class == 'Core') {
                                for (const unitoption of unitoptions) {
                                    if (unitoption.id == fe.unitoption_id) {
                                        newUnit.option.push(unitoption);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        this.units[`${newUnit.f_id}`] = newUnit;
        this.updateUnitClassCount();
        this.updateTotalForcePoints();
        this.displayUnit(this.units[`${newUnit.f_id}`]);
    }

    removeUnit(f_id) {
        delete this.units[`${f_id}`];
        this.updateUnitClassCount();     
        this.updateTotalForcePoints();
    }

    emptyUnits() {
        $('#force-core-units').hide('medium','swing');
        $('#force-support-units').hide('medium','swing');
        setTimeout(() => {
            $('#force-core-units').empty();
            $('#force-support-units').empty();
        }, 500);
        this.units = {}
        this.updateUnitClassCount();     
        this.updateTotalForcePoints();       
    }

    // Update the ForceList's unit size range (unitMin and unitMax)
    // based on ForceList.maxpoints and updates UI display.
    updateUnitSize() {
        this.unitMin = Math.floor(this.maxPoints / 100) + 2;
        this.unitMax = (Math.floor(this.maxPoints / 100) + 1)*4;
        $unitSizeRangeDisplay.html(`<i>${this.unitMin} to ${this.unitMax} models per unit</i>`);
    }

    // Takes a ForceList's unit's unique identifier and recalculates the
    // unit's total unit cost using points (per model), qty, and perUnitCost.
    updateUnitCost(f_id) {
        this.units[`${f_id}`].modelsCost = this.units[`${f_id}`].points * this.units[`${f_id}`].qty;
        this.units[`${f_id}`].totalUnitCost = this.units[`${f_id}`].modelsCost + this.units[`${f_id}`].perUnitCost;
        this.updateTotalForcePoints();
        $(`#fl-${f_id}-points`).html(this.units[`${f_id}`].points);
        $(`#fl-${f_id}-qty`).html(this.units[`${f_id}`].qty);
        $(`#fl-${f_id}-per-cost`).html(this.units[`${f_id}`].perUnitCost);
        $(`#fl-${f_id}-total-cost`).html(this.units[`${f_id}`].totalUnitCost);
    }

    updateAllUnitsCost() {
        let allUnitsCost = 0;
        const units = this.units;
        for (const f_id in units) {
            allUnitsCost = allUnitsCost + this.units[`${f_id}`].totalUnitCost;
        }
        this.allUnitsCost = allUnitsCost;
    }

    // Iterate through units in ForceList and if Qty is not in range, adjust to min/max.
    setUnitsToRange() {
        const units = this.units;
        for (const f_id in units) {
            this.updateUnitQty(f_id);
            this.updateUnitCost(f_id);
        }
    }

    // Takes a ForceList's unit's unique identifier and changes the unit's
    // qty to unitMin if currently below, or to unitMax if currently above.
    updateUnitQty(f_id) {
        const unit = this.units[f_id];
        if (unit.qty < this.unitMin) {
            this.units[`${f_id}`].qty = this.unitMin;
        }
        else if (unit.qty > this.unitMax) {
            this.units[`${f_id}`].qty = this.unitMax;
        }
    }

    // Takes a ForceList's unit's unique identifier with a positive or
    // negative integer and adjusts the unit's qty, id change would be in range.
    adjustUnitQty(f_id,adj) {
        if (this.units[`${f_id}`].qty + adj < this.unitMin || this.units[`${f_id}`].qty + adj > this.unitMax) {
            return
        }
        else {
            this.units[`${f_id}`].qty = this.units[`${f_id}`].qty + adj;
            this.units[`${f_id}`].perxmodels = 0;
            for (const o in this.units[`${f_id}`].option) {
                if (o.perxmodels && o.selected) {
                    this.units[`${f_id}`].perUnitCost += Math.floor(this.units[`${f_id}`].qty / o.perxmodels) * o.pointcost;
                }
                else if (o.pointsperunit && o.selected) {
                    this.units[`${f_id}`].perUnitCost += o.pointsperunit;
                }
            }
            this.updateUnitCost(f_id);
        }
    }

    adjustUnitCost(f_id, o, addsubtract) {
        if ((o.pointcost) && (!o.perxmodels)) {
            this.units[`${f_id}`].points += o.pointcost * addsubtract;
        }
        if (o.perxmodels) {
            this.units[`${f_id}`].perUnitCost += Math.floor(this.units[`${f_id}`].qty / o.perxmodels) * o.pointcost * addsubtract;
        }
        if (o.pointsperunit) {
            this.units[`${f_id}`].perUnitCost += o.pointsperunit * addsubtract
        }
        this.updateUnitCost(f_id);
    }

    handleUnitOption(f_id, o) {
        // If Upgrade is selected...
        if ($(`#fl-${f_id}-option-${o.id}`).prop('checked')) {
            o.selected = 1;
            this.adjustUnitCost(f_id, o, 1);
            if (o.experienceupg) {
                this.units[f_id].experience_id += o.experienceupg;
                this.units[f_id].setUnitExperienceName();
                $(`#fl-${f_id}-exp-name`).html(this.units[`${f_id}`].experience_name);
            }
            // Apply this upgrade change to all like units if appropriate.
            if (o.applyall && Object.keys(forceList.units).length > 1) {
                for (const unit in this.units) {
                    if (this.units[`${unit}`].id == this.units[`${f_id}`].id && unit != f_id) {
                        let option;
                        for (const opt of this.units[`${unit}`].option) {
                            if (opt.id == o.id) {
                                option = opt;
                            }
                        }
                        option.selected = 1;
                        $(`#fl-${unit}-option-${o.id}`).prop('checked', true);
                        this.adjustUnitCost(unit, option, 1);
                        if (o.experienceupg) {
                            this.units[`${unit}`].experience_id += o.experienceupg;
                            this.units[`${unit}`].setUnitExperienceName();
                            $(`#fl-${unit}-exp-name`).html(this.units[`${unit}`].experience_name);
                        }
                    }
                }
            }
        }
        // If Upgrade is deselected...
        else {
            o.selected = 0;
            this.adjustUnitCost(f_id, o, -1);
            if (o.experienceupg) {
                this.units[f_id].experience_id -= o.experienceupg;
                this.units[f_id].setUnitExperienceName();
                $(`#fl-${f_id}-exp-name`).html(this.units[`${f_id}`].experience_name);
            }
            // Apply this upgrade change to all like units if appropriate.
            if (o.applyall && Object.keys(forceList.units).length > 1) {
                for (const unit in this.units) {
                    if (this.units[`${unit}`].id == this.units[`${f_id}`].id && unit != f_id) {
                        let option;
                        for (const opt of this.units[`${unit}`].option) {
                            if (opt.id == o.id) {
                                option = opt;
                            }
                        }
                        option.selected = 0;
                        $(`#fl-${unit}-option-${o.id}`).prop('checked', false);
                        this.adjustUnitCost(unit, option, -1);
                        if (o.experienceupg) {
                            this.units[`${unit}`].experience_id -= o.experienceupg;
                            this.units[`${unit}`].setUnitExperienceName();
                            $(`#fl-${unit}-exp-name`).html(this.units[`${unit}`].experience_name);
                        }
                    }
                }
            }
        }
    }

    displayUnit(unit) {
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']).attr('id',`fl-${unit.f_id}`);
        const cardBody = $('<div>').addClass(['card-body']);
        const cardHeader = $('<div>').addClass(['container-fluid']);
        const topRow = $('<div>').addClass(['row mb-0 gy-0'])
        const nameColumn = $('<div>').addClass(['col-10']);
        const itemName = $('<input>').addClass(['h5 card-title border-0 bg-info text-primary']).attr({'type':'text','id':`fl-${unit.f_id}-nickname`,'value':`${unit.nickname}`});    
        nameColumn.append(itemName);
        const expandColumn = $('<div>').addClass(['col-1']);
        expandColumn.html(`
            <a href='#fl-${unit.f_id}-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='fl-${unit.f_id}-expand'></i>
            </a>
            `);
        const removeColumn = $('<div>').addClass(['col-1']);
        removeColumn.html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-xmark text-primary' id='fl-${unit.f_id}-remove'></i>
            </a>
            `)
        topRow.append([nameColumn,expandColumn,removeColumn]);
        const secondRow =  $('<div>').addClass(['row mt-0 gy-0']);
        const pointsEach = $('<div>').addClass(['col-3 d-flex align-items-end']).html(`<span class='text-secondary fs-5' id='fl-${unit.f_id}-points'>${unit.points}</span>&nbsp;pts ea`);
        const pointAdjuster = $('<div>').addClass(['col-3 d-flex align-items-end']);
            const subtractModel = $('<span>').html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-minus text-secondary align-self-center' id='fl-${unit.f_id}-subtract-model'></i>
            </a>
            `)
            const modelQty = $(`<span id='fl-${unit.f_id}-qty'>`).addClass(['fs-5 ms-2 me-2']).html(`${unit.qty}`);
            const addModel = $('<span>').html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-plus text-secondary align-self-center' id='fl-${unit.f_id}-add-model'></i>
            </a>
            `)
            pointAdjuster.append(subtractModel,modelQty,addModel);
        const perUnitCost = $('<div>').addClass(['col-3 d-flex align-items-end justify-content-middle']).html(`+ <span class='text-secondary fs-5' id='fl-${unit.f_id}-per-cost'>${unit.perUnitCost}</span>&nbsp;pts`);
        const pointsUnit = $('<div>').addClass(['col-3 text-center text-primary fs-5']).html(`<span class='text-secondary' id='fl-${unit.f_id}-total-cost'>${unit.totalUnitCost}</span> pts`);
        secondRow.append(pointsEach,pointAdjuster,perUnitCost,pointsUnit);
        cardHeader.append(topRow,secondRow);
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `fl-${unit.f_id}-details`).html(`
            <hr class='border border-2 border-primary rounded-2'>
            <div class='container'>${unit.name}</div>
            <div class='container'><i id='fl-${unit.f_id}-exp-name'>${unit.experience_name}</i></div>
            <div class='row'>
                <div class='col-4 text-center'>
                    <b>Fight:</b> ${unit.fightskill} / ${unit.fightsave}
                </div>
                <div class='col-4 text-center'>
                    <b>Shoot:</b> ${unit.shootskill} / ${unit.shootsave}
                </div>
                <div class='col-4 text-center'>
                    <b>Resolve:</b> ${unit.resolve}
                </div>
            </div>
            <div class='container mt-1'>
                <b>Main Weapons</b>:
                <div class='mt-0'>${unit.mainweapons}</div>
            </div>
        `);
        if (unit.sidearms) {
            const sidearms = $('<div>').addClass('mt-1').html(`<b>Sidearms</b>: ${unit.sidearms}`);
            cardDetails.append(sidearms);
        }
        if (unit.equipment) {
            const equipment = $('<div>').addClass('mt-1').html(`<b>Equiment</b>: ${unit.equipment}`);
            cardDetails.append(equipment);
        }
        if (unit.option.length > 0) {
            const optionsCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const unitOptionsHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mb-0'>Unit Options</h5>`);
            const optionExpandColumn = $('<div>').addClass(['col-1']);
            optionExpandColumn.html(`
                <a href='#fl-${unit.f_id}-options-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='fl-${unit.f_id}-options-expand'></i>
                </a>
            `);
            unitOptionsHeader.append([descColumn, optionExpandColumn]);
            const unitOptionsDetails = $('<div>').addClass(['collapse','card-text']).attr('id', `fl-${unit.f_id}-options-details`)
            for (const o of unit.option) {
                o['selected'] = 0;
                const newOption = $('<div>').addClass('mt-1').html(`<input type='checkbox' class='form-check-input' id='fl-${unit.f_id}-option-${o.id}'> ${o.details}`);
                unitOptionsDetails.append(newOption);
            }
            optionsCard.append(unitOptionsHeader, unitOptionsDetails);
            cardDetails.append(optionsCard);
        }
        if (unit.specialrule.length > 0) {
            const specialruleCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const specialrulesHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mb-0'>Special Rules</h5>`);
            const specialruleExpandColumn = $('<div>').addClass(['col-1']);
            specialruleExpandColumn.html(`
                <a href='#fl-${unit.f_id}-specialrules-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='fl-${unit.f_id}-specialrules-expand'></i>
                </a>
            `);
            specialrulesHeader.append([descColumn, specialruleExpandColumn]);
            const specialrulesDetails = $('<ul>').addClass(['collapse','card-text']).attr('id', `fl-${unit.f_id}-specialrules-details`)
            for (const rule of unit.specialrule) {
                const newRule = $('<li>').addClass('mt-1').html(`<b>${rule.name}:</b> ${rule.details}`);
                specialrulesDetails.append(newRule);
            }
            specialruleCard.append(specialrulesHeader, specialrulesDetails);
            cardDetails.append(specialruleCard);
        }
        cardBody.append(cardHeader, cardDetails);
        newItem.append(cardBody);
        newItem.hide();
        if (unit.class == 'core') {
            if (this.coreCount == 1) {
                const containerName = $('<div>').addClass('fell text-primary fs-5').text('Core Units');
                $('#force-core-units').prepend(containerName);
                $('#force-core-units').show('medium','swing');
            }
            $('#force-core-units').append(newItem);
        }
        else if (unit.class == 'support') {
            if (this.supportCount == 1) {
                const containerName = $('<div>').addClass('fell text-primary fs-5').text('Support Units');
                $('#force-support-units').prepend(containerName);
                $('#force-support-units').show('medium','swing');
            }$('#force-support-units').append(newItem);
        }
        newItem.show('medium','swing');
        // Handle updates to nickname.
        $(`#fl-${unit.f_id}-nickname`).on('keyup', () => {
            this.units[`${unit.f_id}`]['nickname'] = $(`#fl-${unit.f_id}-nickname`).val();
        });
        // Handle expanding/contracting of item information.
        $(`#fl-${unit.f_id}-expand`).parent().on('click', () => {
            $(`#fl-${unit.f_id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        if (unit.option.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#fl-${unit.f_id}-options-expand`).parent().on('click', () => {
                $(`#fl-${unit.f_id}-options-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
            // Handle checking/unchecking of options.
            for (const o of unit.option) {
                $(`#fl-${unit.f_id}-option-${o.id}`).on('click',() => {
                    this.handleUnitOption(unit.f_id, o);
                })
            }
        }
        if (unit.specialrule.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#fl-${unit.f_id}-specialrules-expand`).parent().on('click', () => {
                $(`#fl-${unit.f_id}-specialrules-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
        }
        // Handle removal of unit from ForceList.
        $(`#fl-${unit.f_id}-remove`).parent().on('click', () => {
            const thisUnitClass = unit.class;
            this.removeUnit(unit.f_id);
            $(`#fl-${unit.f_id}`).hide('medium','swing');
            setTimeout(() => {
                $(`#fl-${unit.f_id}`).remove();
                if (this[`${thisUnitClass}Count`] == 0) {
                    $(`#force-${thisUnitClass}-units`).hide('medium','swing');
                    setTimeout(() => {
                        $(`#force-${thisUnitClass}-units`).empty();
                    }, 500)
                }
            }, 500)
        });
        // Handle minus button to subtract model from unit.
        $(`#fl-${unit.f_id}-subtract-model`).on('click', () => {
            this.adjustUnitQty(unit.f_id,-1);
        });
        // Handle plus button to add model to unit.
        $(`#fl-${unit.f_id}-add-model`).on('click', () => {
            this.adjustUnitQty(unit.f_id,1);
        });
    }
}


// ########## ********** ########## TOP LEVEL FC CLASSES ########## ********** ##########


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


class Faction {

    initialize(faction_data, nationality_name) {
        Object.assign(this, faction_data);
        this.setFactionCommanderIDs();
        this.setFactionCommanderList(nationality_name);
        this.setFactionOptions();
        this.setFactionEffects();
        this.setFactionSpecialrules();
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
        if ((this.option).length > 0) {
            const factioneffect = JSON.parse(sessionStorage.getItem('factioneffect'));
            const factioneffects = [];
            const optionIDs = []
            for (const o of this.option) {
                optionIDs.push(o.id);
            }
            for (const fe of factioneffect) {
                if (optionIDs.includes(fe.forceoption_id)) {
                    factioneffects.push(fe);
                }
            }
            this.factioneffects = factioneffects;
        }
    }
}

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
    }

    setCommanderEffects() {
        const commanderEffect = JSON.parse(sessionStorage.getItem('commandereffect'));
        const commandereffects = [];
        for (const ce of commanderEffect) {
            if (ce.commander_id == this.id) {
                commandereffects.push(ce);
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


// ########## ********** ########## COMPONENT LEVEL FC CLASSES ########## ********** ##########


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
            <a href='#artillery-${this.id}-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='artillery-${this.id}-expand'></i>
            </a>
            `);
            const addColumn = $('<div>').addClass(['col-1']);
        addColumn.html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-plus text-primary'  id='artillery-${this.id}-add'></i>
            </a>
            `)
        cardHeader.append([nameColumn,pointColumn, expandColumn, addColumn]);
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `artillery-${this.id}-details`).html(`
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
        $(`#artillery-${this.id}-expand`).parent().on('click', () => {
            $(`#artillery-${this.id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        // Handle button for adding artillery to ForceList.
        $(`#artillery-${this.id}-add`).parent().on('click', (e) => {
            e.preventDefault();
            const artilleryToAdd = new Artillery(this);
            forceList.addArtillery(artilleryToAdd);
        });
    }
}

class Character {
    constructor(item) {
        Object.assign(this, item);
        this.setCharacterNationalityIDs();
        this.setCharacterNationalityList();
        this.setCharacterFactionIDs();
        this.setCharacterFactionList();
        this.setCharacterSpecialruleIDs();
        this.setCharacterSpecialruleList();
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
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']);
        const cardBody = $('<div>').addClass(['card-body']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col-8']);
        const itemName = $('<h5>').addClass(['card-title']).text(this.name);    
        nameColumn.append(itemName);
        const pointColumn = $('<div>').addClass(['col-2']).html(`${this.points} pts`);
        const expandColumn = $('<div>').addClass(['col-1']);
        expandColumn.html(`
                <a href='#character-${this.id}-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='character-${this.id}-expand'></i>
                </a>
                `);
        const addColumn = $('<div>').addClass(['col-1']).html(`
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
        // Handle button for adding ship to ForceList.
        $(`#character-${this.id}-add`).parent().on('click', (e) => {
            e.preventDefault();
            const characterToAdd = new Character(this);
            forceList.addCharacter(characterToAdd);
        });
    }
}

class Ship {
    constructor(item) {
        Object.assign(this, item);
        this.nickname = this.name;
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

    // Display method for Ships on the menu side.
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
            </a>
            `);
        const addColumn = $('<div>').addClass(['col-1']).html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-plus' id='ship-${this.id}-add'></i>
            </a>
            `);
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
                </a>
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
                </a>
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
        $(`#ship-${this.id}-expand`).parent().on('click', () => {
            $(`#ship-${this.id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        if (this.specialrule.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#ship-${this.id}-specialrules-expand`).parent().on('click', () => {
                $(`#ship-${this.id}-specialrules-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });            
        }
        if (this.upgrade.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#ship-${this.id}-upgrades-expand`).parent().on('click', () => {
                $(`#ship-${this.id}-upgrades-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
        }
        // Handle button for adding ship to ForceList.
        $(`#ship-${this.id}-add`).parent().on('click', (e) => {
            e.preventDefault();
            const shipToAdd = new Ship(this);
            forceList.addShip(shipToAdd);
        });
    }
}


class Unit {
    constructor(item) {
        Object.assign(this, item);
        this.nickname = this.name
        this.setUnitSpecialruleIDs();
        this.setUnitSpecialrules();
        this.setUnitOptions();
        this.setUnitExperienceName();
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

    setUnitExperienceName() {
        if (this.experience_id == 1) {
            this.experience_name ='Inexperienced';
        } else if (this.experience_id == 2) {
            this.experience_name ='Trained';
        } else if (this.experience_id == 3) {
            this.experience_name ='Veteran';
        }
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

    // Display method for Unit objects.
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
            <a href='#unit-${this.id}-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='unit-${this.id}-expand'></i>
            </a>
            `);
            const addColumn = $('<div>').addClass(['col-1']);
        addColumn.html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-plus text-primary'  id='unit-${this.id}-add'></i>
            </a>
            `);
        cardHeader.append([nameColumn,pointColumn, expandColumn, addColumn]);
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `unit-${this.id}-details`).html(`
            <hr class='border border-2 border-primary rounded-2'>
            <div><i>${this.experience_name}</i></div>
            <div class='row'>
                <div class='col-4 text-center'>
                    <b>Fight:</b> ${this.fightskill} / ${this.fightsave}
                </div>
                <div class='col-4 text-center'>
                    <b>Shoot:</b> ${this.shootskill} / ${this.shootsave}
                </div>
                <div class='col-4 text-center'>
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
                </a>
            `);
            unitOptionsHeader.append([descColumn, optionExpandColumn]);
            const unitOptionsDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `unit-${this.id}-options-details`)
            for (const o of this.option) {
                const newOption = $('<li>').addClass('mt-1').html(`${o.details}`);
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
                </a>
            `);
            specialrulesHeader.append([descColumn, specialruleExpandColumn]);
            const specialrulesDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `unit-${this.id}-specialrules-details`)
            for (const rule of this.specialrule) {
                const newRule = $('<li>').addClass('mt-1').html(`<b>${rule.name}:</b> ${rule.details}`);
                specialrulesDetails.append(newRule);
            }
            specialruleCard.append(specialrulesHeader, specialrulesDetails);
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
        $(`#unit-${this.id}-expand`).parent().on('click', () => {
            $(`#unit-${this.id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        if (this.option.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#unit-${this.id}-options-expand`).parent().on('click', () => {
                $(`#unit-${this.id}-options-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });            
        }
        if (this.specialrule.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#unit-${this.id}-specialrules-expand`).parent().on('click', () => {
                $(`#unit-${this.id}-specialrules-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
        }
        // Handle button for adding unit to ForceList.
        $(`#unit-${this.id}-add`).parent().on('click', (e) => {
            e.preventDefault();
            const unitToAdd = new Unit(this);
            forceList.addUnit(unitToAdd);
        });
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
                </a>
                `);
        }
        const addColumn = $('<div>').addClass(['col-1']);
        addColumn.html(``);
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
        $(`#misc-${this.id}-expand`).parent().on('click', () => {
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
    sessionStorage.setItem('commandereffect', JSON.stringify(response.data.commandereffect));
    sessionStorage.setItem('commandernationality', JSON.stringify(response.data.commandernationality));
    sessionStorage.setItem('commanderfaction', JSON.stringify(response.data.commanderfaction));
    sessionStorage.setItem('commanderspecialrule', JSON.stringify(response.data.commanderspecialrule));
    sessionStorage.setItem('factioneffect', JSON.stringify(response.data.factioneffect));
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

function resetComponentSelector() {
    if ($componentSelector[0][0].text != 'Please Select From Menu') {
        $componentSelector.prepend($('<option></option>').val(0).text('Please Select From Menu'));
    }
    $componentSelector.val(0);
    $('#menu').hide('medium', 'swing');
    setTimeout(() => {
        $('#menu').empty();
    }, 500)    
    // Hides and shows save/download options for build side.
    if (!forceList.faction || !forceList.commander) {
        $('#component-instructions').show('slow', 'swing');
        $('#component_selector').hide('medium', 'swing');
        $('#fl-options-expand').hide('fast', 'swing');
        $('#force-save').hide('fast', 'swing');
        $('#force-download').hide('fast', 'swing');
    } else {
        $('#component-instructions').hide('fast', 'swing');
        $('#component_selector').show('medium', 'swing');
        $('#fl-options-expand').show('fast', 'swing');
        $('#force-save').show('fast', 'swing');
        $('#force-download').show('fast', 'swing');
    }
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
    $(`#fl-options-expand`).parent().on('click', () => {
        $(`#fl-options-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
    });
    $('#force-save').on('click', () => {
        forceList.saveList();
        alert('saved!');
    })
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

$pointMax.on('change', () => {
    forceList.updateMaxPoints();
});

// Handle Nationality selector dropdown.
$selectNationality.on('change', async function(e) {
    // Remove the placeholder option as needed.
    if ($selectNationality[0][0].text == 'Who Do You Fight For...') {
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
    // Reset forceList object.
    forceList.resetForceList();
    forceList.emptyBuildArea();
    // Create new Nationality instance and assign it to ForceList object.
    const forceNationality = new Nationality(nationalityData.nationality);
    forceList.setNationality(forceNationality);    
    // Populate Faction and Commander dropdowns.
    populateFactionDropdown(forceList.nationality.factionList);
    populateCommanderDropdown(forceList.nationality.commanderList);
    // Show display in UI.
    resetComponentSelector()
    $('#welcome-area').hide('fast', 'swing');
    $('#build-area').show('slow', 'swing');    
});

// Handle Commander Selector dropdown.
$selectCommander.on('change', function() {
    // Remove the placeholder option as needed.
    if ($selectCommander[0][0].text == 'Who Leads Your Force...') {
        $selectCommander[0][0].remove();
    }
    const nationalCommanderList = JSON.parse(sessionStorage.getItem(`${forceList.nationality.name}_commanders`));
    const selectedCommander = nationalCommanderList.find(commander => commander.id == $selectCommander.val());
    const forceCommander = new Commander();
    forceCommander.initialize(selectedCommander, forceList.nationality.name);
    forceList.setCommander(forceCommander);
    forceList.displayCommander();
    resetComponentSelector()
});

// Handle Faction Selector dropdown.
$selectFaction.on('change', async function() {
    // Remove the placeholder option as needed.
    if ($selectFaction[0][0].text == 'Be More Specific...') {
        $selectFaction[0][0].remove();
    }
    const nationalFactionList = JSON.parse(sessionStorage.getItem(`${forceList.nationality.name}_factions`));
    const selectedFaction = nationalFactionList.find(faction => faction.id == $selectFaction.val());
    const forceFaction = new Faction(forceList.nationality.name);
    forceFaction.initialize(selectedFaction, forceList.nationality.name);
    forceList.setFaction(forceFaction);
    await forceList.faction.setFactionUnits();
    forceList.displayFaction();
    resetComponentSelector()
});

// Handle menu component (artillery, characters, units, etc) dropdown.
$componentSelector.on('change', async function() {
    // Remove the placeholder option as needed.
    if ($selectFaction[0][0].text == 'Please Select From Menu') {
        $selectFaction[0][0].remove();
    }
    // Get string identifier for component type.
    const selected = $componentSelector.val();
    if (sessionStorage.getItem(`${selected}`) == null) {
        if (selected == 'artillery' || selected == 'misc') {
            var response = await axios.get(`/${selected}`);
        }
        else {
            var response = await axios.get(`/${selected}s`);
        }
        if (selected == 'character') {
            sessionStorage.setItem(`faction`, JSON.stringify(response.data['faction']));
            sessionStorage.setItem(`characternationality`, JSON.stringify(response.data['characternationality']));
            sessionStorage.setItem(`characterfaction`, JSON.stringify(response.data['characterfaction']));
            sessionStorage.setItem(`characterspecialrule`, JSON.stringify(response.data['characterspecialrule']));
        }
        else if (selected == 'ship') {
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
    $('#menu').show().empty();
    if (selected == 'character') {
        const fightingMan = $('<div>').addClass(['collapse rounded-2', 'force-selector-field','p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'fighting-man-characters').html(`<span class='fell fs-5'>Fighting Men & Women</span>`);
        const hostageAdvisor = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'hostage-advisor-characters').html(`<span class='fell fs-5'>Hostages & Advisors</span>`);
        $('#menu').append(fightingMan,hostageAdvisor);
        fightingMan.show('medium', 'swing');
        hostageAdvisor.show('medium', 'swing');
    }
    else if (selected == 'ship') {
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
        if (selected == 'character') {
            if (menuItem.certainnations == 1 && menuItem.certainfactions == 1 && forceList.faction) {
                if (menuItem.nationalityIDs.includes(forceList.nationality.id) || menuItem.factionIDs.includes(forceList.faction.id)) {
                    menuItem.display();
                }
            }
            else if (menuItem.certainnations == 1) {
                if (menuItem.nationalityIDs.includes(forceList.nationality.id)) {
                    menuItem.display();
                }
            }
            else if (menuItem.certainfactions == 1) {
                if (forceList.faction) {
                    if (menuItem.factionIDs.includes(forceList.faction.id)) {
                        menuItem.display();
                    }
                }
            }
            else if (forceList.nationality.id == 8) {
                if (menuItem.nonatives == 0) {
                    menuItem.display();
                }
            }
            else {
                menuItem.display();
            }
        }
        else {
            menuItem.display();
        }
    }
});