import os, re
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.types import Integer, String, Text, VARCHAR

import config

cnfg = config.Config()

directory = 'bp_data' # Directory containing csv files to create tables from

engine=create_engine(f'postgresql+psycopg2://postgres:{cnfg.FC_DATABASE_URI}@localhost:5432/bp')

# Start with a fresh schema
with engine.connect() as con:
    con.execute('DROP SCHEMA public CASCADE;')
    con.execute('CREATE SCHEMA public;')

# ******************** BEGIN DATA CLEANUP AND DB POPULATION ********************

tables=[] # list for table names and columns

with engine.connect() as con:
    # Create new tables not present in FB database.
    con.execute('CREATE TABLE commandernationality(id SERIAL PRIMARY KEY, commander_id INT NOT NULL, nationality_id INT NOT NULL, primary_nationality BOOLEAN)')
    con.execute('CREATE TABLE characternationality(id SERIAL PRIMARY KEY, character_id INT NOT NULL, nationality_id INT NOT NULL)')
    con.execute('CREATE TABLE characterfaction(id SERIAL PRIMARY KEY, character_id INT NOT NULL, faction_id INT NOT NULL)')
    con.execute('CREATE TABLE characterspecialrule(id SERIAL PRIMARY KEY, character_id INT NOT NULL, specialrule_id INT NOT NULL)')

# Add new tables to table list.
tables.append({'table_name': 'commandernationality', 'table_columns': ['id', 'commander_id', 'nationality_id', 'primary_nationality']})
tables.append({'table_name': 'characternationality', 'table_columns': ['id', 'character_id', 'nationality_id']})
tables.append({'table_name': 'characterfaction', 'table_columns': ['id', 'character_id', 'faction_id']})
tables.append({'table_name': 'characterspecialrule', 'table_columns': ['id', 'character_id', 'specialrule_id']})


# Instantiate lists for commandereffect and factioneffect
commandereffects = []
factioneffects = []

