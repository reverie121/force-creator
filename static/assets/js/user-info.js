const savedListData = $('#user-saved-lists').data('saved-lists')

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