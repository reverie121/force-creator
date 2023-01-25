const $componentSelector = $('#component_selector');




$componentSelector.on('change', async function(e) {
    
    if ($componentSelector.val() == 'artillery') {
        const response = await axios.get('/artillery');
        console.log(response);
    }

    else if ($componentSelector.val() == 'ships') {
        const response = await axios.get('/ships');
        console.log(response);
    }

});