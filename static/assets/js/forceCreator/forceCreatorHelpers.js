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