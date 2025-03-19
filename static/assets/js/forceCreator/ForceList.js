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
        this.updateAllMiscCost();
        this.updateModelCount();
        this.totalForcePoints = this.totalForcePoints + this.allUnitsCost + this.allArtilleryCost + this.allShipsCost + this.allCharactersCost + this.allMiscCost;
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
        return String(idList);
    }

    prepareSave() {
        const newSave = {};
        newSave['name'] = this.name;
        newSave['maxpoints'] = this.maxPoints;
        newSave['totalforcepoints'] = this.totalForcePoints;
        newSave['nationality_id'] = this.nationality.id;
        newSave['faction_id'] = this.faction.id;
        newSave['forceoption_id'] = this.faction.forceoption_id;
        newSave['commander_id'] = this.commander.id;
        newSave['commandernickname'] = this.commander.nickname;
        newSave['commanderhorseselected'] = 0;
        if (this.commander.horseoption == 1) {
            if ($('#fl-commander-horseoption').prop( "checked") == true) {
                newSave['commanderhorseselected'] = 1;
            }
        }
        newSave['commanderhorseoption'] = this.commander.horseoption;
        newSave['commandersr1_id'] = this.commander.specialruleChosenIDs[0] || 0;           
        newSave['commandersr2_id'] = this.commander.specialruleChosenIDs[1] || 0;
        newSave['idcounter'] = this.idCounter;
        if (Object.keys(this.artillery).length > 0) {
            let count = 0;
            for (const f_id in this.artillery) {
                count ++;
                newSave[`artillery_${count}_id`] = this.artillery[`${f_id}`].id;
                newSave[`artillery_${count}_fid`] = this.artillery[`${f_id}`].f_id;
                newSave[`artillery_${count}_nickname`] = this.artillery[`${f_id}`].nickname;
                newSave[`artillery_${count}_qty`] = this.artillery[`${f_id}`].qty;
                const selectedOptions = this.getSelectedOptions(this.artillery[`${f_id}`]['option']);
                newSave[`artillery_${count}_options`] = selectedOptions;
               }
            newSave[`artillerycount`] = count;
        } else {
            newSave[`artillerycount`] = 0;
        }
        if (Object.keys(this.characters).length > 0) {
            let count = 0;
            for (const f_id in this.characters) {
                count ++;
                newSave[`character_${count}_id`] = this.characters[`${f_id}`].id;
                newSave[`character_${count}_fid`] = this.characters[`${f_id}`].f_id;
                newSave[`character_${count}_nickname`] = this.characters[`${f_id}`].nickname;
            }
            newSave[`charactercount`] = count;
        } else {
            newSave[`charactercount`] = 0;
        }
        if (Object.keys(this.ships).length > 0) {
            let count = 0;
            for (const f_id in this.ships) {
                count ++;
                newSave[`ship_${count}_id`] = this.ships[`${f_id}`].id;
                newSave[`ship_${count}_fid`] = this.ships[`${f_id}`].f_id;
                newSave[`ship_${count}_nickname`] = this.ships[`${f_id}`].nickname;
                const selectedOptions = this.getSelectedOptions(this.ships[`${f_id}`]['upgrade']);
                newSave[`ship_${count}_upgrades`] = selectedOptions;
            }
            newSave[`shipcount`] = count;
        } else {
            newSave[`shipcount`] = 0;
        }
        if (Object.keys(this.units).length > 0) {
            let count = 0;
            for (const f_id in this.units) {
                count ++;
                newSave[`unit_${count}_id`] = this.units[`${f_id}`].id;
                newSave[`unit_${count}_fid`] = this.units[`${f_id}`].f_id;
                newSave[`unit_${count}_nickname`] = this.units[`${f_id}`].nickname;
                newSave[`unit_${count}_qty`] = this.units[`${f_id}`].qty;
                const selectedOptions = this.getSelectedOptions(this.units[`${f_id}`]['option']);
                newSave[`unit_${count}_options`] = selectedOptions;            }
            newSave[`unitcount`] = count;
        } else {
            newSave[`unitcount`] = 0;
        }
        if (Object.keys(this.misc).length > 0) {
            let count = 0;
            for (const f_id in this.misc) {
                count ++;
                newSave[`misc_${count}_fid`] = this.misc[`${f_id}`].f_id;
                newSave[`misc_${count}_name`] = this.misc[`${f_id}`].name;
                newSave[`misc_${count}_details`] = this.misc[`${f_id}`].details;
                newSave[`misc_${count}_points`] = this.misc[`${f_id}`].points;
                newSave[`misc_${count}_qty`] = this.misc[`${f_id}`].qty;
            newSave[`misccount`] = count;
           }
        } else {
            newSave[`misccount`] = 0;
        }
        if (this.uuid) {
            newSave['uuid'] = this.uuid;
        }
        if (this.username) {
            newSave['username'] = this.username;
        }
        return newSave;
    }

    async saveList() {
        const newSave = this.prepareSave();
        // Send save data to back end.
        const response = await axios.post('/lists/save', newSave);
        // Take uuid response and add to ForceList and to save data.
        this.uuid = response.data;
        newSave.uuid = response.data;
        // Add save data to ForceList. Save data is used for 'revert' feature and to update future saves.
        this.save = newSave;
        this.resetBuildSideTools();
        window.location.href = `/lists/${this.save.uuid}`;
    }

    async saveListToPDF() {
        // const newSave = this.prepareSave();
        // this.save = newSave;

        // Send save data to back end for conversion to pdf.
        const response = await axios.post('/lists/pdf', this, {responseType: 'blob'});
        // Get list data from response. List name will be used for file name.
        const listData = JSON.parse(response.config.data);
        // Create a URL for the PDF and a link to the URL.
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        // Link is set to download a PDF file.
        link.setAttribute('download', `${listData.name}.pdf`);
        document.body.appendChild(link);
        // Click the link.
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);        
    }

    async loadSave(saveData) {
        $forceName.val(saveData.name).change();
        $pointMax.val(saveData.maxpoints).change();
        $selectNationality.val(saveData.nationality_id).change();
        $selectFaction.val(saveData.faction_id).change();
        if (saveData.forceoption_id != 0) {
            setTimeout(() => {
                $(`#faction-${saveData.faction_id}-option-${saveData.forceoption_id}`).prop( "checked", true );
                setTimeout(() => { 
                    this.handleFactionOption(1,saveData.forceoption_id)
                },100)             
            },100)             
        }
        $selectCommander.val(saveData.commander_id).change();
        $('#fl-commander-nick-name').val(saveData.commandernickname).change();
        if (saveData.commanderhorseselected == 1) {
            setTimeout(() => {
                $('#fl-commander-horseoption').prop( "checked", true );
                this.commander.points ++;
            }, 100)
        }
        if (saveData.commandersr1_id != 0) {
            setTimeout(() => {
                $(`#fl-commander-sr-choice-${saveData.commandersr1_id}`).prop( "checked", true );
                setTimeout(() => { 
                    this.handleCommanderSpecialruleChoice(1,saveData.commandersr1_id);
                },100)             
            },100)             
        }
        if (saveData.commandersr2_id != 0) {
            setTimeout(() => {
                $(`#fl-commander-sr-choice-${saveData.commandersr2_id}`).prop( "checked", true );
                setTimeout(() => { 
                    this.handleCommanderSpecialruleChoice(1,saveData.commandersr2_id);
                },100)             
            },100)            
         }
        this.uuid = saveData.uuid;
        setTimeout(async () => {
            if (saveData.artillerycount > 0) {
                if (sessionStorage.getItem('artillery') == null) {
                    const response = await axios.get('artillery');
                    sessionStorage.setItem('artillery', JSON.stringify(response.data['artillery']));
                }
                const artilleryData = JSON.parse(sessionStorage.getItem('artillery'));
                for (const artilleryItem of artilleryData) {
                    for (let i = 1; i <= saveData.artillerycount; i++) {
                        if (artilleryItem.id == saveData[`artillery_${i}_id`]) {
                            const newArtillery = new Artillery(artilleryItem);
                            newArtillery['nickname'] = saveData[`artillery_${i}_nickname`];
                            newArtillery['f_id'] = saveData[`artillery_${i}_fid`];
                            newArtillery['qty'] = saveData[`artillery_${i}_qty`];
                            this.addArtillery(newArtillery);
                            setTimeout(() => {
                                for (const option of this.artillery[`${newArtillery['f_id']}`]['option']) {
                                    if (saveData[`artillery_${i}_options`].includes(option.id)) {
                                        $(`#fl-${newArtillery['f_id']}-option-${option.id}`).prop( "checked", true );
                                        setTimeout(() => {
                                            this.handleArtilleryOption(newArtillery['f_id'],option);
                                        }, 100);
                                    }
                                }
                            }, 100);
                        }
                    }
                }
            }
            if (saveData.charactercount > 0) {
                if (sessionStorage.getItem('character') == null) {
                    const response = await axios.get('character');
                    sessionStorage.setItem('character', JSON.stringify(response.data['character']));
                }
                const characterData = JSON.parse(sessionStorage.getItem('character'));
                for (const characterItem of characterData) {
                    for (let i = 1; i <= saveData.charactercount; i++) {
                        if (characterItem.id == saveData[`character_${i}_id`]) {
                            const newCharacter = new Character(characterItem);
                            newCharacter['nickname'] = saveData[`character_${i}_nickname`];
                            newCharacter['f_id'] = saveData[`character_${i}_fid`];
                            this.addCharacter(newCharacter);
                        }
                    }
                }
            }
            if (saveData.shipcount > 0) {
                if (sessionStorage.getItem('ship') == null) {
                    const response = await axios.get('ship');
                    sessionStorage.setItem('ship', JSON.stringify(response.data['ship']));
                }
                const shipData = JSON.parse(sessionStorage.getItem('ship'));
                for (const shipItem of shipData) {
                    for (let i = 1; i <= saveData.shipcount; i++) {
                        if (shipItem.id == saveData[`ship_${i}_id`]) {
                            const newShip = new Ship(shipItem);
                            newShip['nickname'] = saveData[`ship_${i}_nickname`];
                            newShip['f_id'] = saveData[`ship_${i}_fid`];
                            this.addShip(newShip);
                            setTimeout(() => {
                                for (const upgrade of this.ships[`${newShip['f_id']}`]['upgrade']) {
                                    if (saveData[`ship_${i}_upgrades`].includes(upgrade.id)) {
                                        $(`#fl-${newShip['f_id']}-upgrade-${upgrade.id}`).prop( "checked", true );
                                        setTimeout(() => {
                                            this.handleShipUpgrade(newShip['f_id'],upgrade);
                                        }, 100);
                                    }
                                }
                            }, 100);
                        }
                    }
                }
            } 
            if (saveData.unitcount > 0) {
                for (const unitItem of this.faction.unitList) {
                    for (let i = 1; i <= saveData.unitcount; i++) {
                        if (unitItem.id == saveData[`unit_${i}_id`]) {
                            const newUnit = new Unit(unitItem);
                            newUnit['nickname'] = saveData[`unit_${i}_nickname`];
                            newUnit['f_id'] = saveData[`unit_${i}_fid`];
                            newUnit['qty'] = saveData[`unit_${i}_qty`];
                            this.addUnit(newUnit);
                            setTimeout(() => {
                                for (const option of this.units[`${newUnit['f_id']}`]['option']) {
                                    if (saveData[`unit_${i}_options`].includes(option.id)) {
                                        $(`#fl-${newUnit['f_id']}-option-${option.id}`).prop( "checked", true );
                                        setTimeout(() => {
                                            this.handleUnitOption(newUnit['f_id'],option);
                                        }, 100);
                                    }
                                }
                            }, 100);
                        }
                    }
                }
            }        
            if (saveData.misccount > 0) {
                for (let i = 1; i <= saveData.misccount; i++) {
                    const newMisc = new Misc();
                    newMisc['name'] = saveData[`misc_${i}_name`];
                    newMisc['f_id'] = saveData[`misc_${i}_fid`];
                    newMisc['qty'] = saveData[`misc_${i}_qty`];
                    newMisc['points'] = saveData[`misc_${i}_points`];
                    newMisc['details'] = saveData[`misc_${i}_details`];
                    this.addMisc(newMisc);
                }
            }
            if (saveData.username) {
                this.username = saveData.username;
            }
            this.updateTotalForcePoints();
            this.idCounter = saveData.idcounter;
            this.save = saveData;
            this.resetBuildSideTools();
        }, 800)
    }

    resetBuildSideTools() {
        // Hide and show forceList tool icons.
        // $('#force-revert').hide('medium', 'swing');
        // $('#force-save').hide('medium', 'swing');
        // $('#force-pdf').hide('medium', 'swing');
        setTimeout(() => {
            $('#force-revert').show('medium', 'swing');
            $('#force-save').show('medium', 'swing');
            $('#force-pdf').show('medium', 'swing');
        },400)
    }

    updateModelCount() {
        let modelCount = 0;
        // Count Commmander (count twice for Red & White Chiefs)
        if (this.commander !== undefined) {
            modelCount ++;
            if (this.commander.id == 227) {
                modelCount ++;
            }
        }
        // Count Characters
        modelCount += Object.keys(this.characters).length;
        // Count Units
        for (const unit in this.units) {
            modelCount += this.units[`${unit}`]['qty'];
        }
        let strikePointsEvery = Math.floor(modelCount / 4);
        if (modelCount < 4) {
            strikePointsEvery = 1;
        }
        this.modelCount = modelCount;
        this.strikePointsEvery = strikePointsEvery;
        $('#model-count').html(`${modelCount}`);
        $('#strike-points-1').html(`${strikePointsEvery}`);
        $('#strike-points-2').html(`${strikePointsEvery * 2}`);
        $('#strike-points-3').html(`${strikePointsEvery * 3}`);
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
        this.commander['nickname'] = this.commander.name
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

    // Used for commanders with an Unorthodox Force rule to change unit 
    // classes from core to support or support to core as appropriate.
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
        let chosenIDs = []
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
                if (sr.selected == 1) {
                    chosenIDs.push(sr.id)
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
                if (sr.selected == 1) {
                    chosenIDs.push(sr.id)
                }
            }
        }
        this.commander.specialruleChosenIDs = chosenIDs;
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
            this.faction['forceoption_id'] = forceoption_id;
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
        else {
            this.faction['forceoption_id'] = 0;
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
        const commanderDisplay = $('<div>').addClass(['card-body', 'bg-info', 'text-primary', 'rounded-1', 'fell', 'display-faction-commander']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col']);
        if (this.commander.commanderclass_id == 1) {
            var commanderName = $('<input>').addClass(['form-control p-0 border-0 bg-info text-primary bigger-text']).attr({'type':'text','maxlength':'35', 'id':`fl-commander-nickname`,'value':`${this.commander.nickname}`});
        } else {
            var commanderName = $('<h5>').addClass(['card-title']).text(this.commander.name);     
        }
        nameColumn.append(commanderName);
        const expandColumn = $('<div>').addClass(['col-auto']);
        expandColumn.html(`
            <a href='#commander-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='commander-expand' ></i>
            </a>
        `);
        const removeColumn = $('<div>').addClass(['col-auto']);
        removeColumn.html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-xmark text-primary' id='commander-remove'></i>
            </a>
        `);
        cardHeader.append([nameColumn,expandColumn,removeColumn]);
        const cardDetails = $('<div>').addClass(['collapse']).attr('id','commander-details').html(`<hr class='border border-2 border-primary rounded-2'>`);
        if (this.commander.commanderclass_id == 1) {
            const commanderNameOriginal = $('<div>').html(`${this.commander.name}`);
            cardDetails.append(commanderNameOriginal);
        }
        if (this.commander.details) {
            const details = $('<div>').addClass(['card-text text-secondary']).html(`${this.commander.details}`);
            const horizontalrule = $('<hr>').addClass(['border', 'border-2', 'border-primary', 'rounded-2']);
            cardDetails.append(details, horizontalrule);
        }
        if (this.commander.unorthodoxforce) {
            const unorthodoxforce = $('<div>').addClass(['card-text text-secondary']).html(`<b>Unorthodox Force:</b> ${this.commander.unorthodoxforce}`);
            const horizontalrule = $('<hr>').addClass(['border', 'border-2', 'border-primary', 'rounded-2']);
            cardDetails.append(unorthodoxforce, horizontalrule);
        }
        const commandRow = $('<div>').addClass('row');
        const commandRange = $('<div>').addClass(['card-text', 'col-6']).html(`<b>Command Range:</b> ${this.commander.commandrange}"`);
        const commandPoints = $('<div>').addClass(['card-text', 'col-6']).html(`<b>Command Points:</b> ${this.commander.commandpoints}`);
        commandRow.append(commandRange, commandPoints);
        const mainWeapons = $('<div>').addClass(['card-text']).html(`<b>Main Weapons:</b> ${this.commander.mainweapons}`);
        cardDetails.append([commandRow, mainWeapons]);
        // Horse Option checkbox for Commanders that have this option.
        if (this.commander.horseoption == 1) {
            const horseopt = $('<div>').addClass('mt-1').html(`<input type='checkbox' class='form-check-input' id='fl-commander-horseoption'> This commander may add a Horse for 1 pt.`);
            cardDetails.append(horseopt);
        }
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
        // Handle updates to nickname.
        $(`#fl-commander-nickname`).on('keyup change', () => {
            this.commander['nickname'] = $(`#fl-commander-nickname`).val();
        });
        // Handle expanding/contracting of force's commander information.
        $('#commander-expand').parent().on('click', () => {
            $('#commander-expand').toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        // Handle expander for all Commander Special Rules content.
        if (this.commander.specialrule.length > 0 || this.commander.specialruleChoice.length > 0) {
            $(`#commander-${this.id}-specialrules-expand`).parent().on('click', () => {
                $(`#commander-${this.id}-specialrules-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
        }
        // Handle Special Rule checkboxes for Standard Commanders.
        if (this.commander.specialruleChoice.length > 0) {
            for (const sr of this.commander.specialruleChoice) {
                $(`#fl-commander-sr-choice-${sr.id}`).on('change',(e) => {
                    if ($(`#fl-commander-sr-choice-${sr.id}`).prop('checked')) {
                        this.handleCommanderSpecialruleChoice(1,sr.id);
                    } else {
                        this.handleCommanderSpecialruleChoice(-1,sr.id);
                    }
                });
            }
        }
        // Handle Horse Option click.
        if (this.commander.horseoption == 1) {
            $(`#fl-commander-horseoption`).on('click', () => {
                if ($(`#fl-commander-horseoption`).prop('checked')) {
                    this.commander.points ++;
                } else {
                    this.commander.points --;
                }
                this.updateTotalForcePoints();
            });
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
        const factionDisplay = $('<div>').addClass(['card-body', 'bg-info', 'text-primary', 'rounded-1', 'fell', 'display-faction-commander']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col']);
        const factionName = $('<h5>').addClass(['card-title']).text(this.faction.name);    
        nameColumn.append(factionName);
        const expandColumn = $('<div>').addClass(['col-auto']);
        expandColumn.html(`
            <a href='#faction-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='faction-expand' ></i>
            </a>
        `);
        const removeColumn = $('<div>').addClass(['col-auto']);
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
        const activePeriod = $('<div>').addClass(['card-text']).html(`<b>Active Period:</b> ${this.faction.first_year} to ${this.faction.last_year} `)
        const commandOptions = $('<div>').addClass(['card-text']).html(`<b>Commander Options:</b> ${this.faction.commandoptions}`);
        cardDetails.append([details, activePeriod, commandOptions]);
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
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mb-0'>Force Options</h5>`);
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
                $(`#faction-${this.faction.id}-option-${o.id}`).on('click change',() => {
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
        if (!Object.keys(newArtillery).includes('f_id')) {
            newArtillery['f_id'] = this.generateId();
        }
        if (!Object.keys(newArtillery).includes('qty')) {
            newArtillery['qty'] = 1;
        }
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
        $(`#fl-${f_id}-points`).html(this.artillery[`${f_id}`].points);
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

    // Add or subtract option cost from artillery cost.
    adjustArtilleryCost(f_id, o, addsubtract) {
        this.artillery[`${f_id}`].points += o.pointcost * addsubtract;
        this.updateArtilleryCost(f_id);
    }

    handleArtilleryOption(f_id, o) {
        // If Upgrade is selected...
        if ($(`#fl-${f_id}-option-${o.id}`).prop('checked')) {
            o.selected = 1;
            this.adjustArtilleryCost(f_id, o, 1);
        }
        // If Upgrade is deselected...
        else {
            o.selected = 0;
            this.adjustArtilleryCost(f_id, o, -1);
        }
    }

    displayArtillery(artillery) {
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']).attr('id',`fl-${artillery.f_id}`);
        const cardBody = $('<div>').addClass(['card-body display-card-body']);
        const cardHeader = $('<div>').addClass(['container-fluid display-card-header']);
        const topRow = $('<div>').addClass(['row mb-0 gy-0'])
        const nameColumn = $('<div>').addClass(['col']);
        const itemName = $('<input>').addClass(['form-control p-0 border-0 bg-info text-primary bigger-text']).attr({'type':'text','maxlength':'35','id':`fl-${artillery.f_id}-nickname`,'value':`${artillery.nickname}`});    
        nameColumn.append(itemName);
        const expandColumn = $('<div>').addClass(['col-auto']).html(`
            <a href='#fl-${artillery.f_id}-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='fl-${artillery.f_id}-expand'></i>
            </a>
            `);
        const removeColumn = $('<div>').addClass(['col-auto']).html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-xmark text-primary' id='fl-${artillery.f_id}-remove'></i>
            </a>
            `)
        topRow.append([nameColumn,expandColumn,removeColumn]);
        const secondRow = $('<div>').addClass(['row mb-0 gy-0'])
        const pointsEach = $('<div>').addClass(['col-auto col-md-4 d-flex align-items-end']).html(`<span class='text-secondary bigger-text' id='fl-${artillery.f_id}-points'>${artillery.points}</span>&nbsp;pts ea`);
        const pointAdjuster = $('<div>').addClass(['col-auto col-md-4 d-flex align-items-end justify-content-center']);
            const subtractModel = $('<span>').html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-minus text-secondary align-self-center' id='fl-${artillery.f_id}-subtract-model'></i>
            </a>
            `)
            const modelQty = $(`<span id='fl-${artillery.f_id}-qty'>`).addClass(['bigger-text ms-2 me-2']).html(`${artillery.qty}`);
            const addModel = $('<span>').html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-plus text-secondary align-self-center' id='fl-${artillery.f_id}-add-model'></i>
            </a>
            `)
            pointAdjuster.append(subtractModel,modelQty,addModel);
        const pointsArtillery = $('<div>').addClass(['col-auto col-md-4 d-flex align-items-end justify-content-end text-primary bigger-text']).html(`<span class='text-secondary' id='fl-${artillery.f_id}-total-cost'>${artillery.totalCost}</span>&nbsp;pts`);
        secondRow.append(pointsEach,pointAdjuster,pointsArtillery);
        cardHeader.append([topRow, secondRow]);
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `fl-${artillery.f_id}-details`).html(`
            <hr class='border border-2 border-primary rounded-2'>
            <div>${artillery.name}</div>
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
                <b>Movement Penalty</b>: ${artillery.movepenalty}"
                </div>
                <div class='col-5'>
                <b>Reload Markers</b>: ${artillery.reloadmarkers}
                </div>
            </div>
        
        `);
        if (!artillery.name.includes('Swivel')) {
            const optionCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const optionHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mt-1 mb-0'>Options</h5>`);
            const optionExpandColumn = $('<div>').addClass(['col-1']);
            optionExpandColumn.html(`
                <a href='#fl-${artillery.f_id}-options-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='fl-${artillery.f_id}-options-expand'></i>
                </a>
            `);
            optionHeader.append([descColumn, optionExpandColumn]);
            const artilleryOptionDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `fl-${artillery.f_id}-options-details`)
            for (const o of artillery.option) {
                o['selected'] = 0;
                const newOption = $('<div>').addClass('mt-1').html(`<input type='checkbox' class='form-check-input' id='fl-${artillery.f_id}-option-${o.id}'> <b>${o.name}</b> (${o.pointcost} pts)`);
                const optionDetails = $('<div>').html(`${o.details}`);
                newOption.append(optionDetails);
                artilleryOptionDetails.append(newOption);
            }
            optionCard.append(optionHeader, artilleryOptionDetails);
            cardDetails.append(optionCard);
        }
        cardBody.append(cardHeader, cardDetails);
        newItem.append(cardBody);
        if (Object.keys(this.artillery).length == 1) {
            const componentName = $('<div>').addClass('fell text-primary bigger-text').text('Artillery');
            $('#force-artillery').prepend(componentName);
            $('#force-artillery').show('medium','swing');
        }
        newItem.hide();
        $('#force-artillery').append(newItem);
        newItem.show('medium','swing');
        // Handle updates to nickname.
        $(`#fl-${artillery.f_id}-nickname`).on('keyup change', () => {
            this.artillery[`${artillery.f_id}`]['nickname'] = $(`#fl-${artillery.f_id}-nickname`).val();
        });
        // Handle expanding/contracting of item information.
        $(`#fl-${artillery.f_id}-expand`).parent().on('click', () => {
            $(`#fl-${artillery.f_id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        if (!artillery.name.includes('Swivel')) {
            // Handle expanding/contracting of item information.
            $(`#fl-${artillery.f_id}-options-expand`).parent().on('click', () => {
                $(`#fl-${artillery.f_id}-options-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
            // Handle checking/unchecking of options.
            for (const o of artillery.option) {
                $(`#fl-${artillery.f_id}-option-${o.id}`).on('click',() => {
                    this.handleArtilleryOption(artillery.f_id, o);
                })
            }
        }
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
            if (!Object.keys(newCharacter).includes('f_id')) {
                newCharacter['f_id'] = this.generateId();
            }
            this.characters[`${newCharacter.f_id}`] = newCharacter
            this.updateCharacterTypeCount();
            this.updateTotalForcePoints();
            this.displayCharacter(this.characters[`${newCharacter.f_id}`]);
            if (newCharacter.id != 39) {
                $(`#character-${newCharacter.id}`).hide('medium','swing');
            }
        }
    }

    removeCharacter(f_id) {
        if (this.characters[`${f_id}`]['id'] != 39) {
            $(`#character-${this.characters[`${f_id}`]['id']}`).show('medium','swing');
        }
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
        const cardBody = $('<div>').addClass(['card-body display-card-body']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col']);
        const itemName = $('<input>').addClass(['form-control p-0 border-0 bg-info text-primary bigger-text']).attr({'type':'text','maxlength':'35','id':`fl-${character.f_id}-nickname`,'value':`${character.nickname}`});    
        nameColumn.append(itemName);
        const pointColumn = $('<div>').addClass(['col-auto']).html(`${character.points} pts`);
        const expandColumn = $('<div>').addClass(['col-auto']);
        expandColumn.html(`
                <a href='#fl-${character.f_id}-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='fl-${character.f_id}-expand'></i>
                </a>
                `);
        const removeColumn = $('<div>').addClass(['col-auto']).html(`
        <a href='#/' role='button'>
            <i class='fa-solid fa-xmark text-primary' id='fl-${character.f_id}-remove'></i>
        </a>
        `) 
        cardHeader.append([nameColumn,pointColumn, expandColumn, removeColumn]);
        // Beginning of Card Details.
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `fl-${character.f_id}-details`).html(`<hr class='border border-2 border-primary rounded-2'>`);
        const characterName = $('<div>').html(`${character.name}`);
        cardDetails.append(characterName);
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
                const containerName = $('<div>').addClass('fell text-primary bigger-text').text('Fighting Men & Women');
                $('#force-fighting-characters').prepend(containerName);
                $('#force-fighting-characters').show('medium','swing');
            }
            $('#force-fighting-characters').append(newItem);
        }
        else if (character.charactertype == 2) {
            if (this.civilianCount == 1) {
                const containerName = $('<div>').addClass('fell text-primary bigger-text').text('Hostages & Advisors');
                $('#force-civilian-characters').prepend(containerName);
                $('#force-civilian-characters').show('medium','swing');
            }$('#force-civilian-characters').append(newItem);
        }
        newItem.show('medium','swing')
        // Handle updates to nickname.
        $(`#fl-${character.f_id}-nickname`).on('keyup change', () => {
            this.characters[`${character.f_id}`]['nickname'] = $(`#fl-${character.f_id}-nickname`).val();
        });
        // Handle expanding/contracting of item information.
        $(`#fl-${character.f_id}-expand`).parent().on('click', () => {
            $(`#fl-${character.f_id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        if (character.specialrule.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#fl-${character.f_id}-specialrules-expand`).parent().on('click', () => {
                $(`#fl-${character.f_id}-specialrules-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
        }
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

    removeAnachronisticShipUpgrades(upgrades) {
        let i = 0;
        while (i < upgrades.length) {
          if (upgrades[i]['post1700'] === 1) {
            console.debug(`Removing ${upgrades[i]['name']} upgrade from Ship (Anachronistic).`)
            upgrades.splice(i, 1);
          } else {
            ++i;
          }
        }
        return upgrades;
      }

    addShip(newShip) {
        if (!Object.keys(newShip).includes('f_id')) {
            newShip['f_id'] = this.generateId();
        }
        newShip['upgradeCost'] = 0;
        newShip['totalCost'] = newShip.points;
        if (this.faction.last_year < 1701) {
            newShip['upgrade'] = this.removeAnachronisticShipUpgrades(newShip['upgrade']);
        }
        this.ships[`${newShip.f_id}`] = newShip;
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
                $(`#fl-${f_id}-draft`).html(`${this.ships[`${f_id}`].draft}`);
            }
            else if (u.name.startsWith('Improved Rig')) {
                this.ships[`${f_id}`].topspeed += 1;
                $(`#fl-${f_id}-speed`).html(`${this.ships[`${f_id}`].topspeed}`);
            }
            else if (u.name.startsWith('Light Gunboat')) {
                this.ships[`${f_id}`].swivels = 2;
                this.ships[`${f_id}`].swivelsdecks = '2';
                this.ships[`${f_id}`].cannons = 1;
                this.ships[`${f_id}`].cannonsdecks = '1';
                $(`#fl-${f_id}-cannonsDecks-${1}`).html('1');
                $(`#fl-${f_id}-swivelsDecks-${1}`).html('2');
                $(`#fl-${f_id}-cannonsLabel`).show('medium','swing');
                $(`#fl-${f_id}-cannonsData`).show('medium','swing');
            }
        }
        else {
            u.selected = 0;
            this.ships[`${f_id}`].upgradeCost -= u.pointcost;
            this.updateShipCost(f_id);
            $(`#fl-${f_id}-cost`).html(`${this.ships[`${f_id}`].totalCost} pts`);
            if (u.name.startsWith('Streamlined Hull')) {
                this.ships[`${f_id}`].draft -= 1;
                $(`#fl-${f_id}-draft`).html(`${this.ships[`${f_id}`].draft}`);
            }                        
            else if (u.name.startsWith('Improved Rig')) {
                this.ships[`${f_id}`].topspeed -= 1;
                $(`#fl-${f_id}-speed`).html(`${this.ships[`${f_id}`].topspeed}`);
            }
            else if (u.name.startsWith('Light Gunboat')) {
                this.ships[`${f_id}`].swivels = 4;
                this.ships[`${f_id}`].swivelsdecks = '4';
                this.ships[`${f_id}`].cannons = 0;
                this.ships[`${f_id}`].cannonsdecks = '0';
                $(`#fl-${f_id}-cannonsDecks-${1}`).html('0');
                $(`#fl-${f_id}-swivelsDecks-${1}`).html('4');
                $(`#fl-${f_id}-cannonsLabel`).hide('medium','swing');
                $(`#fl-${f_id}-cannonsData`).hide('medium','swing');
            }
        }
    }

    displayShip(ship) {
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']).attr('id',`fl-${ship.f_id}`);
        const cardBody = $('<div>').addClass(['card-body display-card-body']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col']);
        const itemName = $('<input>').addClass(['form-control p-0 border-0 bg-info text-primary bigger-text']).attr({'type':'text','maxlength':'35','id':`fl-${ship.f_id}-nickname`,'value':`${ship.nickname}`});    
        // const itemName = $('<h5>').addClass(['card-title']).text(ship.name);    
        nameColumn.append(itemName);
        const pointColumn = $('<div>').addClass(['col-auto']).html(`${ship.points} pts`).attr('id',`fl-${ship.f_id}-cost`);
        const expandColumn = $('<div>').addClass(['col-auto']);
        expandColumn.html(`
            <a href='#fl-${ship.f_id}-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='fl-${ship.f_id}-expand'></i>
            </a>
            `);
        const removeColumn = $('<div>').addClass(['col-auto']).html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-xmark' id='fl-${ship.f_id}-remove'></i>
            </a>
            `);
        cardHeader.append([nameColumn,pointColumn, expandColumn, removeColumn]);
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `fl-${ship.f_id}-details`).html(`<hr class='border border-2 border-primary rounded-2'>`);
        const leftBox = $('<div>').addClass('col-sm-12 col-md-9 col-xl-10').html(`
            <div>${ship.name}</div>
            <div><b>Size:</b> ${ship.size}</div>
            <div><b>Draft:</b> <span id='fl-${ship.f_id}-draft'>${ship.draft}</span></div>
            <div><b>Speed:</b> <span id='fl-${ship.f_id}-speed'>${ship.topspeed}</span>"</div>
            <div><b>Windward:</b> ${ship.windward}</div>
            <div><b>Turn:</b> ${ship.turn}</div>
            <div><b>Sail Settings:</b> ${ship.sailssettings}</div>
        `);
        // Artillery Deck Layout
        if (ship.swivels > 0) {
            const deckPlan = $('<div>');
            const dpHeader = $('<div>').addClass('row');
            const labelColumn = $('<div>').addClass(`col-auto`)
            const headerLabel = $('<div>').html('<b>Deck</b>');
            labelColumn.append(headerLabel);
            const dataColumn = $('<div>').addClass(`col`);
            const headerColumns = $('<div>').addClass('row g-0');
            for (let i = 0; i < ship.size; i++) {
                const newColumn = $('<div>').addClass(`col col-md-2`).html(`<b>${i+1}</b>`);
                headerColumns.append(newColumn);
            }
            dataColumn.append(headerColumns);
            dpHeader.append(labelColumn, dataColumn);
            // Add Cannons Data
            const gunsLabel = $('<div>').attr('id',`fl-${ship.f_id}-cannonsLabel`).html('Guns');
            const gunsData = $('<div>').addClass('row g-0').attr('id',`fl-${ship.f_id}-cannonsData`);
            for (let i = 0; i < ship.size; i++) {
                const newColumn = $('<div>')
                newColumn.addClass(`col col-md-2`).attr('id',`fl-${ship.f_id}-cannonsDecks-${i+1}`).html(`0`);
                if (ship.cannons > 0) {
                    const gunsPerDeck = ship.cannonsdecks.split('/');
                    newColumn.html(`${gunsPerDeck[i]}`);
                }
                else {
                    gunsLabel.css("display", "none");
                    gunsData.css("display", "none");
                }
                gunsData.append(newColumn);
            }
            labelColumn.append(gunsLabel);
            dataColumn.append(gunsData);
            // Add Swivels Data
            const swivelsLabel = $('<div>').attr('id',`fl-${ship.f_id}-swivelsLabel`).html('Swivels');
            const swivelsData = $('<div>').addClass('row g-0').attr('id',`fl-${ship.f_id}-swivelsData`);
            const swivelsPerDeck = ship.swivelsdecks.split('/');
            for (let i = 0; i < ship.size; i++) {
                const newColumn = $('<div>');
                if (ship.swivels > 0) {
                    newColumn.addClass(`col col-md-2`).attr('id',`fl-${ship.f_id}-swivelsDecks-${i+1}`).html(`${swivelsPerDeck[i]}`);
                }
                else {
                    swivelsLabel.css("display", "none");
                    newColumn.addClass(`col col-md-2`).attr('id',`fl-${ship.f_id}-swivelsDecks-${i+1}`).html(`0`);
                }
                swivelsData.append(newColumn);
            }
            labelColumn.append(swivelsLabel);
            dataColumn.append(swivelsData);
            // Hide Swivels Row if ship cannot have them.
            if (!ship.swivels > 0) {
                swivelsData.css("display", "none");
                swivelsLabel.css("display", "none");
            }              
            // End of Cannons/Swivels Data
            deckPlan.append(dpHeader);
            leftBox.append(deckPlan);
        }
        const rightBox = $('<div>').addClass('col-sm-12 col-md-3 col-xl-2 fell');
        const hullRiggingRow = $('<div>').addClass('row');
        const hullCol = $('<div>').addClass('col-6 col-md-12').html('<b class="text-secondary">Hull</b>');
        for (let i = 0; i < ship.hullfortitude; i++) {
            const newDiv = $('<div>').addClass('row g-0');
            if (i == (ship.hullfortitude - 1)) {
                const newCol = $('<div>').addClass('col').html(`${ship.hullfortitude - i}`)
                newDiv.append(newCol);
            }
            else {
                for (let n = 0; n < ship.hullintegrity; n++) {
                    const newCol = $('<div>').addClass('col').html(`${ship.hullfortitude - i}`)
                    newDiv.append(newCol);
                }
            }
            hullCol.append(newDiv);
            hullRiggingRow.append(hullCol);
        }
        if (ship.riggingfortitude > 0) {
            const riggingCol = $('<div>').addClass('col-6 col-md-12').html('<b class="text-secondary">Rigging</b>');
            for (let i = 0; i < ship.riggingfortitude; i++) {
                const newDiv = $('<div>').addClass('row g-0');
                if (i == (ship.riggingfortitude - 1)) {
                    const newCol = $('<div>').addClass('col').html(`${ship.riggingfortitude - i}`)
                    newDiv.append(newCol);
                }
                else {
                    for (let n = 0; n < ship.riggingintegrity; n++) {
                        const newCol = $('<div>').addClass('col').html(`${ship.riggingfortitude - i}`)
                        newDiv.append(newCol);
                    }
                }
                riggingCol.append(newDiv);
                hullRiggingRow.append(riggingCol);
            }
        }
        rightBox.append(hullRiggingRow)
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
            const componentName = $('<div>').addClass('fell text-primary bigger-text').text('Ships');
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
        $(`#fl-${ship.f_id}-nickname`).on('keyup change', () => {
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
        if (!Object.keys(newUnit).includes('f_id')) {
            newUnit['f_id'] = this.generateId();
        }
        if (!Object.keys(newUnit).includes('qty')) {
            newUnit['qty'] = this.unitMin;
        }
        newUnit['modelsCost'] = newUnit.points * newUnit.qty;
        newUnit['perUnitCost'] = 0;
        newUnit['totalUnitCost'] = newUnit.modelsCost + newUnit.perUnitCost;
        const unitoptions = JSON.parse(sessionStorage.getItem('unitoption'));
        if (this.faction.factioneffects != []) {
            for (const effect of this.faction.factioneffects) {
                if (effect.unitoption_id && !effect.forceoption_id) {
                    for (const unitoption of unitoptions) {
                        if (unitoption.id == effect.unitoption_id && (unitoption.unit_id == newUnit.id || !unitoption.unit_id)) {
                            newUnit.option.push(unitoption);
                        }
                    }
                }
            }
        }
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
                        if (!fe.unit_id || fe.unit_id == newUnit.id) {
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
        this.displayUnit(this.units[`${newUnit.f_id}`]);
        // Add any applyall unit options that have been selected.
        for (const unit_f_id in this.units) {
            if (this.units[`${unit_f_id}`].id == newUnit.id && unit_f_id != newUnit.f_id) {
                for (const o of this.units[`${unit_f_id}`].option) {
                    if (o.selected == 1 && o.applyall == 1) {
                        for (const new_o of this.units[`${newUnit.f_id}`].option) {
                            if (new_o.id == o.id) {
                                new_o.selected = 1;
                                $(`#fl-${newUnit.f_id}-option-${new_o.id}`).prop('checked', true);
                                this.adjustUnitCost(newUnit.f_id, new_o, 1);
                                if (new_o.experienceupg) {
                                    this.units[`${newUnit.f_id}`].experience_id += new_o.experienceupg;
                                    this.units[`${newUnit.f_id}`].setUnitExperienceName();
                                    $(`#fl-${newUnit.f_id}-exp-name`).html(this.units[`${newUnit.f_id}`].experience_name);
                                }                                    
                            }
                        }
                    }
                }
            }
        }
        this.updateTotalForcePoints();
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
        $unitSizeRangeDisplay.html(`<i>${this.unitMin} to ${this.unitMax} Models per Unit</i>`);
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
            this.units[`${f_id}`].perUnitCost = 0;
            for (const o of this.units[`${f_id}`].option) {
                if (o.perxmodels && o.selected) {
                    this.units[`${f_id}`].perUnitCost += Math.floor(this.units[`${f_id}`].qty / o.perxmodels) * o.pointsperunit;
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
            this.units[`${f_id}`].perUnitCost += Math.floor(this.units[`${f_id}`].qty / o.perxmodels) * o.pointsperunit * addsubtract;
        }
        if (o.pointsperunit && !o.perxmodels) {
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
        const cardBody = $('<div>').addClass(['card-body display-card-body']);
        const cardHeader = $('<div>').addClass(['container-fluid display-card-header']);
        const topRow = $('<div>').addClass(['row mb-0 gy-0'])
        const nameColumn = $('<div>').addClass(['col']);
        const itemName = $('<input>').addClass(['form-control p-0 border-0 bg-info text-primary bigger-text']).attr({'type':'text','maxlength':'35','id':`fl-${unit.f_id}-nickname`,'value':`${unit.nickname}`});    
        nameColumn.append(itemName);
        const expandColumn = $('<div>').addClass(['col-auto']);
        expandColumn.html(`
            <a href='#fl-${unit.f_id}-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='fl-${unit.f_id}-expand'></i>
            </a>
            `);
        const removeColumn = $('<div>').addClass(['col-auto']);
        removeColumn.html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-xmark text-primary' id='fl-${unit.f_id}-remove'></i>
            </a>
            `)
        topRow.append([nameColumn,expandColumn,removeColumn]);
        const secondRow =  $('<div>').addClass(['row mt-0 gy-0']);
        const pointsEach = $('<div>').addClass(['col-auto col-md-3 d-flex align-items-end']).html(`<span class='text-secondary bigger-text' id='fl-${unit.f_id}-points'>${unit.points}</span>&nbsp;pts ea`);
        const pointAdjuster = $('<div>').addClass(['col-auto col-md-3 d-flex align-items-end']);
            const subtractModel = $('<span>').html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-minus text-secondary align-self-center' id='fl-${unit.f_id}-subtract-model'></i>
            </a>
            `)
            const modelQty = $(`<span id='fl-${unit.f_id}-qty'>`).addClass(['bigger-text ms-2 me-2']).html(`${unit.qty}`);
            const addModel = $('<span>').html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-plus text-secondary align-self-center' id='fl-${unit.f_id}-add-model'></i>
            </a>
            `)
            pointAdjuster.append(subtractModel,modelQty,addModel);
        const perUnitCost = $('<div>').addClass(['col-auto col-md-3 d-flex align-items-end justify-content-middle']).html(`+ <span class='text-secondary bigger-text' id='fl-${unit.f_id}-per-cost'>${unit.perUnitCost}</span>&nbsp;pts`);
        const pointsUnit = $('<div>').addClass(['col-auto col-md-3 text-center text-primary bigger-text']).html(`<span class='text-secondary' id='fl-${unit.f_id}-total-cost'>${unit.totalUnitCost}</span> pts`);
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
                const containerName = $('<div>').addClass('fell text-primary bigger-text').text('Core Units');
                $('#force-core-units').prepend(containerName);
                $('#force-core-units').show('medium','swing');
            }
            $('#force-core-units').append(newItem);
        }
        else if (unit.class == 'support') {
            if (this.supportCount == 1) {
                const containerName = $('<div>').addClass('fell text-primary bigger-text').text('Support Units');
                $('#force-support-units').prepend(containerName);
                $('#force-support-units').show('medium','swing');
            }$('#force-support-units').append(newItem);
        }
        newItem.show('medium','swing');
        // Handle updates to nickname.
        $(`#fl-${unit.f_id}-nickname`).on('keyup change', () => {
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

    addMisc(newMisc) {
        if (!Object.keys(newMisc).includes('f_id')) {
            newMisc['f_id'] = this.generateId();
        }
        this.misc[`${newMisc.f_id}`] = newMisc;
        this.updateMiscCost(newMisc.f_id);
        this.displayMisc(this.misc[`${newMisc.f_id}`]);
    }

    removeMisc(f_id) {
        delete this.misc[`${f_id}`];
        this.updateTotalForcePoints();
    }

    updateMiscCost(f_id) {
        this.misc[`${f_id}`].totalCost = this.misc[`${f_id}`].points * this.misc[`${f_id}`].qty;
        this.updateTotalForcePoints();
        $(`#fl-${f_id}-points`).html(this.misc[`${f_id}`].points);
        $(`#fl-${f_id}-qty`).html(this.misc[`${f_id}`].qty);
        $(`#fl-${f_id}-total-cost`).html(this.misc[`${f_id}`].totalCost);
    }

    updateAllMiscCost() {
        let allMiscCost = 0;
        const misc = this.misc;
        for (const f_id in misc) {
            allMiscCost = allMiscCost + this.misc[`${f_id}`].totalCost;
        }
        this.allMiscCost = allMiscCost;
    }

    // Takes a ForceList's custom item's unique identifier with a positive or
    // negative integer and adjusts the custom/misc qty.
    adjustMiscQty(f_id,adj) {
        if (this.misc[`${f_id}`].qty + adj < 1) {
            return
        }
        else {
            this.misc[`${f_id}`].qty = this.misc[`${f_id}`].qty + adj;
            this.updateMiscCost(f_id);
        }
    }

    displayMisc(misc) {
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']).attr('id',`fl-${misc.f_id}`);
        const cardBody = $('<div>').addClass(['card-body display-faction-commander']);
        const cardHeader = $('<div>').addClass(['container-fluid']);
        const topRow = $('<div>').addClass(['row mb-0 gy-0'])
        const nameColumn = $('<div>').addClass(['col']);
        // Custom Item name input.
        const itemName = $('<input>').addClass(['form-control p-0 border-0 bg-info text-primary fell bigger-text']).attr({'type':'text','maxlength':'35','id':`fl-${misc.f_id}-name`,'value':`${misc.name}`});    
        nameColumn.append(itemName);
        const expandColumn = $('<div>').addClass(['col-auto']).html(`
            <a href='#fl-${misc.f_id}-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='fl-${misc.f_id}-expand'></i>
            </a>
            `);
        const removeColumn = $('<div>').addClass(['col-auto']).html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-xmark text-primary' id='fl-${misc.f_id}-remove'></i>
            </a>
            `)
        topRow.append([nameColumn,expandColumn,removeColumn]);
        const secondRow = $('<div>').addClass(['row mb-0 gy-0'])
        const pointsEach = $('<div>').addClass(['col-auto col-md-4']);
        const pointsEachRow = $('<div>').addClass('row mt-1');
        const pointsEachColA = $('<div>').addClass('col-sm-auto mx-0 d-flex align-items-baseline').html(`Point&nbsp;Cost:`);
        const pointsEachColB = $('<div>').addClass('col');
        // Custom Item points input.
        const pointsInput = $('<input>').addClass(['form-control py-0 mt-1 border-0 bg-info text-secondary bigger-text']).attr({'type':'number','style':'width: 75px','id':`fl-${misc.f_id}-points`,'value':`${misc.points}`});    
        pointsEachColA.append(pointsInput);
        pointsEachRow.append(pointsEachColA,pointsEachColB);
        pointsEach.append(pointsEachRow);
        const pointAdjuster = $('<div>').addClass(['col-auto col-md-4 d-flex align-items-end justify-content-center']);
            const subtractQty = $('<span>').html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-minus text-secondary align-self-center' id='fl-${misc.f_id}-subtract-model'></i>
            </a>
            `)
            const qty = $(`<span id='fl-${misc.f_id}-qty'>`).addClass(['bigger-text ms-2 me-2']).html(`${misc.qty}`);
            const addQty = $('<span>').html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-plus text-secondary align-self-center' id='fl-${misc.f_id}-add-model'></i>
            </a>
            `)
            pointAdjuster.append(subtractQty,qty,addQty);
        const pointsMisc = $('<div>').addClass(['col-auto col-md-4 d-flex align-items-end justify-content-end text-primary bigger-text']).html(`<span class='text-secondary' id='fl-${misc.f_id}-total-cost'>${misc.totalCost}</span>&nbsp;pts`);
        secondRow.append(pointsEach,pointAdjuster,pointsMisc);
        cardHeader.append([topRow, secondRow]);
        // Text Area for Custom item description.
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `fl-${misc.f_id}-details`).html(`
            <hr class='border border-2 border-primary rounded-2'>
            <div>
                <textarea class='form-control bg-info border-secondary text-primary fell' id='fl-${misc.f_id}-description'>${misc.details}</textarea>
            </div>
        `);
        cardBody.append(cardHeader, cardDetails);
        newItem.append(cardBody);
        if (Object.keys(this.misc).length == 1) {
            const componentName = $('<div>').addClass('fell text-primary bigger-text').text('Custom');
            $('#force-misc').prepend(componentName);
            $('#force-misc').show('medium','swing');
        }
        newItem.hide();
        $('#force-misc').append(newItem);
        newItem.show('medium','swing');
        // Handle updates to name.
        $(`#fl-${misc.f_id}-name`).on('keyup change', () => {
            this.misc[`${misc.f_id}`]['name'] = $(`#fl-${misc.f_id}-name`).val();
        });
        // Handle updates to points.
        $(`#fl-${misc.f_id}-points`).on('change', () => {
            this.misc[`${misc.f_id}`]['points'] = parseInt($(`#fl-${misc.f_id}-points`).val());
            this.updateMiscCost(`${misc.f_id}`);
        });
        // Handle updates to description/details.
        $(`#fl-${misc.f_id}-details`).on('keyup change', () => {
            this.misc[`${misc.f_id}`]['details'] = $(`#fl-${misc.f_id}-description`).val();
        });
        // Handle expanding/contracting of item information.
        $(`#fl-${misc.f_id}-expand`).parent().on('click', () => {
            $(`#fl-${misc.f_id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        // Handle minus button to decrease qty.
        $(`#fl-${misc.f_id}-subtract-model`).on('click', () => {
            this.adjustMiscQty(misc.f_id,-1);
        });
        // Handle plus button to increase qty.
        $(`#fl-${misc.f_id}-add-model`).on('click', () => {
            this.adjustMiscQty(misc.f_id,1);
        });
        // Handle removal of misc from ForceList.
        $(`#fl-${misc.f_id}-remove`).parent().on('click', () => {
            this.removeMisc(misc.f_id);
            $(`#fl-${misc.f_id}`).hide('medium','swing');
            setTimeout(() => {
                $(`#fl-${misc.f_id}`).remove();
                if (Object.keys(this.misc).length == 0) {
                    $(`#force-misc`).hide('medium','swing');
                    setTimeout(() => {
                        $(`#force-misc`).empty();
                    }, 500)
                }
            }, 500)
        });
    }
}