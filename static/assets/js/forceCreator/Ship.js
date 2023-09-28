class Ship {
    constructor(item) {
        Object.assign(this, item);
        this.nickname = this.name;
        this.setShipSpecialruleIDs();
        this.setShipSpecialrules();
        this.setShipUpgrades();
    }

    setShipSpecialruleIDs() {
        const shipSpecialrule = JSON.parse(sessionStorage.getItem('shipspecialrule'));
        const shipSpecialruleIDs = [];
        for (const ssr of shipSpecialrule) {
            if (ssr.ship_id == this.id) {
                shipSpecialruleIDs.push(ssr.specialrule_id);
            }
        }
        this.specialRuleIDs = shipSpecialruleIDs;
    }

    setShipSpecialrules() {
        const specialrule = JSON.parse(sessionStorage.getItem('specialrule'));
        const specialruleList = [];
        for (const sr of specialrule) {
            if (this.specialRuleIDs.includes(sr.id)) {
                const newRule = {};
                Object.assign(newRule, sr);
                specialruleList.push(newRule);
            }
        }
        this.specialrule = specialruleList;
    }

    setShipUpgrades() {
        const shipUpgrade = JSON.parse(sessionStorage.getItem('shipupgrade'));
        const shipUpgrades = [];
        for (const su of shipUpgrade) {
            if (su.ship_id == this.id) {
                const newUpgrade = {};
                Object.assign(newUpgrade, su);
                shipUpgrades.push(newUpgrade);
            }
        }
        this.upgrade = shipUpgrades;
    }

    // Display method for Ships on the menu side.
    display() {
        const newItem = $('<div>').addClass(['card', 'm-1', 'bg-info', 'text-primary', 'border', 'border-2', 'border-secondary', 'fell']);
        const cardBody = $('<div>').addClass(['card-body display-card-body']);
        const cardHeader = $('<div>').addClass(['row']);
        const nameColumn = $('<div>').addClass(['col']);
        const itemName = $('<h5>').addClass(['card-title']).text(this.name);    
        nameColumn.append(itemName);
        const pointColumn = $('<div>').addClass(['col-auto']).html(`${this.points} pts`);
        const expandColumn = $('<div>').addClass(['col-auto']);
        expandColumn.html(`
            <a href='#ship-${this.id}-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='ship-${this.id}-expand'></i>
            </a>
            `);
        const addColumn = $('<div>').addClass(['col-auto']).html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-plus' id='ship-${this.id}-add'></i>
            </a>
            `);
        cardHeader.append([nameColumn,pointColumn, expandColumn, addColumn]);
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `ship-${this.id}-details`).html(`<hr class='border border-2 border-primary rounded-2'>`);
        const leftBox = $('<div>').addClass('col-sm-12 col-md-9 col-xl-10').html(`
            <div><b>Size:</b> ${this.size}</div>
            <div><b>Draft:</b> ${this.draft}</div>
            <div><b>Speed:</b> ${this.topspeed}</div>
            <div><b>Windward:</b> ${this.windward}</div>
            <div><b>Turn:</b> ${this.turn}</div>
            <div><b>Sail Settings:</b> ${this.sailssettings}</div>
        `);
        // Artillery Deck Layout
        if (this.swivels > 0 || this.cannons > 0) {
            const deckPlan = $('<div>');
            const dpHeader = $('<div>').addClass('row');
            const labelColumn = $('<div>').addClass(`col-auto`)
            const headerLabel = $('<div>').html('<b>Deck</b>');
            labelColumn.append(headerLabel);
            const dataColumn = $('<div>').addClass(`col`);
            const headerColumns = $('<div>').addClass('row');
            for (let i = 0; i < this.size; i++) {
                const newColumn = $('<div>').addClass(`col col-md-2`).html(`<b>${i+1}</b>`);
                headerColumns.append(newColumn);
            }
            dataColumn.append(headerColumns);
            dpHeader.append(labelColumn, dataColumn);
            if (this.cannons > 0) {
                const gunsLabel = $('<div>').html('Guns');
                labelColumn.append(gunsLabel);
                const gunsData = $('<div>').addClass('row');
                const gunsPerDeck = this.cannonsdecks.split('/');
                for (let i = 0; i < this.size; i++) {
                    const newColumn = $('<div>').addClass(`col col-md-2`).html(`${gunsPerDeck[i]}`);
                    gunsData.append(newColumn);
                }
                dataColumn.append(gunsData);
            }
            if (this.swivels > 0) {
                const swivelsLabel = $('<div>').html('Swivels');
                labelColumn.append(swivelsLabel);
                const swivelsData = $('<div>').addClass('row');
                const swivelsPerDeck = this.swivelsdecks.split('/');
                for (let i = 0; i < this.size; i++) {
                    const newColumn = $('<div>').addClass(`col col-md-2`).html(`${swivelsPerDeck[i]}`);
                    swivelsData.append(newColumn);
                }
                dataColumn.append(swivelsData);
            }
            deckPlan.append(dpHeader);
            leftBox.append(deckPlan);
        }
        const rightBox = $('<div>').addClass('col-sm-12 col-md-3 col-xl-2 fell');
        const hullRiggingRow = $('<div>').addClass('row');
        const hullCol = $('<div>').addClass('col-6 col-md-12').html('<b class="text-secondary">Hull</b>');
        for (let i = 0; i < this.hullfortitude; i++) {
            const newDiv = $('<div>').addClass('row g-0');
            if (i == (this.hullfortitude - 1)) {
                const newCol = $('<div>').addClass('col').html(`${this.hullfortitude - i}`)
                newDiv.append(newCol);
            }
            else {
                for (let n = 0; n < this.hullintegrity; n++) {
                    const newCol = $('<div>').addClass('col').html(`${this.hullfortitude - i}`)
                    newDiv.append(newCol);
                }
            }
            hullCol.append(newDiv);
            hullRiggingRow.append(hullCol);
        }
        if (this.riggingfortitude > 0) {
            const riggingCol = $('<div>').addClass('col-6 col-md-12').html('<b class="text-secondary">Rigging</b>');
            for (let i = 0; i < this.riggingfortitude; i++) {
                const newDiv = $('<div>').addClass('row g-0');
                if (i == (this.riggingfortitude - 1)) {
                    const newCol = $('<div>').addClass('col').html(`${this.riggingfortitude - i}`)
                    newDiv.append(newCol);
                }
                else {
                    for (let n = 0; n < this.riggingintegrity; n++) {
                        const newCol = $('<div>').addClass('col').html(`${this.riggingfortitude - i}`)
                        newDiv.append(newCol);
                    }
                }
                riggingCol.append(newDiv);
                hullRiggingRow.append(riggingCol);
            }
        }
        rightBox.append(hullRiggingRow)
        const topBox = $('<div>').addClass('row');
        topBox.append(leftBox,rightBox);
        cardDetails.append(topBox);
        if (this.specialrule.length > 0) {
            const specialrulesCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const shipSpecialrulesHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mt-1 mb-0'>Traits</h5>`);
            const specialruleExpandColumn = $('<div>').addClass(['col-1']);
            specialruleExpandColumn.html(`
                <a href='#ship-${this.id}-specialrules-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='ship-${this.id}-specialrules-expand'></i>
                </a>
            `);
            shipSpecialrulesHeader.append([descColumn, specialruleExpandColumn]);
            const shipSpecialrulesDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `ship-${this.id}-specialrules-details`)
            for (const sr of this.specialrule) {
                const newSpecialrule = $('<li>').html(`<b>${sr.name}:</b> ${sr.details}`);
                shipSpecialrulesDetails.append(newSpecialrule);
            }
            specialrulesCard.append(shipSpecialrulesHeader, shipSpecialrulesDetails);
            cardDetails.append(specialrulesCard);
        }
        if (this.upgrade.length > 0) {
            const upgradeCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const upgradeHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mt-1 mb-0'>Upgrades</h5>`);
            const upgradeExpandColumn = $('<div>').addClass(['col-1']);
            upgradeExpandColumn.html(`
                <a href='#ship-${this.id}-upgrades-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='ship-${this.id}-upgrades-expand'></i>
                </a>
            `);
            upgradeHeader.append([descColumn, upgradeExpandColumn]);
            const shipUpgradeDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `ship-${this.id}-upgrades-details`)
            for (const u of this.upgrade) {
                const newUpgrade = $('<li>').html(`<b>${u.name}</b> (${u.pointcost} pts)`);
                const upgradeDetails = $('<div>').html(`${u.details}`);
                newUpgrade.append(upgradeDetails);
                shipUpgradeDetails.append(newUpgrade);
            }
            upgradeCard.append(upgradeHeader, shipUpgradeDetails);
            cardDetails.append(upgradeCard);
        }
        cardBody.append(cardHeader, cardDetails);
        newItem.append(cardBody);
        const model = this.model.toLowerCase().replace(/\s+/g, '');
        $(`#${model}-container`).append(newItem);
        // Handle expanding/contracting of item information.
        $(`#ship-${this.id}-expand`).parent().on('click', () => {
            $(`#ship-${this.id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        if (this.specialrule.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#ship-${this.id}-specialrules-expand`).parent().on('click', () => {
                $(`#ship-${this.id}-specialrules-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });            
        }
        if (this.upgrade.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#ship-${this.id}-upgrades-expand`).parent().on('click', () => {
                $(`#ship-${this.id}-upgrades-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
        }
        // Handle button for adding ship to ForceList.
        $(`#ship-${this.id}-add`).parent().on('click', (e) => {
            e.preventDefault();
            const shipToAdd = new Ship(this);
            forceList.addShip(shipToAdd);
        });
    }
}