# Repeat same process for every file in the specified directory.
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)

    # Checking if it is a file
    if os.path.isfile(f):
        try:
            
            # Make dataframe from csv file.
            with open(f, 'r') as file:
                df = pd.read_csv(f)

            ### Begin Data Cleanup ###

            # Get table name from file name.
            if filename == 'data_location.csv':
                table_name = str(filename).replace('data_','').replace('.csv', '')
            else:
                table_name = str(filename).replace('data_bp','').replace('.csv', '')

            # Drop columns with identical data throughout. These can be easily added back if/as needed.
            for col in df.columns:  # Loop through columns in the dataframe.
                if len(df[col].unique()) == 1:  # Get the length of the unique values in column.
                                                # If length == 1 all values in column are identical.
                    print(f'Dropping {col} from {filename} (column values are all identical)')
                    df.drop([col], axis=1, inplace=True)  # Drop the column.

            # Clean up column names.
            df.columns = df.columns.str.replace('bp', '') # Game initials 'bp' must be removed from many column names.
            df.rename(columns=lambda x: re.sub('id$','_id', x), inplace = True) # Add underscores to columns ending w/ 'id'
                                                                                # to be used for Foreign Keys.
            df.rename(columns = {'_id': 'id'}, inplace = True) # Re-set _id column name to 'id' to be used for Primary Key.

            # Specific column changes: 
            if 'nationality' in df.columns: # unit.nationality and commander.nationality should be .nationality_id
                df.rename(columns = {'nationality': 'nationality_id'}, inplace = True)
            if 'experience' in df.columns: # unit.experience should be unit.experience_id
                df.rename(columns = {'experience': 'experience_id'}, inplace = True)

            # Replace card suit names with symbols where needed:
            df.replace(to_replace = ['SPADE','HEART','DIAMOND','CLUB'],value = ['♠︎','♥︎','♦︎','♣︎'], inplace=True, regex=True)

            if table_name == 'artillery':
                df.drop(df['name'].loc[df['name'].isin(['Chainshot','Grapeshot'])].index, inplace=True)                
                df['name'].replace(to_replace = ['Ship pair','on Ship/Structure',' Structure','Field'],value = ['(Pair on Naval Carriage)','(Ship / Structure)',' (Structure)','(Field Carriage)'], inplace=True, regex=True)
                df.sort_values(by=['name'], inplace=True, ascending=False)

            # Create new columns for character table.
            elif table_name == 'character':
                df['charactertype'] = 1 # (1 = Fighting Man).
                df['unitrestrictions'] = ''
                df['extraabilities'] = ''
                df['commandpoints'] = 0
                df['commandrange'] = 0
                df['commandpointconditions'] = ''
                df['nonatives'] = 0
                df['certainnations'] = 0
                df['certainfactions'] = 0
                df['certaincommanders'] = 0
                df['breaklimits'] = 0
                df['onlywithcommander'] = 0
            # Move data around in character table.
                with engine.connect() as con:
                    # Change character type to 2 for Hostages/Advisors.
                    df.loc[df['name'].str.contains('Hostage'), 'charactertype'] = 2
                    # Change no_natives to 1 for Characters that cannot be used with the Native factions.
                    df.loc[df['details'].str.contains('Any but Native'), 'nonatives'] = 1
                    # Change certain_commanders to 1 for Characters that require a specific commander.
                    df.loc[df['details'].str.contains('May only be included in a Force commanded by'), 'certaincommanders'] = 1
                    # Remove everything but the character name from character.name.
                    # Must happen after character type data applied to new column.
                    df['name'].replace(to_replace = ['Character - ','\(Fighting Man\)','\(Fighting Man','\(Fighting Ma','\(Hostage/Advisor\)'],value = ['','','','',''], inplace=True, regex=True)
                    for i_y in df.index:
                        details = df['details'][i_y]
                        details_list = details.splitlines()
                        for line in details_list:
                            if 'Unit Restrictions' in line: # Add data to column.
                                i_x = df.columns.get_loc('unitrestrictions')
                                line_list = line.split(':')
                                restrictions = line_list[1].strip()
                                if restrictions != 'None':
                                    df.iat[i_y,i_x] = restrictions
                            elif 'Command Points:' in line: # Add data to column.
                                i_x = df.columns.get_loc('commandpoints')
                                i_x_conditions = df.columns.get_loc('commandpointconditions')
                                line = line.replace('-','0')
                                line_list = line.split(':')
                                value = int(line_list[1].strip()[:1])
                                conditions = line_list[1][2:].strip()[1:-1]
                                if value > 0:
                                    df.iat[i_y,i_x] = value  
                                if conditions:
                                    conditions_formatted = conditions[0].upper() + conditions[1:] + '.'
                                    df.iat[i_y,i_x_conditions] = conditions_formatted
                            elif 'Command Range:' in line: # Add data to column.
                                i_x = df.columns.get_loc('commandrange')
                                line = line.replace('-','0"')
                                line_list = line.split(':')
                                value = int(line_list[1].strip()[:-1])
                                if value > 0:
                                    df.iat[i_y,i_x] = value
                            elif 'Extra Abilities' in line: # Add data to column.
                                i_x = df.columns.get_loc('extraabilities')
                                line_list = line.split(':')
                                abilities = line_list[1].strip()
                                if not abilities.startswith('-'):
                                    if abilities.startswith('At the start of the battle,'):
                                        df.iat[i_y,i_x] = '<p class="mt-0 mb-0">' + abilities
                                    else:
                                        df.iat[i_y,i_x] = '<p class="mt-0 mb-0">' + abilities + '</p>'
                            else: # Add any additional lines of data for Extra Abilities.
                                if not line.startswith('Nation') and not line.startswith('Special') and not line.startswith('Main') and not line.startswith('"') and line:
                                    i_x = df.columns.get_loc('extraabilities')
                                    current = df['extraabilities'][i_y]
                                    if line.startswith('Rule'):
                                        abilities = current + ' ' + line + '</p>'
                                    elif line.startswith('(may only give'):
                                        abilities = current
                                        i_x_commandpointconditions = df.columns.get_loc('commandpointconditions')
                                        condition = line[1:-1]
                                        df.iat[i_y,i_x_commandpointconditions] = condition[0].upper() + condition[1:]
                                    elif line.startswith('1-'):
                                        abilities = current + '<ul class="mb-0"><li> ' + line + '</li>'
                                    elif line.startswith('6-'):
                                        abilities = current + '<li> ' + line + '</li></ul>'
                                    else:                                    
                                        abilities = current + '<p class="mt-0 mb-0">' + line + '</p>'
                                    df.iat[i_y,i_x] = abilities
                    # Musician, Standard Bearer, and Drummer Boy do not count towards normal Character limits.
                    df.loc[df['id'].isin([11,17,66]), 'breaklimits'] = 1
                    # Change to 1 for characters that must share a unit with the Force Commander.                    
                    df.loc[df['id'].isin([11,17,61]), 'onlywithcommander'] = 1
                    df.loc[df['charactertype'] == 2, 'onlywithcommander'] = 1                    
                    # Drop unused columns
                    df.drop(columns = ['details', 'model', 'uifolder', 'sort'], inplace=True)

            elif table_name == 'commander':
                df.drop(df['id'].loc[df['id'].isin([130,131,132])].index, inplace=True)                
                with engine.connect() as con:
                    for row in df.iterrows():
                        nationality_id = df.columns.get_loc('nationality_id')
                        if row[1][nationality_id] > 0 and row[1][nationality_id] != 7: # Add data from commander table to commandernationality table.
                            con.execute(f'INSERT INTO commandernationality(commander_id,nationality_id, primary_nationality) VALUES({row[1][0]}, {int(row[1][nationality_id])}, true);')
                df.drop(columns = ['nationality_id','nickname','extrainfo'], inplace = True)
                df.loc[~df['id'].isin([39,68,120,133,136,139,140,143,157,159,212,227,233,240,241]), 'details'] = np.NaN
                df.loc[df['id'] == 16, 'unorthodoxforce'] = 'A Force led by this commander may take Sea Dogs, (Native American) Warriors, (Native American) Warrior Musketeers, and (Spanish) Milicianos Indios as Core units.'
                df.loc[df['id'] == 17, 'unorthodoxforce'] = 'A force lead by this commander may take Milicianos Indios (Spanish) and Warrior Musketeers (Native Americans) as Core Units.'
                df.loc[df['id'] == 38, 'unorthodoxforce'] = 'A Force lead by this commander may take Flibustiers as Core units.'
                df.loc[df['id'] == 65, 'unorthodoxforce'] = '(English) Freebooters and (Dutch) Kapers may be taken as Core units in this Force.'
                df.loc[df['id'] == 69, 'unorthodoxforce'] = 'This Force may take (Unaligned) Jewish Militia as a Core unit.'
                df.loc[df['id'] == 72, 'unorthodoxforce'] = 'If leading a Militia force, (Dutch) Kapers are Core units and Freebooters are Support units.'
                df.loc[df['id'] == 89, 'unorthodoxforce'] = 'This force may take Warrior Musketeers as Core units.'
                df.loc[df['id'] == 92, 'unorthodoxforce'] = 'This force may take Warrior Musketeers as Core units.'
                df.loc[df['id'] == 96, 'unorthodoxforce'] = 'Flibustier units in this Force may add Horses for 4 points (not per model). While mounted, these units apply a +1 penalty to all Fight and Shoot saves.'
                df.loc[df['id'] == 99, 'unorthodoxforce'] = 'This Force treats all Support units as Core units but may not include Milice Canadienne, Milices à Cheval, or Coureur de Bois.'
                df.loc[df['id'] == 108, 'unorthodoxforce'] = 'This Force may take Warriors (Native American) and Warrior Musketeers (Native American) as Core units.'
                df.loc[df['id'] == 117, 'unorthodoxforce'] = 'This Force may include Indian Fighters, (Native American) Warriors, and (Native American) Warrior Musketeers as Core Units.'
                df.loc[df['id'] == 135, 'unorthodoxforce'] = 'Milice Canadienne may be included as Support units.'
                df.loc[df['id'] == 142, 'unorthodoxforce'] = 'This Force may take Braves as Core units'
                df.loc[df['id'] == 149, 'unorthodoxforce'] = 'Kapers (Core), Freebooters (Support)'
                df.loc[df['id'] == 150, 'unorthodoxforce'] = 'Braves (Core), Boslopers (Core)'
                df.loc[df['id'] == 152, 'unorthodoxforce'] = 'This Force may include Indian Fighters, Warriors, and Braves as Core Units.'
                df.loc[df['id'] == 159, 'unorthodoxforce'] = 'Braves (Core)'
                df.loc[df['id'] == 160, 'unorthodoxforce'] = 'Braves (Core)'
                df.loc[df['id'] == 171, 'unorthodoxforce'] = 'A Force led by this Commander may include Marins and Late Flibustiers as Core units.'
                df.loc[df['id'] == 208, 'unorthodoxforce'] = 'A Force led by this Commander may include Braves (Native American) as Core units.'
                df['horseoption'] = 0
                df.loc[df['id'].isin([2,3,4,7,8,9,10,11,12,26,27,28,71,73,74,75,93,94,95,96,99,100,101,102,118,121,126,127,129]), 'horseoption'] = 1
                df.loc[df['commanderclass_id'] == 1, 'horseoption'] = 1
                df.sort_values(by=['name'], inplace=True)

            elif table_name == 'commanderfaction':
                df.drop(df['faction_id'].loc[df['faction_id'].isin([54])].index, inplace=True)                               

            elif table_name == 'commanderspecialrule':
                df['isoption'] = 0
                df.loc[df['id'].isin([6,349,350]), 'specialrule_id'] = 54
                df.drop(df['commander_id'].loc[df['commander_id'].isin([130,131,132])].index, inplace=True)                

            elif table_name == 'faction':
                df['maxshipdecks'] = 10
                df['attackerrollbonus'] = 0
                df.drop(df['id'].loc[df['id'].isin([54])].index, inplace=True)
                # Add values for maxshipdecks where needed.
                df.loc[df['nationality_id'].isin([8]), 'maxshipdecks'] = 1
                df.loc[df['id'].isin([46,27,41,108,109,23]), 'maxshipdecks'] = 1
                df.loc[df['id'].isin([61,72,74,104]), 'maxshipdecks'] = 2
                df.loc[df['id'].isin([110]), 'maxshipdecks'] = 3
                # Add values for attackerrollbonus where needed.
                df.loc[df['id'].isin([2,5,7,9,12,13,14,21,24,27,41,45,57,62,69,70,79,82,83,89,91,94,102,103,108]), 'attackerrollbonus'] = 2
                df.loc[df['id'].isin([3,6,8,43,44,53,81,87,92]), 'attackerrollbonus'] = 3
                df.loc[df['id'].isin([22,25,39,74,76,85]), 'attackerrollbonus'] = 4
                df.loc[df['id'].isin([15]), 'attackerrollbonus'] = -2

            elif table_name == 'factionunit':
                df.drop(df['faction_id'].loc[df['faction_id'].isin([54])].index, inplace=True)   

            # Add columns to forceoption table to account for minimum unit requirements and mounted commander requirement.
            elif table_name == 'forceoption':
                df['unit_qty_req'] = 0
                df['unit_id'] = 0
                df['req_mounted_commander'] = 0
                df.drop(df['faction_id'].loc[df['faction_id'].isin([54])].index, inplace=True)
                df.loc[df['details'].str.contains('at least'), 'unit_qty_req'] = 2
                df.loc[df['id'].isin([20,24]), 'unit_id'] = 16
                df.loc[df['id'].isin([1,51]), 'unit_id'] = 43
                df.loc[df['id'].isin([14,61]), 'unit_id'] = 26
                df.loc[df['id'].isin([23]), 'unit_id'] = 18
                df.loc[df['id'].isin([10,39,59]), 'unit_id'] = 32
                df.loc[df['id'].isin([1,10,14,23,39,51,59,61]), 'req_mounted_commander'] = 1

            elif table_name == 'forcespecialrule':
                with open(f, 'r') as file:
                    # Add faction special rules from FotF and RtB to forcespecialrule df from faction df.
                    df2 = pd.read_csv('bp_data/faction.csv')
                    newId = 119
                    for row in df2.itertuples():
                        faction_id = row[1]
                        if faction_id >= 55:
                            specialrules = row[4]
                            specialrulesList = specialrules.strip().splitlines()
                            for line in specialrulesList:
                                if not 'Force Special Rules' in line:
                                    factionRule = line[2:].strip()
                                    df.loc[len(df.index)] = [newId, faction_id, factionRule, 0]
                                    newId += 1
                    # Standardize text for bonuses for roll to determine attacker.
                    df.loc[df['id'].isin([7,16,29,33,41,55,65,68,206,231,232,255,257]), 'details'] = 'This Force adds +2 when determining the attacker in a scenario.'
                    df.loc[df['id'].isin([19,22,63,73]), 'details'] = 'This Force adds +3 when determining the attacker in a scenario.'

            elif table_name == 'ship':
                df['topspeed'] = df['topspeed'].str[:-1].astype(int)

            elif table_name == 'specialrule':
                df.drop(columns = ['onunit', 'oncommander', 'onship', 'onfactionopt'], inplace=True)
                df.drop(df['id'].loc[df['id'].isin([20,41,46,99])].index, inplace=True)
                df['name'].replace(to_replace = [' \(cdr\)',' \(shp\)'], value = ['',''], inplace=True, regex=True)

            elif table_name == 'unit':
                df.drop(df['id'].loc[df['id'].isin([46])].index, inplace=True)
                df.sort_values(by=['name'], inplace=True)

            elif table_name == 'unitoption':
                df['limited'] = 0
                df['addsubtractweaponequipment'] = 0
                df['weaponequipment_id'] = 1
                df.loc[df['id'] == 295, 'unit_id'] = 8
                df.loc[df['id'] == 296, 'unit_id'] = 10
                df.loc[df['id'].isin([295,296]), 'limited'] = 1

            # These tables to be restructured and renamed.
            if table_name == 'unorthodoxforce' or table_name == 'unorthodoxoption':
                commander_portion = df.loc[df['commander_id'] > 0].copy()
                faction_portion = df.loc[df['forceoption_id'] > 0].copy()
                if table_name == 'unorthodoxoption':
                    commander_portion.loc[commander_portion['unitoption_id'] == 0, 'unitoption_id'] = np.NaN
                    faction_portion.loc[faction_portion['unitoption_id'] == 0, 'unitoption_id'] = np.NaN
                commandereffects.append(commander_portion)
                factioneffects.append(faction_portion)

            else:
                column_names = [] # To be used later for FK assignments.
                df_schema = {} # To be used later when df is converted to a table in the db.

                # Iterate through table columns.
                for col in df.columns:
                    column_names.append(col)
                    
                    # Add columns to schema to define their data types.
                    if col == 'name':
                        df_schema['name'] = String(80)
                    elif col == 'details':
                        df_schema['details'] = Text
                    elif df[f'{col}'].dtype == 'int64':
                        df_schema[f'{col}'] = Integer
                    else:
                        df_schema[f'{col}'] = VARCHAR

                    if table_name == 'weaponequipment':
                        df_schema['pointcost'] = Integer
                        df_schema['pointsperunit'] = Integer
                    
                    # In rows to be used for FK constraints replace value 0 with NaN (will be null in db).
                    if '_id' in col:
                        for ind in df.index:
                            if df[col][ind] == 0:
                                df[col].replace(0, np.NaN, inplace=True)

                # Add table name to list for foreign key assignment later.
                tables.append({'table_name': table_name, 'table_columns': column_names})

                # In rows to be used for FK constraints replace value 0 with NaN (will be null in db). NO LONGER NEEDED
                # for col in df.columns:
                #     if '_id' in col:
                #         for ind in df.index:
                #             if df[col][ind] == 0:
                #                 df[col].replace(0, np.NaN, inplace=True)

                ### End Data Cleanup ###

                # Add dataframe to db as table.
                # If table already present, replaces previous data.
                df.to_sql(table_name, engine, if_exists='replace', index= False, dtype= df_schema)
                
                # Set 'id' column as table's Primary Key.
                with engine.connect() as con:
                    con.execute(f"CREATE SEQUENCE {table_name}_serial AS integer START {(df['id'].max()) + 1} OWNED BY {table_name}.id;")
                    con.execute(f"ALTER TABLE {table_name} ALTER COLUMN id SET DEFAULT nextval('{table_name}_serial');")
                    con.execute(f'ALTER TABLE {table_name} ADD PRIMARY KEY (id);')

                if (table_name == 'unitoption'):
                    with engine.connect() as con:
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, pointcost, perxmodels, pointsperunit, experienceupg, applyall) VALUES (33, 'Unorthodox Force: Le Sieur de Grammont', 'Flibustier units in this Force may add Horses for 4 points (not per model). While mounted, these units apply a +1 penalty to all Fight and Shoot saves.', 7, 0, 0, 4, 0, 0)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, pointsperunit, limited) VALUES (333, 'Expert Artillery Crew', 'This unit may replace the <i>Artillery Crew</i> Special Rule with <I>Expert Artillery Crew</i> for +4pts per unit.', 66, 4, 1)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, pointsperunit, limited) VALUES (334, 'Expert Artillery Crew', 'This unit may replace the <i>Artillery Crew</i> Special Rule with <I>Expert Artillery Crew</i> for +4pts per unit.', 89, 4, 1)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, pointsperunit, limited) VALUES (335, 'Expert Artillery Crew', 'This unit may replace the <i>Artillery Crew</i> Special Rule with <I>Expert Artillery Crew</i> for +4pts per unit.', 102, 4, 1)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, pointcost, experienceupg, applyall, limited) VALUES (336, 'European Pikemen Exp Upgrade', 'Upgrade from <i>Trained</i> to <i>Veteran</i> for 1 point per model.', 69, 1, 1, 1, 1)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, limited) VALUES (337, 'Churchs Raiders Militia Rule Swap', 'This unit may exchange the <i>Drilled</i> Special Rule for the <i>Elusive</i> Special Rule', 54, 1)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, limited) VALUES (338, 'Tercios Milicianos Weapon Swap', 'This unit may exchange their Matchlock Muskets for Carbines at no cost.', 1, 1)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, limited) VALUES (339, 'Tercios Hostigadores Weapon Swap', 'This unit may exchange their Matchlock Muskets for Heavy Matchlock Muskets at no cost.', 77, 1)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, limited) VALUES (340, 'Milicianos Indios Bows for Muskets', 'Exchange Bows for Firelock Muskets as Main Weapons at no cost.', 11, 1)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, limited) VALUES (341, 'European Militia Matchlock for Firelock', 'Exchange Matchlock Muskets for Firelock Muskets as Main Weapons at no cost.', 67, 1)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, limited) VALUES (342, 'European Militia Musket for Carbines and Scouts', 'Exchange Muskets for Firelock Carbines and the <i>Scout</i> Special Rule at no cost.', 67, 1)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, limited) VALUES (343, 'Marineros Musket for Carbines and Scouts', 'If this unit has Muskets as a Main Weapon it may exchange its Muskets for Firelock Carbines and the <i>Scout</i> Special Rule at no cost.', 10, 1)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, limited) VALUES (344, 'European Sailors Musket for Carbines and Scouts', 'If this unit has Muskets as a Main Weapon it may exchange its Muskets for Firelock Carbines and the <i>Scout</i> Special Rule at no cost.', 66, 1)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, limited) VALUES (350, 'African Warriors Slow Reload to Poorly Equipped', 'Any unit in this Force with the <i>Slow Reload</i> Special Rules may replace it with the <i>Poorly Equipped</i> Special Rule at no cost.', 48, 1)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, limited) VALUES (351, 'Warrior Musketeers Slow Reload to Poorly Equipped', 'Any unit in this Force with the <i>Slow Reload</i> Special Rules may replace it with the <i>Poorly Equipped</i> Special Rule at no cost.', 53, 1)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, limited) VALUES (348, 'Warrior Archers Slow Reload to Poorly Equipped', 'Any unit in this Force with the <i>Slow Reload</i> Special Rules may replace it with the <i>Poorly Equipped</i> Special Rule at no cost.', 64, 1)")
                        con.execute("INSERT INTO unitoption(id, name, details, unit_id, limited) VALUES (349, 'Warriors Slow Reload to Poorly Equipped', 'Any unit in this Force with the <i>Slow Reload</i> Special Rules may replace it with the <i>Poorly Equipped</i> Special Rule at no cost.', 45, 1)")

                # if table_name == 'commander':
                #     with engine.connect() as con:
                #         for row in df.iterrows():
                #             if row[1][7] > 0: # Add data from commander table to commandernationality table.
                #                 con.execute(f'INSERT INTO commandernationality(commander_id,nationality_id, primary_nationality) VALUES({row[1][0]}, {int(row[1][7])}, true);')

        except Exception as e: print(f'* * * * * * * * * * {e} * * * * * * * * * *')

