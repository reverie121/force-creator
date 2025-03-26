def addSpecialruleToList(rule, specialruleList, specialruleIds):
    if rule['id'] not in specialruleIds:
        specialruleList.append({"name": rule['name'], "details": rule['details'], "id": rule['id']})
        specialruleIds.append(rule['id'])

def prepPdfData(force_list_data):       
    pdf_data = {
        "name": force_list_data['name'],
        "nationality": force_list_data['nationality']['name'],
        "totalForcePoints": force_list_data['totalForcePoints'],
        "maxPoints": force_list_data['maxPoints'],
        "modelCount": force_list_data['modelCount'],
        "strikePointsEvery": force_list_data['strikePointsEvery'],
        "faction": {
            "name": force_list_data['faction']['name'],
            "first_year": force_list_data['faction']['first_year'],
            "last_year": force_list_data['faction']['last_year'], 
            "specialrule": [], 
            "option": []
        }, 
        "commander": {
            "name": force_list_data['commander']['name'],
            "nickname": force_list_data['commander']['nickname'],
            "horseoption": force_list_data['commander']['horseoption'],
            "commandpoints": force_list_data['commander']['commandpoints'],
            "commandrange": force_list_data['commander']['commandrange'],
            "mainweapons": force_list_data['commander']['mainweapons'],
            "sidearms": force_list_data['commander']['sidearms'], 
            "specialrule": []
        }, 
        "units": [], 
        "characters": [], 
        "artillery": [], 
        "ships": [], 
        "misc": [], 
        "specialrule": [], 
        "specialruleIds": [], 
        "shiptrait": [], 
        "shiptraitIds": []
    }

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
            addSpecialruleToList(rule, pdf_data['specialrule'], pdf_data['specialruleIds'])
    if force_list_data['commander']['specialruleChoice'] != []:
        for rule in force_list_data['commander']['specialruleChoice']:
            if rule['id'] in force_list_data['commander']['specialruleChosenIDs']:
                pdf_data['commander']['specialrule'].append({"name": rule['name']})
                if include_special_rules:  # Only add to summary list if checked
                    addSpecialruleToList(rule, pdf_data['specialrule'], pdf_data['specialruleIds'])

    # Units
    for f_id in force_list_data['units']:
        unit = force_list_data['units'][f_id]
        new_unit = {
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
                addSpecialruleToList(rule, pdf_data['specialrule'], pdf_data['specialruleIds'])
        for option in unit['option']:
            if option['selected'] == 1:
                new_unit['option'].append({"name": option['name'], "details": option['details']})
        pdf_data['units'].append(new_unit)

    # Characters
    for f_id in force_list_data['characters']:
        character = force_list_data['characters'][f_id]
        new_character = {
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
                addSpecialruleToList(rule, pdf_data['specialrule'], pdf_data['specialruleIds'])
        pdf_data['characters'].append(new_character)

    # Artillery
    for f_id in force_list_data['artillery']:
        artillery = force_list_data['artillery'][f_id]
        new_artillery = {
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
                addSpecialruleToList(rule, ship_traits, pdf_data['shiptraitIds'])
        for upgrade in ship['upgrade']:
            if upgrade['selected'] == 1:
                new_ship['upgrade'].append({"name": upgrade['name'], "details": upgrade['details']})
        pdf_data['ships'].append(new_ship)

    # Misc
    for f_id in force_list_data['misc']:
        misc = force_list_data['misc'][f_id]
        new_misc = {
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
    del pdf_data['specialruleIds']

    if include_ship_traits and ship_traits:
        pdf_data['shiptrait'] = sorted(ship_traits, key=lambda x: x['name'])
    else:
        pdf_data['shiptrait'] = []
    del pdf_data['shiptraitIds']

    # Add pdf_options to pdf_data for template access
    pdf_data['pdf_options'] = pdf_options

    return pdf_data