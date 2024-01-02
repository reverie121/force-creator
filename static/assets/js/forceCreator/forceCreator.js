// Create new ForceList object to use throughout process.
const forceList = new ForceList(150);

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
    // Hide or show Artillery option based on Faction
    if ('faction' in forceList) {
        if (forceList.faction.artilleryallowed == 0) {
            $("#component_selector option[value='artillery']").hide();
        }
        else {
            $("#component_selector option[value='artillery']").show();
        }
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
        $('#add-custom-button').hide('medium', 'swing');
        if (!forceList.save) {
            $('#force-revert').hide('fast', 'swing');            
        }
        $('#force-revert').hide('fast', 'swing');
        $('#force-save').hide('fast', 'swing');
        $('#force-pdf').hide('fast', 'swing');
    } else {
        $('#component-instructions').hide('fast', 'swing');
        $('#add-custom-button').show('medium', 'swing');
        $('#component_selector').show('medium', 'swing');
        if (forceList.save) {
            $('#force-revert').show('fast', 'swing');            
        }
        $('#force-save').show('fast', 'swing');
        $('#force-pdf').show('fast', 'swing');
    }
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
    $('#force-revert').on('click', () => {
        forceList.loadSave(forceList.save);
    })
    $('#force-save').on('click', () => {
        forceList.saveList();
    })
    $('#force-pdf').on('click', () => {
        forceList.saveListToPDF();
    })    
    // Handle button for adding custom/misc to ForceList.
    $(`#add-custom-button`).on('click', () => {
        const customToAdd = new Misc();
        forceList.addMisc(customToAdd);
    });
    $('#main-area').show('slow','swing');
    if ($("#build-side").data("list-save") != '') {
        const saveData = $("#build-side").data("list-save");
        forceList.loadSave(saveData);
    }
});

// Change the Force's Title in response to user input. *****
$forceName.on('keyup change', () => {
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
        const fightingMan = $('<div>').addClass(['collapse rounded-2', 'force-selector-field','p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'fighting-man-characters').html(`<span class='fell bigger-text'>Fighting Men & Women</span>`);
        const hostageAdvisor = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'hostage-advisor-characters').html(`<span class='fell bigger-text'>Hostages & Advisors</span>`);
        $('#menu').append(fightingMan,hostageAdvisor);
        fightingMan.show('medium', 'swing');
        hostageAdvisor.show('medium', 'swing');
    }
    else if (selected == 'ship') {
        const canoa = $('<div>').addClass(['collapse rounded-2', 'force-selector-field','p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'canoa-container').html(`<span class='fell bigger-text'>Canoa</span>`);
        const longboat = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'longboat-container').html(`<span class='fell bigger-text'>Longboat</span>`);
        const piragua = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'piragua-container').html(`<span class='fell bigger-text'>Piragua</span>`);
        const bark = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'bark-container').html(`<span class='fell bigger-text'>Bark</span>`);
        const bermudaSloop = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'bermudasloop-container').html(`<span class='fell bigger-text'>Bermuda Sloop</span>`);
        const tartana = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'tartana-container').html(`<span class='fell bigger-text'>Tartana</span>`);
        const sloop = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'sloop-container').html(`<span class='fell bigger-text'>Sloop</span>`);
        const corvette = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'corvette-container').html(`<span class='fell bigger-text'>Corvette</span>`);
        const fluyt = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'fluyt-container').html(`<span class='fell bigger-text'>Fluyt</span>`);
        const brigantine = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'brigantine-container').html(`<span class='fell bigger-text'>Brigantine</span>`);
        const lightFrigate = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'lightfrigate-container').html(`<span class='fell bigger-text'>Light Frigate</span>`);
        const galleon = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'galleon-container').html(`<span class='fell bigger-text'>Galleon</span>`);
        const sixthRateFrigate = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', '6thratefrigate-container').html(`<span class='fell bigger-text'>6th Rate Frigate</span>`);
        $('#menu').append(canoa,longboat,piragua,bark,bermudaSloop,tartana,sloop,corvette,fluyt,brigantine,lightFrigate,galleon,sixthRateFrigate);
        canoa.show('medium', 'swing');
        longboat.show('medium', 'swing');
        piragua.show('medium', 'swing');
        if (forceList.faction.maxshipdecks > 1) {
            bark.show('medium', 'swing');
            bermudaSloop.show('medium', 'swing');
            tartana.show('medium', 'swing');
            sloop.show('medium', 'swing');
            corvette.show('medium', 'swing');
            if (forceList.faction.maxshipdecks > 2) {
                fluyt.show('medium', 'swing');
                brigantine.show('medium', 'swing');
                lightFrigate.show('medium', 'swing');
                if (forceList.faction.maxshipdecks > 3) {
                    galleon.show('medium', 'swing');
                    sixthRateFrigate.show('medium', 'swing');
                }
            }
        }
    }
    else if (selected == 'unit') {
        const core = $('<div>').addClass(['collapse rounded-2', 'force-selector-field','p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'core-units').html(`<span class='fell bigger-text'>Core Units</span>`);
        const support = $('<div>').addClass(['collapse rounded-2', 'force-selector-field', 'p-1', 'm-1', 'border', 'border-2', 'border-secondary']).attr('id', 'support-units').html(`<span class='fell bigger-text'>Support Units</span>`);
        $('#menu').append(core,support);
        core.show('medium', 'swing');
        support.show('medium', 'swing');
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
        // else if (selected == 'misc') {
        //     var menuItem = new Misc(item);
        // }
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