commandereffect = pd.concat(commandereffects)
commandereffect.drop(commandereffect['commander_id'].loc[commandereffect['commander_id'] == 82].index, inplace=True)
commandereffect.reset_index(drop=True, inplace=True)
commandereffect['id'] = commandereffect.index +1
commandereffect.loc[commandereffect['id'] == 73, 'unitclass_id'] = 0

factioneffect = pd.concat(factioneffects)
factioneffect.drop(factioneffect['forceoption_id'].loc[factioneffect['forceoption_id'] == 41].index, inplace=True)
factioneffect.reset_index(drop=True, inplace=True)
factioneffect['id'] = factioneffect.index +1
factioneffect.insert(6,'applyall', 0)
factioneffect['faction_id'] = np.NaN
factioneffect.drop(factioneffect['id'].loc[factioneffect['id'].isin([30,31,32,33,34,35,36,37])].index, inplace=True) # Remove extra Baymen commandereffects
factioneffect.loc[factioneffect['id'].isin([3,4,5]), 'applyall'] = 1
factioneffect.loc[factioneffect['unitoption_id'] == 322, 'name'] = 'Baymen Elusive Scouts'
factioneffect.loc[factioneffect['unitoption_id'] == 322, 'details'] = 'Add Unit Option for all units to add Elusive and Scout Special Rules for 4 pts.'
factioneffect.loc[factioneffect['unitoption_id'] == 322, 'faction_id'] = 110
factioneffect.loc[factioneffect['unitoption_id'] == 322, ['forceoption_id', 'addsubtract', 'unit_id']] = np.NaN
factioneffect.loc[factioneffect['forceoption_id'].isin([65,66,85]), 'forceoption_id'] = np.NaN
factioneffect.loc[factioneffect['id'] == 25, 'unitoption_id'] = 334
factioneffect.loc[factioneffect['id'] == 26, 'unitoption_id'] = 333
factioneffect.loc[factioneffect['id'] == 27, 'unitoption_id'] = 335
factioneffect.loc[factioneffect['id'].isin([16,17,24,25,26,27]), ['addsubtract','applyall','unit_id']] = np.NaN
factioneffect.loc[factioneffect['id'] == 16, 'faction_id'] = 92
factioneffect.loc[factioneffect['id'] == 17, 'faction_id'] = 76
factioneffect.loc[factioneffect['id'].isin([24,25,26,27]), 'faction_id'] = 107



