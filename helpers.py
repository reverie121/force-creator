def addSpecialruleToList(rule, specialruleList, specialruleIds):
    if rule['id'] not in specialruleIds:
        specialruleList.append({"name": rule['name'], "details": rule['details']})
        specialruleIds.append(rule['id'])

def prepPdfData(force_list_data):       
    pdf_data = {
        "name": force_list_data.get('name', 'Unknown'),
        "nationality": force_list_data.get('nationality', {}).get('name', str(force_list_data.get('nationality_id', ''))),
        "faction": {
            "name": force_list_data.get('faction', {}).get('name', str(force_list_data.get('faction_id', ''))),
            "first_year": force_list_data.get('faction', {}).get('first_year', 0),
            "last_year": force_list_data.get('faction', {}).get('last_year', 0),
            "specialrule": [],
            "option": []
        },
        "commander": {
            "name": force_list_data.get('commander', {}).get('name', str(force_list_data.get('commander_id', ''))),
            "nickname": force_list_data.get('commander', {}).get('nickname', force_list_data.get('commandernickname', '')),
            "horseoption": force_list_data.get('commander', {}).get('horseoption', force_list_data.get('commanderhorseselected', 0)),
            "commandpoints": force_list_data.get('commander', {}).get('commandpoints', 0),
            "commandrange": force_list_data.get('commander', {}).get('commandrange', 0),
            "mainweapons": force_list_data.get('commander', {}).get('mainweapons', ''),
            "sidearms": force_list_data.get('commander', {}).get('sidearms', ''),
            "specialrule": []
        },
        "units": [],
        "characters": [],
        "artillery": [],
        "ships": [],
        "misc": [],
        "specialrule": [],
        "specialruleids": [],
        "shiptrait": [],
        "shiptraitids": []
    }

    # Safely convert numeric fields to integers
    try:
        pdf_data["totalforcepoints"] = int(force_list_data.get('totalForcePoints', 0))
    except (ValueError, TypeError):
        pdf_data["totalforcepoints"] = 0
    try:
        pdf_data["maxpoints"] = int(force_list_data.get('maxPoints', 0))
    except (ValueError, TypeError):
        pdf_data["maxpoints"] = 0
    try:
        pdf_data["modelcount"] = int(force_list_data.get('modelCount', 0))
    except (ValueError, TypeError):
        pdf_data["modelcount"] = 0
    try:
        pdf_data["strikepointsevery"] = int(force_list_data.get('strikePointsEvery', 0))
    except (ValueError, TypeError):
        pdf_data["strikepointsevery"] = 0

    # Get PDF options, defaulting to True if not present
    pdf_options = force_list_data.get('pdfOptions', {})
    include_special_rules = pdf_options.get('includeSpecialRules', True)
    include_ship_traits = pdf_options.get('includeShipTraits', True)

    # Faction special rules (always included)
    for rule in force_list_data.get('faction', {}).get('specialrule', []):
        pdf_data['faction']['specialrule'].append({"details": rule['details']})

    # Faction options (always included, not tied to pdfOptions)
    for option in force_list_data.get('faction', {}).get('option', []):
        if option['selected'] == 1:
            pdf_data['faction']['option'].append({"name": option['name'], "details": option['details']})

    # Commander special rules (always included)
    for rule in force_list_data.get('commander', {}).get('specialrule', []):
        pdf_data['commander']['specialrule'].append({"name": rule['name']})
        if include_special_rules:  # Only add to summary list if checked
            addSpecialruleToList(rule, pdf_data['specialrule'], pdf_data['specialruleids'])
    if force_list_data.get('commander', {}).get('specialruleChoice', []) != []:
        for rule in force_list_data.get('commander', {}).get('specialruleChoice', []):
            if rule['id'] in force_list_data.get('commander', {}).get('specialruleChosenIDs', []):
                pdf_data['commander']['specialrule'].append({"name": rule['name']})
                if include_special_rules:  # Only add to summary list if checked
                    addSpecialruleToList(rule, pdf_data['specialrule'], pdf_data['specialruleids'])

    # Units
    for f_id in force_list_data.get('units', {}):
        unit = force_list_data['units'][f_id]
        new_unit = {
            "fid": unit['f_id'],
            "name": unit['name'],
            "nickname": unit['nickname'], 
            "class": unit['class'].capitalize(), 
            "experience_name": unit['experience_name'], 
            "perUnitCost": unit['perUnitCost'], 
            "qty": unit['qty'], 
            "points": unit['points'], 
            "totalUnitCost": unit['totalUnitCost'], 
            "fightskill": unit['fightskill'], 
            "fightsave": unit['fightsave'], 
            "shootskill": unit['shootskill'], 
            "shootsave": unit['shootsave'], 
            "resolve": unit['resolve'], 
            "mainweapons": unit['mainweapons'], 
            "sidearms": unit['sidearms'], 
            "specialrule": [], 
            "option": []
        }
        for rule in unit.get('specialrule', []):
            new_unit['specialrule'].append({"name": rule['name']})
            if include_special_rules:  # Only add to summary list if checked
                addSpecialruleToList(rule, pdf_data['specialrule'], pdf_data['specialruleids'])
        for option in unit.get('option', []):
            if option['selected'] == 1:
                new_unit['option'].append({"name": option['name'], "details": option['details']})
        pdf_data['units'].append(new_unit)

    # Characters
    for f_id in force_list_data.get('characters', {}):
        character = force_list_data['characters'][f_id]
        new_character = {
            "fid": character['f_id'],
            "name": character['name'],
            "nickname": character['nickname'], 
            "charactertype": character['charactertype'], 
            "commandpoints": character['commandpoints'], 
            "commandrange": character['commandrange'], 
            "commandpointconditions": character['commandpointconditions'], 
            "unitrestrictions": character['unitrestrictions'], 
            "extraabilities": character['extraabilities'],
            "specialrule": []
        }
        for rule in character.get('specialrule', []):
            new_character['specialrule'].append({"name": rule['name']})
            if include_special_rules:  # Only add to summary list if checked
                addSpecialruleToList(rule, pdf_data['specialrule'], pdf_data['specialruleids'])
        pdf_data['characters'].append(new_character)

    # Artillery
    for f_id in force_list_data.get('artillery', {}):
        artillery = force_list_data['artillery'][f_id]
        new_artillery = {
            "fid": artillery['f_id'],            
            "name": artillery['name'],
            "nickname": artillery['nickname'], 
            "qty": artillery['qty'], 
            "points": artillery['points'], 
            "optionCost": 0, 
            "totalCost": artillery['totalCost'], 
            "d10": artillery['d10'], 
            "minimumcrew": artillery['minimumcrew'], 
            "arcfire": artillery['arcfire'], 
            "shootbase": artillery['shootbase'], 
            "movepenalty": artillery['movepenalty'], 
            "reloadmarkers": artillery['reloadmarkers'], 
            "option": []              
        }
        for option in artillery.get('option', []):
            if 'selected' in option and option['selected'] == 1:
                new_artillery['option'].append({"name": option['name'], "rules": option['rules']})
                new_artillery['optionCost'] += option['pointcost']
                new_artillery['totalCost'] += option['pointcost']
        pdf_data['artillery'].append(new_artillery)

    # Ships
    ship_traits = []
    for f_id in force_list_data.get('ships', {}):
        ship = force_list_data['ships'][f_id]
        new_ship = {
            "fid": ship['f_id'],            
            "name": ship['name'],
            "nickname": ship['nickname'], 
            "size": ship['size'], 
            "draft": ship['draft'], 
            "topspeed": ship['topspeed'], 
            "windward": ship['windward'], 
            "turn": ship['turn'], 
            "sailssettings": ship['sailssettings'], 
            "riggingfortitude": ship['riggingfortitude'], 
            "riggingintegrity": ship['riggingintegrity'], 
            "hullfortitude": ship['hullfortitude'], 
            "hullintegrity": ship['hullintegrity'],                 
            "specialrule": [], 
            "upgrade": []                       
        }
        for rule in ship.get('specialrule', []):
            new_ship['specialrule'].append({"name": rule['name']})
            if include_ship_traits:  # Only add to summary list if checked
                addSpecialruleToList(rule, ship_traits, pdf_data['shiptraitids'])
        for upgrade in ship.get('upgrade', []):
            if upgrade['selected'] == 1:
                new_ship['upgrade'].append({"name": upgrade['name'], "details": upgrade['details']})
        pdf_data['ships'].append(new_ship)

    # Misc
    for f_id in force_list_data.get('misc', {}):
        misc = force_list_data['misc'][f_id]
        new_misc = {
            "fid": misc['f_id'],            
            "name": misc['name'],
            "details": misc['details'],
            "points": misc['points'],
            "qty": misc['qty'], 
            "totalCost": misc['totalCost'],                 
        }
        pdf_data['misc'].append(new_misc)

    # Sort and clean up special rules and ship traits (summary lists only)
    if include_special_rules:
        pdf_data['specialrule'].sort(key=lambda x: x['name'])
    else:
        pdf_data['specialrule'] = []
    del pdf_data['specialruleids']

    if include_ship_traits and ship_traits:
        pdf_data['shiptrait'] = sorted(ship_traits, key=lambda x: x['name'])
    else:
        pdf_data['shiptrait'] = []
    del pdf_data['shiptraitids']

    # Add pdf_options to pdf_data for template access
    pdf_data['pdf_options'] = pdf_options

    return pdf_data

    # Get PDF options, defaulting to True if not present
    pdf_options = force_list_data.get('pdfOptions', {})
    include_special_rules = pdf_options.get('includeSpecialRules', True)
    include_ship_traits = pdf_options.get('includeShipTraits', True)

    # Faction special rules (always included)
    for rule in force_list_data['faction']['specialrule']:
        pdf_data['faction']['specialrule'].append({"details": rule['details']})

    # Faction options (always included, not tied to pdfOptions)
    for option in force_list_data['faction']['option']:
        if option['selected'] == 1:
            pdf_data['faction']['option'].append({"name": option['name'], "details": option['details']})

    # Commander special rules (always included)
    for rule in force_list_data['commander']['specialrule']:
        pdf_data['commander']['specialrule'].append({"name": rule['name']})
        if include_special_rules:  # Only add to summary list if checked
            addSpecialruleToList(rule, pdf_data['specialrule'], pdf_data['specialruleids'])
    if force_list_data['commander']['specialruleChoice'] != []:
        for rule in force_list_data['commander']['specialruleChoice']:
            if rule['id'] in force_list_data['commander']['specialruleChosenIDs']:
                pdf_data['commander']['specialrule'].append({"name": rule['name']})
                if include_special_rules:  # Only add to summary list if checked
                    addSpecialruleToList(rule, pdf_data['specialrule'], pdf_data['specialruleids'])

    # Units
    for f_id in force_list_data['units']:
        unit = force_list_data['units'][f_id]
        new_unit = {
            "fid": unit['f_id'],
            "name": unit['name'],
            "nickname": unit['nickname'], 
            "class": unit['class'].capitalize(), 
            "experience_name": unit['experience_name'], 
            "perUnitCost": unit['perUnitCost'], 
            "qty": unit['qty'], 
            "points": unit['points'], 
            "totalUnitCost": unit['totalUnitCost'], 
            "fightskill": unit['fightskill'], 
            "fightsave": unit['fightsave'], 
            "shootskill": unit['shootskill'], 
            "shootsave": unit['shootsave'], 
            "resolve": unit['resolve'], 
            "mainweapons": unit['mainweapons'], 
            "sidearms": unit['sidearms'], 
            "specialrule": [], 
            "option": []
        }
        for rule in unit['specialrule']:
            new_unit['specialrule'].append({"name": rule['name']})
            if include_special_rules:  # Only add to summary list if checked
                addSpecialruleToList(rule, pdf_data['specialrule'], pdf_data['specialruleids'])
        for option in unit['option']:
            if option['selected'] == 1:
                new_unit['option'].append({"name": option['name'], "details": option['details']})
        pdf_data['units'].append(new_unit)

    # Characters
    for f_id in force_list_data['characters']:
        character = force_list_data['characters'][f_id]
        new_character = {
            "fid": character['f_id'],
            "name": character['name'],
            "nickname": character['nickname'], 
            "charactertype": character['charactertype'], 
            "commandpoints": character['commandpoints'], 
            "commandrange": character['commandrange'], 
            "commandpointconditions": character['commandpointconditions'], 
            "unitrestrictions": character['unitrestrictions'], 
            "extraabilities": character['extraabilities'],
            "specialrule": []
        }
        for rule in character['specialrule']:
            new_character['specialrule'].append({"name": rule['name']})
            if include_special_rules:  # Only add to summary list if checked
                addSpecialruleToList(rule, pdf_data['specialrule'], pdf_data['specialruleids'])
        pdf_data['characters'].append(new_character)

    # Artillery
    for f_id in force_list_data['artillery']:
        artillery = force_list_data['artillery'][f_id]
        new_artillery = {
            "fid": artillery['f_id'],            
            "name": artillery['name'],
            "nickname": artillery['nickname'], 
            "qty": artillery['qty'], 
            "points": artillery['points'], 
            "optionCost": 0, 
            "totalCost": artillery['totalCost'], 
            "d10": artillery['d10'], 
            "minimumcrew": artillery['minimumcrew'], 
            "arcfire": artillery['arcfire'], 
            "shootbase": artillery['shootbase'], 
            "movepenalty": artillery['movepenalty'], 
            "reloadmarkers": artillery['reloadmarkers'], 
            "option": []              
        }
        for option in artillery['option']:
            if 'selected' in option and option['selected'] == 1:
                new_artillery['option'].append({"name": option['name'], "rules": option['rules']})
                new_artillery['optionCost'] += option['pointcost']
                new_artillery['totalCost'] += option['pointcost']
        pdf_data['artillery'].append(new_artillery)

    # Ships
    ship_traits = []
    for f_id in force_list_data['ships']:
        ship = force_list_data['ships'][f_id]
        new_ship = {
            "fid": ship['f_id'],            
            "name": ship['name'],
            "nickname": ship['nickname'], 
            "size": ship['size'], 
            "draft": ship['draft'], 
            "topspeed": ship['topspeed'], 
            "windward": ship['windward'], 
            "turn": ship['turn'], 
            "sailssettings": ship['sailssettings'], 
            "riggingfortitude": ship['riggingfortitude'], 
            "riggingintegrity": ship['riggingintegrity'], 
            "hullfortitude": ship['hullfortitude'], 
            "hullintegrity": ship['hullintegrity'],                 
            "specialrule": [], 
            "upgrade": []                       
        }
        for rule in ship['specialrule']:
            new_ship['specialrule'].append({"name": rule['name']})
            if include_ship_traits:  # Only add to summary list if checked
                addSpecialruleToList(rule, ship_traits, pdf_data['shiptraitids'])
        for upgrade in ship['upgrade']:
            if upgrade['selected'] == 1:
                new_ship['upgrade'].append({"name": upgrade['name'], "details": upgrade['details']})
        pdf_data['ships'].append(new_ship)

    # Misc
    for f_id in force_list_data['misc']:
        misc = force_list_data['misc'][f_id]
        new_misc = {
            "fid": misc['f_id'],            
            "name": misc['name'],
            "details": misc['details'],
            "points": misc['points'],
            "qty": misc['qty'], 
            "totalCost": misc['totalCost'],                 
        }
        pdf_data['misc'].append(new_misc)

    # Sort and clean up special rules and ship traits (summary lists only)
    if include_special_rules:
        pdf_data['specialrule'].sort(key=lambda x: x['name'])
    else:
        pdf_data['specialrule'] = []
    del pdf_data['specialruleids']

    if include_ship_traits and ship_traits:
        pdf_data['shiptrait'] = sorted(ship_traits, key=lambda x: x['name'])
    else:
        pdf_data['shiptrait'] = []
    del pdf_data['shiptraitids']

    # Add pdf_options to pdf_data for template access
    pdf_data['pdf_options'] = pdf_options

    return pdf_data