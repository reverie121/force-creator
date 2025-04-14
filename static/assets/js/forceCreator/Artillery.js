class Artillery {
    constructor(item) {
        Object.assign(this, item);
        this.setArtilleryOptions();
        this.nickname = `${this.name} (${this.mounting})`;
    }

    setArtilleryOptions() {
        const weaponEquipment = JSON.parse(sessionStorage.weaponequipment || '[]');
        console.debug('weaponEquipment:', weaponEquipment);
        const grapeshot = weaponEquipment.find(item => item && item.id === 6);
        const chainshot = weaponEquipment.find(item => item && item.id === 7);
        if (!grapeshot || !chainshot) {
            console.error('Failed to find artillery options:', {
                grapeshot: grapeshot || null,
                chainshot: chainshot || null
            });
            this.option = [];
            return;
        }
        this.option = [grapeshot, chainshot];
        console.debug('Artillery options set:', this.option);
    }

    display() {
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']);
        const cardBody = $('<div>').addClass(['card-body display-card-body']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col']);
        const itemName = $('<h5>').addClass(['card-title']).text(`${this.name} (${this.mounting})`);
        nameColumn.append(itemName);
        const pointColumn = $('<div>').addClass(['col-auto']).html(`${this.points} pts`);
        const expandColumn = $('<div>').addClass(['col-auto']);
        expandColumn.html(`
            <a href='#artillery-${this.id}-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='artillery-${this.id}-expand'></i>
            </a>
            `);
            const addColumn = $('<div>').addClass(['col-auto']);
        addColumn.html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-plus text-primary'  id='artillery-${this.id}-add'></i>
            </a>
            `)
        cardHeader.append([nameColumn,pointColumn, expandColumn, addColumn]);
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `artillery-${this.id}-details`).html(`
            <hr class='border border-2 border-primary rounded-2'>
            <div class='row'>
                <div class='col-7'>
                    <b>Dice:</b> ${this.d10}
                </div>
                <div class='col-5'>
                    <b>Crew</b>: ${this.minimumcrew}
                </div>
            </div>
            <div class='row'>
                <div class='col-7'>
                <b>Arc of Fire</b>: ${this.arcfire}
                </div>
                <div class='col-5'>
                <b>Shoot Base</b>: ${this.shootbase}
                </div>
            </div>
            <div class='row'>
                <div class='col-7'>
                <b>Movement Penalty</b>: ${this.movepenalty}"
                </div>
                <div class='col-5'>
                <b>Reload Markers</b>: ${this.reloadmarkers}
                </div>
            </div>
        
        `);
        cardBody.append(cardHeader, cardDetails);
        newItem.append(cardBody);
        $('#menu-item-container').append(newItem);
        // Handle expanding/contracting of item information.
        $(`#artillery-${this.id}-expand`).parent().on('click', () => {
            $(`#artillery-${this.id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        // Handle button for adding artillery to ForceList.
        $(`#artillery-${this.id}-add`).parent().on('click', (e) => {
            e.preventDefault();
            const artilleryToAdd = new Artillery(this);
            forceList.addArtillery(artilleryToAdd);
        });
    }
}