table_name = ''
for df in [commandereffect,factioneffect]:
    df.reset_index(drop=True)
    for col in df.columns:
        if '_id' in col:
            df[col].replace(0, np.NaN, inplace=True)
    if not table_name:
        df.drop(columns = 'forceoption_id', inplace=True)
        column_names=['id','commander_id','name','details','addsubtract','unit_id','unitclass_id','unitoption_id']    
        df_schema = {'id': Integer, 'commander_id': Integer, 'name': String(80), 'details': Text, 'addsubtract': Integer, 'unit_id': Integer, 'unitclass_id': Integer, 'unitoption_id': Integer}
        table_name = 'commandereffect'
    else:
        df.drop(columns = 'commander_id', inplace=True)
        column_names=['id','forceoption_id','name','details','addsubtract','unit_id','unitclass_id','unitoption_id']    
        df_schema = {'id': Integer, 'forceoption_id': Integer, 'name': String(80), 'details': Text, 'addsubtract': Integer, 'unit_id': Integer, 'unitclass_id': Integer, 'unitoption_id': Integer, 'faction_id': Integer}
        table_name = 'factioneffect'
    tables.append({'table_name': table_name, 'table_columns': column_names})
    df.to_sql(table_name, engine, if_exists='replace', index= False, dtype= df_schema)
    with engine.connect() as con:
                    con.execute(f"CREATE SEQUENCE {table_name}_serial AS integer START {(df['id'].max()) + 1} OWNED BY {table_name}.id;")
                    con.execute(f"ALTER TABLE {table_name} ALTER COLUMN id SET DEFAULT nextval('{table_name}_serial');")
                    con.execute(f'ALTER TABLE {table_name} ADD PRIMARY KEY (id);')    
                    

