const savedListData = $('#user-saved-lists').data('saved-lists')

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
    sessionStorage.setItem('weaponequipment', JSON.stringify(response.data.weaponequipment));
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

function getNationName(id) {
    let nationalityName = 'Spain';
    if (id == 2) {
        nationalityName = 'England';
    }
    else if (id == 3) {
        nationalityName = 'France';
    }
    else if (id == 4) {
        nationalityName = 'Unaligned & Peripheral Powers';
    }
    else if (id == 5) {
        nationalityName = 'Dutch';
    }
    else if (id == 6) {
        nationalityName = 'Pirates';
    }
    else if (id == 8) {
        nationalityName = 'Native Americans';
    }    
    return nationalityName
}

$(window).ready(async function() {
    // Get Universal Data as needed.
    if (sessionStorage.getItem('nationality') == null) {
        await requestUniversalData();
    }

    for (const list of savedListData) {
        const nationName = getNationName(list.nationality_id);
        // If list Nation option is not already in sesstion storage,
        // send request for data and add to session storage.
        if (sessionStorage.getItem(nationName) == null) {
            const response = await axios.get(`/nationalities/${list.nationality_id}`);
            storeFactionsAndCommanders(response);
        }
        // Get Nationality data from session.
        const nationalityData = JSON.parse(sessionStorage.getItem(`${nationName}`));
        // Update Saved List Table with Nation name.
        $(`#list-${list.uuid}-nationality`).html(`${nationalityData.nationality.name}`);
        // Update Saved List Table with Faction name.
        const nationalFactionList = JSON.parse(sessionStorage.getItem(`${nationName}_factions`));
        const selectedFaction = nationalFactionList.find(faction => faction.id == list.faction_id);
        $(`#list-${list.uuid}-faction`).html(`${selectedFaction.name}`);
        // Handlers for removing saved list.
        $(`#${list.uuid}-remove`).parent().on('click',async () => {
            const response = await axios.get(`/lists/${list.uuid}/delete`);
            $(`#${list.uuid}-remove`).parent().parent().parent().hide('medium','swing');
        });
    }

    $('#main-area').show('slow','swing');
});