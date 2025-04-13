const savedListData = $('#user-saved-lists').data('saved-lists')

// Add Nation data from axios request to session storage.
function storeFactionsAndCommanders(axiosResponse) {
    const nationality = axiosResponse.data.nationality;
    const commanders = axiosResponse.data.commander;
    const factions = axiosResponse.data.faction;
    sessionStorage.setItem(nationality.name, JSON.stringify(axiosResponse.data));
    sessionStorage.setItem(`${nationality.name}_commanders`, JSON.stringify(commanders));
    sessionStorage.setItem(`${nationality.name}_factions`, JSON.stringify(factions));
}

function getNationName(id) {
    let nationalityName = 'Spain';
    if (id == 2) {
        nationalityName = 'England';
    } else if (id == 3) {
        nationalityName = 'France';
    } else if (id == 4) {
        nationalityName = 'Unaligned & Peripheral Powers';
    } else if (id == 5) {
        nationalityName = 'Dutch';
    } else if (id == 6) {
        nationalityName = 'Pirates';
    } else if (id == 8) {
        nationalityName = 'Native Americans';
    }
    return nationalityName;
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
            $('#deleteListUuid').val(list.uuid);
            $('#deleteListModal').modal('show');
        });
    }

    // Handler for confirm delete button
    $('#confirmDeleteButton').on('click', async () => {
        const uuid = $('#deleteListUuid').val();
        try {
            const response = await axios.post(`/lists/${uuid}/delete`, {}, {
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });
            if (response.data.success) {
                $(`#${uuid}-remove`).parent().parent().parent().hide('medium', 'swing');
                $('#deleteListModal').modal('hide');
                // Optional: Redirect to the user page if a redirect URL is provided
                if (response.data.redirect) {
                    window.location.href = response.data.redirect;
                }
            } else {
                alert('You are not authorized to delete this list.');
            }
        } catch (error) {
            console.error('Delete failed:', error.response?.data || error.message);
            // Provide specific error messages based on the response
            if (error.response?.status === 403) {
                alert('Session expired or invalid request. Please refresh the page and try again.');
            } else if (error.response?.status === 429) {
                alert('Too many requests. Please wait a moment and try again.');
            } else {
                alert('Failed to delete list. Please try again.');
            }
        }
    });

    $('#deleteAccountButton').on('click', function() {
        $('#deleteAccountModal').modal('show');
    });

    $('#confirmDeleteAccountButton').on('click', function() {
        var recaptchaResponse = grecaptcha.getResponse();
        console.debug('reCAPTCHA response on submit:', recaptchaResponse);
        if (!recaptchaResponse) {
            alert('Please complete the reCAPTCHA.');
            return;
        }
        document.getElementById('recaptcha_response_delete').value = recaptchaResponse;
        document.getElementById('delete-user-form').submit();
    });

    $('#main-area').show('slow', 'swing');
});