# ******************** END DATA CLEANUP AND DB POPULATION ********************

# Additional database construction and structuring.
with engine.connect() as con:
    # # Create nationality table. ** NO LONGER NEEDED NOW THAT Force Builder SCRAPES ARE SCRIPTED. **
    # nationalities = ['Spanish', 'English', 'French', 'Unaligned', 'Dutch', 'Golden Age Pirates', 'placeholder', 'Natives']
    # con.execute('CREATE TABLE IF NOT EXISTS nationality(id serial PRIMARY KEY, name VARCHAR UNIQUE);')
    # for nation in nationalities:
    #     con.execute(f"INSERT INTO nationality (name) VALUES ('{nation}');")

    # Create Foreign Keys where needed.
    for table in tables:
        for col in table['table_columns']:
            avoid_list = ['unitclass_id', 'wcproduct_id'] # Atypical columns with '_id' in name.
            if '_id' in col and col not in avoid_list: # Foreign Keys should be set to columns ending in '_id'.
                try:
                    keyed_table = col.replace('_id','') # Column name minus '_id' should equate to referenced table name.
                    # Create the Primary Key constraint.
                    con.execute(f'ALTER TABLE {table["table_name"]} ADD CONSTRAINT fk_{table["table_name"]}_{keyed_table} FOREIGN KEY ({col}) REFERENCES {keyed_table} (id) MATCH FULL ON DELETE CASCADE;')
                    
                    print(f'Added FK connecting {table["table_name"]} {col} to {keyed_table} id')
                
                # If there is a problem, print a formatted error msg and continue creating Foreign Key constraints.
                except Exception as e: print(f'''
                    ********************************************************************
                    
                    ERROR for table {table["table_name"]} {col} referencing table {keyed_table}:
                    {e}''')

    con.execute('UPDATE unitoption SET weaponequipment_id = null WHERE weaponequipment_id = 1;')

    con.execute("UPDATE ship SET cannonsdecks = '6/0', swivelsdecks = '2/4' WHERE id = 1;")
    con.execute('DELETE FROM faction WHERE id = 17 OR id = 30;')
    con.execute('DELETE FROM forceoption WHERE id = 90 OR id = 71 OR id = 65 OR id = 66 OR id = 85;')
    con.execute('DELETE FROM unitoption WHERE id = 312;')
    con.execute('DELETE FROM commander WHERE id = 56 OR id = 128;')
    con.execute('DELETE FROM unit WHERE id = 21 OR id = 50 OR id = 58 OR id = 65 OR id = 83 OR id = 96;')
    # con.execute('DELETE FROM unorthodoxoption WHERE id = 25 OR id = 33 OR id = 34')
    # Set certainnations and certainfactions to 1 (true) for character records, as appropriate.
    con.execute('UPDATE character SET certainnations = 1 WHERE id IN (37,39,40,41,42,53,54,55,56,57,58,59,61,63,68,69);')
    con.execute('UPDATE character SET certainfactions = 1 WHERE (id IN (38,40,41,55,56,61,63,67,70) OR id BETWEEN 43 AND 52);')
    # Remove 0's from weaponequipment
    con.execute('UPDATE weaponequipment SET pointcost = null WHERE pointcost = 0;')
    con.execute('UPDATE weaponequipment SET pointsperunit = null WHERE pointsperunit = 0;')
    # Add data to unitoption
    con.execute("INSERT INTO unitoption(id, name, details, unit_id, pointsperunit, limited, addsubtractweaponequipment, weaponequipment_id) VALUES (325, 'Poisoned Arrows','Units with Bows may add Poisoned Arrows to the entire unit for 3 points.',45,3,1,1,3)")
    con.execute("INSERT INTO unitoption(id, name, details, unit_id, pointsperunit, limited, addsubtractweaponequipment, weaponequipment_id) VALUES (326, 'Poisoned Arrows','Units with Bows may add Poisoned Arrows to the entire unit for 3 points.',47,3,1,1,3)")
    con.execute("INSERT INTO unitoption(id, name, details, unit_id, pointsperunit, limited, addsubtractweaponequipment, weaponequipment_id) VALUES (327, 'Poisoned Arrows','Units with Bows may add Poisoned Arrows to the entire unit for 3 points.',48,3,1,1,3)")
    con.execute("INSERT INTO unitoption(id, name, details, unit_id, pointsperunit, limited, addsubtractweaponequipment, weaponequipment_id) VALUES (328, 'Poisoned Arrows','Units with Bows may add Poisoned Arrows to the entire unit for 3 points.',64,3,1,1,3)")
    con.execute("INSERT INTO unitoption(id, name, details, pointsperunit, addsubtractweaponequipment, weaponequipment_id) VALUES (329, 'Torches','Any unit that is not Mounted may take Torches for 3 points.',3,1,4)")
    con.execute("INSERT INTO unitoption(id, name, details, pointsperunit, addsubtractweaponequipment, weaponequipment_id) VALUES (345, 'Climbing Gear','Any unit that is not Mounted may take Climbing Gear for 2 points. If a unit has models with Explosives (not just the option to purchase them) that unit may take Climbing Gear for free.',2,1,5)")
    con.execute("INSERT INTO unitoption(id, name, details, unit_id, pointsperunit, limited) VALUES (330, 'Musket Downgrade','Unit may downgrade their Muskets to a Sidearm for -4 points (not per model).',53,-4,1)")
    con.execute("INSERT INTO unitoption(id, name, details, unit_id, pointsperunit, limited) VALUES (331, 'Musket Downgrade','If armed with Muskets as a primary weapon, unit may downgrade it to a Sidearm for -4 points (not per model).',81,-4,1)")
    con.execute("INSERT INTO unitoption(id, name, details, unit_id, pointsperunit, limited) VALUES (332, 'Musket Downgrade','If armed with Muskets as a primary weapon, unit may downgrade it to a Sidearm for -4 points (not per model).',113,-4,1)")
    # Add data to commandereffect
    con.execute("INSERT INTO commandereffect(commander_id, addsubtract, unit_id, unitoption_id) VALUES (96,1,7,33)")
    con.execute("INSERT INTO commandereffect(commander_id, addsubtract, unit_id, unitclass_id) VALUES (99,1,25,0)")
    con.execute("INSERT INTO commandereffect(commander_id, addsubtract, unit_id, unitclass_id) VALUES (99,1,26,0)")
    con.execute("INSERT INTO commandereffect(commander_id, addsubtract, unit_id, unitclass_id) VALUES (99,1,73,0)")
    # Add data to factioneffect
    con.execute("INSERT INTO factioneffect(forceoption_id, name, addsubtract, applyall, unit_id, unitclass_id) VALUES (50,'Spanish Corsairs',1,0,101,0)")
    con.execute("INSERT INTO factioneffect(forceoption_id, name, addsubtract, applyall, unit_id, unitclass_id) VALUES (50,'Spanish Corsairs',1,0,11,0)")
    con.execute("INSERT INTO factioneffect(forceoption_id, name, addsubtract, applyall, unit_id, unitclass_id) VALUES (50,'Spanish Corsairs',1,0,92,0)")
    con.execute("INSERT INTO factioneffect(forceoption_id, name, addsubtract, applyall, unit_id, unitclass_id) VALUES (68,'West India Company',-1,0,109,0)")

    con.execute("INSERT INTO factioneffect(forceoption_id, name, details, addsubtract, unit_id, unitoption_id) VALUES (89,'Baymen Out of Practice', 'Out of Practice Option for Later Flibustiers.',1,99,323)")

    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (31, 'Caribbean Tribes Poisoned Arrows', 'Add Poisoned Arrows Unit Option to Warriors', 325)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (32, 'South American Tribes Poisoned Arrows', 'Add Poisoned Arrows Unit Option to Warriors', 325)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (16, 'Caribs (Kalinago) Poisoned Arrows', 'Add Poisoned Arrows Unit Option to Warriors', 325)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (31, 'Caribbean Tribes Poisoned Arrows', 'Add Poisoned Arrows Unit Option to Young Warriors', 326)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (32, 'South American Tribes Poisoned Arrows', 'Add Poisoned Arrows Unit Option to Young Warriors', 326)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (16, 'Caribs (Kalinago) Poisoned Arrows', 'Add Poisoned Arrows Unit Option to Young Warriors', 326)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (31, 'Caribbean Tribes Poisoned Arrows', 'Add Poisoned Arrows Unit Option to African Warriors', 327)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (32, 'South American Tribes Poisoned Arrows', 'Add Poisoned Arrows Unit Option to African Warriors', 327)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (16, 'Caribs (Kalinago)Poisoned Arrows', 'Add Poisoned Arrows Unit Option to African Warriors', 327)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (31, 'Caribbean Tribes Poisoned Arrows', 'Add Poisoned Arrows Unit Option to Warrior Archers', 328)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (32, 'South American Tribes Poisoned Arrows', 'Add Poisoned Arrows Unit Option to Warrior Archers', 328)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (16, 'Caribs (Kalinago) Poisoned Arrows', 'Add Poisoned Arrows Unit Option to Warrior Archers', 328)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (98, 'Choctaw Musket Downgrade', 'Add Unit Option for Warrior Musketeers.', 330)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (98, 'Choctaw Musket Downgrade', 'Add Unit Option for Braves.', 331)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (98, 'Choctaw Musket Downgrade', 'Add Unit Option for Renegadoes.', 332)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (48, 'Swedish Militia Pikemen Exp Upgrade', 'Add Unit Option for Pikemen.', 336)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (55, 'Churchs Raiders English Militia SR Swap', 'Add Unit Option for English Militia.', 337)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (23, 'Tercio Weapon Swap', 'Add Unit Option for Milicianos.', 338)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (23, 'Tercio Weapon Swap', 'Add Unit Option for Hostigadores.', 339)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (38, 'Portuguese-Brazilian Tercios & Militia Weapon Swap', 'Add Unit Option for Milicanos Indios.', 340)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (106, 'Brazilian Portuguese Garrison Weapon Swap', 'Add Unit Option for Milicanos Indios.', 340)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (51, 'Portuguese Bandeirantes Weapon Swap', 'Add Unit Option for Milicanos Indios.', 340)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (51, 'Portuguese Bandeirantes Weapon Swap', 'Add Unit Option for European Militia.', 341)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (51, 'Portuguese Bandeirantes Weapon Swap', 'Add Unit Option for European Militia.', 342)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (51, 'Portuguese Bandeirantes Weapon Swap', 'Add Unit Option for Marineros.', 343)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (51, 'Portuguese Bandeirantes Weapon Swap', 'Add Unit Option for European Sailors.', 344)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (108, 'Miskito African Warriors SR Swap', 'Add Unit Option for African Warriors.', 350)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (108, 'Miskito Warrior Musketeers SR Swap', 'Add Unit Option for Warrior Musketeers.', 351)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (108, 'Miskito Warrior Archers SR Swap', 'Add Unit Option for Warriors Archers.', 348)")
    con.execute("INSERT INTO factioneffect(faction_id, name, details, unitoption_id) VALUES (108, 'Miskito Warriors SR Swap', 'Add Unit Option for Warriors.', 349)")


    #Add data to commandernationality
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (106,5,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (64,3,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (159,8,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (216,8,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (176,2,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (177,2,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (64,2,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (65,2,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (98,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (160,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (199,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (198,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (197,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (65,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (61,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (62,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (63,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (202,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (201,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (200,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (194,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (195,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (196,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (205,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (204,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (203,1,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (181,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (182,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (183,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (194,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (195,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (196,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (79,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (80,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (81,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (23,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (24,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (25,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (33,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (34,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (35,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (199,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (198,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (197,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (17,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (32,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (116,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (64,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (161,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (162,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (163,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (164,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (165,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (166,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (44,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (178,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (179,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (180,4,false)')
    con.execute('INSERT INTO commandernationality(commander_id, nationality_id, primary_nationality) VALUES (209,4,false)')
    # Add data to commanderspecialrule (for Standard Commanders)
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (185, 24,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (185, 23,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (185, 30,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (185, 78,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (185, 22,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (185, 79,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (185, 55,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (185, 35,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (185, 83,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (185, 88,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (186, 24,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (186, 23,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (186, 30,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (186, 78,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (186, 22,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (186, 79,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (186, 55,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (186, 35,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (186, 83,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (186, 88,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (195, 24,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (195, 23,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (195, 30,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (195, 78,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (195, 66,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (195, 18,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (195, 93,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (195, 65,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (195, 47,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (195, 157,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (195, 103,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (196, 24,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (196, 23,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (196, 30,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (196, 78,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (196, 66,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (196, 18,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (196, 93,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (196, 65,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (196, 47,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (196, 157,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (196, 103,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (197, 24,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (197, 23,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (197, 30,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (197, 70,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (197, 125,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (197, 95,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (197, 55,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (197, 92,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (197, 31,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (198, 24,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (198, 23,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (198, 30,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (198, 70,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (198, 125,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (198, 95,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (198, 55,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (198, 92,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (198, 31,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (200, 24,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (200, 23,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (200, 95,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (200, 70,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (200, 66,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (200, 30,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (200, 54,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (200, 65,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (201, 24,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (201, 23,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (201, 95,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (201, 70,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (201, 66,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (201, 30,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (201, 54,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (201, 65,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (203, 65,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (203, 30,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (203, 23,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (203, 26,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (203, 54,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (203, 24,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (203, 91,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (203, 93,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (204, 65,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (204, 30,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (204, 23,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (204, 26,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (204, 54,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (204, 24,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (204, 91,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (204, 93,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (182, 24,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (182, 23,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (182, 78,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (182, 14,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (182, 32,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (182, 31,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (182, 61,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (183, 24,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (183, 23,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (183, 78,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (183, 14,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (183, 32,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (183, 31,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (183, 61,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (225, 24,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (225, 92,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (225, 38,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (225, 55,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (225, 86,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (225, 7,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (225, 35,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (225, 91,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (225, 47,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (225, 157,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (225, 103,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (226, 24,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (226, 92,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (226, 38,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (226, 55,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (226, 86,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (226, 7,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (226, 35,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (226, 91,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (226, 47,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (226, 157,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (226, 103,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (243, 2,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (243, 85,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (243, 5,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (243, 55,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (243, 100,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (243, 37,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (243, 18,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (243, 92,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (244, 2,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (244, 85,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (244, 5,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (244, 55,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (244, 100,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (244, 37,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (244, 18,1)')
    con.execute('INSERT INTO commanderspecialrule(commander_id, specialrule_id, isoption) VALUES (244, 92,1)')
    # Add data to characternationality
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (37,8)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (39,2)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (40,3)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (41,3)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (42,2)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (53,6)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (54,6)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (55,8)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (56,8)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (57,2)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (58,6)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (59,6)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (61,1)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (63,1)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (68,6)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (69,2)')
    con.execute('INSERT INTO characternationality(character_id, nationality_id) VALUES (69,6)')
    # Add data to characterfaction
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (38,56)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (40,35)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (40,61)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (40,104)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (41,35)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (41,61)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (41,104)')    
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (41,33)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (41,63)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (41,102)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (43,5)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (43,9)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (44,5)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (44,9)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (45,5)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (45,7)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (45,9)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (46,5)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (46,7)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (46,9)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (48,5)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (48,9)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (49,5)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (49,9)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (50,5)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (50,9)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (51,5)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (51,9)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (52,5)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (52,9)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (55,83)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (55,70)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (55,89)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (55,46)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (55,109)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (55,77)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (56,83)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (56,70)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (56,89)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (56,46)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (56,108)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (61,38)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (61,51)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (63,38)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (63,51)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (67,85)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (67,87)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (70,10)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (70,90)')
    con.execute('INSERT INTO characterfaction(character_id, faction_id) VALUES (70,105)')
    # Add data to characterspecialrule
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (60,68)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (60,14)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (56,9)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (62,14)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (55,6)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (16,54)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (16,18)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (63,22)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (63,108)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (37,125)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (58,70)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (58,19)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (9,15)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (61,30)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (11,30)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (57,6)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (57,7)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (39,6)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (39,5)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (13,66)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (13,9)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (59,19)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (59,70)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (14,125)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (14,17)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (15,68)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (15,18)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (19,28)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (66,30)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (21,7)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (21,6)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (22,9)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (53,14)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (53,18)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (48,2)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (48,34)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (48,158)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (44,18)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (68,19)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (68,2)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (68,93)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (51,106)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (51,158)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (69,83)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (69,95)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (69,18)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (70,34)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (70,8)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (49,28)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (49,30)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (49,158)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (52,158)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (43,18)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (54,54)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (54,18)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (50,108)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (50,158)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (38,34)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (38,58)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (45,84)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (67,14)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (42,96)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (46,6)')
    con.execute('INSERT INTO characterspecialrule(character_id, specialrule_id) VALUES (46,125)')




engine.dispose()
