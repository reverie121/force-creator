const savedListData = $('#user-saved-lists').data('saved-lists')


$(window).ready(async function() {

    for (const list of savedListData) {
        $(`#${list.uuid}-remove`).parent().on('click',async () => {
            const response = await axios.get(`/lists/${list.uuid}/delete`);
            $(`#${list.uuid}-remove`).parent().parent().parent().hide('medium','swing');
        });
    }

    $('#main-area').show('slow','swing');
});