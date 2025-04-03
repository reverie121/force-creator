const savedListData = $('#user-saved-lists').data('saved-lists')

// Add Nation data from axios request to session storage.
function storeFactionsAndCommanders(axiosResponse) {
    const nationality = axiosResponse.data.nationality;
    const commanders = axiosResponse.data.commander;
    const factions = axiosResponse.data.faction;
//    console.log(`Adding nation data to session storage for ${nationality.name}.`);
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
        // If list Nation option is not already in session storage,
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
        // Handler for showing delete modal
        $(`#${list.uuid}-remove`).parent().on('click', (e) => {
            e.preventDefault();
            $('#deleteListUuid').val(list.uuid); // Set the uuid in the modal
            $('#deleteListModal').modal('show');
        });
    }

    // Handler for confirm delete button
    $('#confirmDeleteButton').on('click', async () => {
        const uuid = $('#deleteListUuid').val();
        try {
            const response = await axios.get(`/lists/${uuid}/delete`);
            if (response.data.success) {
                $(`#${uuid}-remove`).parent().parent().parent().hide('medium', 'swing');
                $('#deleteListModal').modal('hide');
            } else {
                alert('You are not authorized to delete this list.');
            }
        } catch (error) {
            console.error('Delete failed:', error.response?.data || error.message);
            alert('Failed to delete list. Please try again.');
        }
    });

    $('#main-area').show('slow','swing');
});