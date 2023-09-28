class Unit {
    constructor(item) {
        Object.assign(this, item);
        this.nickname = this.name
        this.setUnitSpecialruleIDs();
        this.setUnitSpecialrules();
        this.setUnitOptions();
        this.setUnitExperienceName();
    }

    setUnitSpecialruleIDs() {
        const unitSpecialrule = JSON.parse(sessionStorage.getItem('unitspecialrule'));
        const unitSpecialruleIDs = [];
        for (const usr of unitSpecialrule) {
            if (usr.unit_id == this.id) {
                unitSpecialruleIDs.push(usr.specialrule_id);
            }
        }
        this.specialRuleIDs = unitSpecialruleIDs;
    }

    setUnitSpecialrules() {
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

    setUnitExperienceName() {
        if (this.experience_id == 1) {
            this.experience_name ='Inexperienced';
        } else if (this.experience_id == 2) {
            this.experience_name ='Trained';
        } else if (this.experience_id == 3) {
            this.experience_name ='Veteran';
        }
    }

    setUnitOptions() {
        const unitOption = JSON.parse(sessionStorage.getItem('unitoption'));
        const unitOptions = [];
        for (const uo of unitOption) {
            if ((uo.unit_id == this.id && uo.limited == 0) || uo.id == 329 || uo.id == 345) {
                const newOption = {};
                Object.assign(newOption, uo);
                unitOptions.push(newOption);
            }
        }
        this.option = unitOptions;
    }

    // Display method for Unit objects.
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
            <a href='#unit-${this.id}-details' role='button' data-bs-toggle='collapse'>
                <i class='fa-solid fa-chevron-down' id='unit-${this.id}-expand'></i>
            </a>
            `);
            const addColumn = $('<div>').addClass(['col-auto']);
        addColumn.html(`
            <a href='#/' role='button'>
                <i class='fa-solid fa-plus text-primary'  id='unit-${this.id}-add'></i>
            </a>
            `);
        cardHeader.append([nameColumn,pointColumn, expandColumn, addColumn]);
        const cardDetails = $('<div>').addClass(['collapse', 'card-text']).attr('id', `unit-${this.id}-details`).html(`
            <hr class='border border-2 border-primary rounded-2'>
            <div><i>${this.experience_name}</i></div>
            <div class='row'>
                <div class='col-4 text-center'>
                    <b>Fight:</b> ${this.fightskill} / ${this.fightsave}
                </div>
                <div class='col-4 text-center'>
                    <b>Shoot:</b> ${this.shootskill} / ${this.shootsave}
                </div>
                <div class='col-4 text-center'>
                    <b>Resolve:</b> ${this.resolve}
                </div>
            </div>
            <div class='mt-1'>
                <b>Main Weapons</b>:
                <div class='mt-0'>${this.mainweapons}</div>
            </div>
        `);
        if (this.sidearms) {
            const sidearms = $('<div>').addClass('mt-1').html(`<b>Sidearms</b>: ${this.sidearms}`);
            cardDetails.append(sidearms);
        }
        if (this.equipment) {
            const equipment = $('<div>').addClass('mt-1').html(`<b>Equiment</b>: ${this.equipment}`);
            cardDetails.append(equipment);
        }
        if (this.option.length > 0) {
            const optionsCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const unitOptionsHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mb-0'>Unit Options</h5>`);
            const optionExpandColumn = $('<div>').addClass(['col-1']);
            optionExpandColumn.html(`
                <a href='#unit-${this.id}-options-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='unit-${this.id}-options-expand'></i>
                </a>
            `);
            unitOptionsHeader.append([descColumn, optionExpandColumn]);
            const unitOptionsDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `unit-${this.id}-options-details`)
            for (const o of this.option) {
                const newOption = $('<li>').addClass('mt-1').html(`${o.details}`);
                unitOptionsDetails.append(newOption);
            }
            optionsCard.append(unitOptionsHeader, unitOptionsDetails);
            cardDetails.append(optionsCard);
        }
        if (this.specialrule.length > 0) {
            const specialruleCard = $('<div>').html(`<hr class='border border-2 border-primary rounded-2'>`);
            const specialrulesHeader = $('<div>').addClass(['row']);
            const descColumn = $('<div>').addClass(['col-10']).html(`<h5 class='card-title mb-0'>Special Rules</h5>`);
            const specialruleExpandColumn = $('<div>').addClass(['col-1']);
            specialruleExpandColumn.html(`
                <a href='#unit-${this.id}-specialrules-details' role='button' data-bs-toggle='collapse'>
                    <i class='fa-solid fa-chevron-down' id='unit-${this.id}-specialrules-expand'></i>
                </a>
            `);
            specialrulesHeader.append([descColumn, specialruleExpandColumn]);
            const specialrulesDetails = $('<ul>').addClass(['collapse', 'card-text']).attr('id', `unit-${this.id}-specialrules-details`)
            for (const rule of this.specialrule) {
                const newRule = $('<li>').addClass('mt-1').html(`<b>${rule.name}:</b> ${rule.details}`);
                specialrulesDetails.append(newRule);
            }
            specialruleCard.append(specialrulesHeader, specialrulesDetails);
            cardDetails.append(specialruleCard);
        }
        cardBody.append(cardHeader, cardDetails);
        newItem.append(cardBody);
        if (!forceList.faction) {
            $('#menu-item-container').append(newItem);
        }
        else if (forceList.faction.unitClass[`${this.id}`] == 1) {
            $('#core-units').append(newItem);
        }
        else if (forceList.faction.unitClass[`${this.id}`] == 2) {
            $('#support-units').append(newItem);
        }
        // Handle expanding/contracting of item information.
        $(`#unit-${this.id}-expand`).parent().on('click', () => {
            $(`#unit-${this.id}-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
        });
        if (this.option.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#unit-${this.id}-options-expand`).parent().on('click', () => {
                $(`#unit-${this.id}-options-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });            
        }
        if (this.specialrule.length > 0) {
            // Handle expanding/contracting of item information.
            $(`#unit-${this.id}-specialrules-expand`).parent().on('click', () => {
                $(`#unit-${this.id}-specialrules-expand`).toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
            });
        }
        // Handle button for adding unit to ForceList.
        $(`#unit-${this.id}-add`).parent().on('click', (e) => {
            e.preventDefault();
            const unitToAdd = new Unit(this);
            forceList.addUnit(unitToAdd);
        });
    }
}