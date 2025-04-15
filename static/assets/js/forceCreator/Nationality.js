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
    // with id, name, first_year, and last_year from session storage for dropdown.
    getNationalFactionList() {
        console.debug(`Getting faction list from session storage for ${this.name}.`);
        const factionsData = JSON.parse(sessionStorage.getItem(`${this.name}_factions`));
        const nationalFactionList = [{'id': 0, 'name': 'Be More Specific...'}];
        for (const faction of factionsData) {
            const newFaction = {
                'id': faction.id,
                'name': faction.name,
                'first_year': faction.first_year,
                'last_year': faction.last_year
            };
            nationalFactionList.push(newFaction);
        }
        this.factionList = nationalFactionList;
    }
}