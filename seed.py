import os, re
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.types import Integer, String, Text, VARCHAR, Boolean

import innocuous

directory = 'bp_data' # Directory containing csv files to create tables from

tables=[] # list for table names and columns

engine=create_engine(f'postgresql+psycopg2://postgres:{innocuous.p}@localhost:5432/bp')

# Start with a fresh schema
with engine.connect() as con:
    con.execute('DROP SCHEMA public CASCADE;')
    con.execute('CREATE SCHEMA public;')

# ******************** BEGIN DATA CLEANUP AND DB POPULATION ********************

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
                
                # In rows to be used for FK constraints replace value 0 with NaN (will be null in db).
                if '_id' in col:
                    for ind in df.index:
                        if df[col][ind] == 0:
                            df[col].replace(0, np.NaN, inplace=True)

            # Get table name from file name.
            if filename == 'data_location.csv':
                table_name = str(filename).replace('data_','').replace('.csv', '')
            else:
                table_name = str(filename).replace('data_bp','').replace('.csv', '')

            # Add table name to list for foreign key assignment later.
            tables.append({'table_name': table_name, 'table_columns': column_names})

            # In rows to be used for FK constraints replace value 0 with NaN (will be null in db).
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
                    con.execute(f'ALTER TABLE {table["table_name"]} ADD CONSTRAINT fk_{table["table_name"]}_{keyed_table} FOREIGN KEY ({col}) REFERENCES {keyed_table} (id) MATCH FULL;;')
                    
                    print(f'Added FK connecting {table["table_name"]} {col} to {keyed_table} id')
                
                # If there is a problem, print a formatted error msg and continue creating Foreign Key constraints.
                except Exception as e: print(f'''
                    ********************************************************************
                    
                    ERROR for table {table["table_name"]} {col} referencing table {keyed_table}:
                    {e}''')

engine.dispose()
