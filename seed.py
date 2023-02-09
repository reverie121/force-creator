import os, re
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.types import Integer, String, Text, VARCHAR, Boolean

import innocuous

directory = 'bp_data' # Directory containing csv files to create tables from

engine=create_engine(f'postgresql+psycopg2://postgres:{innocuous.p}@localhost:5432/bp')

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

            # Create new columns for character table.
            if table_name == 'character':
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
            
            # Move data around in character table.
            if table_name == 'character':
                with engine.connect() as con:
                    # Change character type to 2 for Hostages/Advisors.
                    df.loc[df['name'].str.contains('Hostage'), 'charactertype'] = 2
                    # Change no_natives to 1 for Characters that cannot be used with the Native factions.
                    df.loc[df['details'].str.contains('Any but Native'), 'nonatives'] = 1
                    # Change certain_commanders to 1 for Characters that require a specific commander.
                    df.loc[df['details'].str.contains('May only be included in a Force commanded by'), 'certaincommanders'] = 1
                    # Remove everything from the character name from character.name.
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
                    df.drop(columns = ['details', 'model', 'uifolder', 'sort'], inplace=True)

            column_names = [] # To be used later for FK assignments.
            df_schema = {} # To be used later when df is converted to a table in the db.
            
            if table_name == 'commander':
                with engine.connect() as con:
                    for row in df.iterrows():
                        nationality_id = df.columns.get_loc('nationality_id')
                        if row[1][nationality_id] > 0 and row[1][nationality_id] != 7: # Add data from commander table to commandernationality table.
                            con.execute(f'INSERT INTO commandernationality(commander_id,nationality_id, primary_nationality) VALUES({row[1][0]}, {int(row[1][nationality_id])}, true);')
                    df.drop(columns = ['nationality_id'], inplace = True)

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
                con.execute(f'ALTER TABLE {table_name} ADD PRIMARY KEY (id);')

            # if table_name == 'commander':
            #     with engine.connect() as con:
            #         for row in df.iterrows():
            #             if row[1][7] > 0: # Add data from commander table to commandernationality table.
            #                 con.execute(f'INSERT INTO commandernationality(commander_id,nationality_id, primary_nationality) VALUES({row[1][0]}, {int(row[1][7])}, true);')
                
        except Exception as e: print(e)

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

    con.execute("UPDATE ship SET cannonsdecks = '6/0', swivelsdecks = '2/4' WHERE id = 1;")
    con.execute('DELETE FROM faction WHERE id = 17 OR id = 30;')
    con.execute('DELETE FROM commander WHERE id = 56 OR id = 128;')
    con.execute('DELETE FROM unit WHERE id = 21 OR id = 50 OR id = 58 OR id = 65 OR id = 83 OR id = 96;')
    # Remove Unorthdox Force records from Specialrules
    con.execute('DELETE FROM specialrule WHERE id = 128 OR id = 49 OR id = 127 OR id = 62 OR id = 82 OR id = 64 OR id = 81 OR id = 48 OR id = 63')
    # Set certainnations and certainfactions to 1 (true) for character records, as appropriate.
    con.execute('UPDATE character SET certainnations = 1 WHERE id IN (37,39,40,41,42,53,54,55,56,57,58,59,61,63,68,69);')
    con.execute('UPDATE character SET certainfactions = 1 WHERE (id IN (38,40,41,55,56,61,63,67,70) OR id BETWEEN 43 AND 52);')
    #Add date to commandernationality
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
