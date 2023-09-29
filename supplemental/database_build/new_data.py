import os
import config
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from app import app
from models import db, Source, ComponentSource, Faction

# Add Sources table to db
source1 = Source(name='Blood & Plunder Core Rulebook', year_of_publication=2017, print_url='https://www.firelockgames.com/product/blood-plunder-core-rulebook-revised-edition/')
source2 = Source(name='No Peace Beyond The Line', year_of_publication=2019, print_url='https://www.firelockgames.com/product/no-peace-beyond-the-line-expansion-rulebook/')
source3 = Source(name='The Buccaneer\'s Companion Vol. 1', year_of_publication=2020, digital_url='https://www.firelockgames.com/wp-content/uploads/2019/10/Commanders-and-Characters.pdf')
source4 = Source(name='Fire On The Frontier', year_of_publication=2021, print_url='https://www.firelockgames.com/product/fire-on-the-frontier-expansion-rulebook/', digital_url='https://www.firelockgames.com/product/fire-on-the-frontier-expansion-rulebook-pdf-pre-order/')
source5 = Source(name='Raise The Black', year_of_publication=2022, print_url='https://www.firelockgames.com/product/raise-the-black-expansion-book/')

db.session.add(source1)
db.session.add(source2)
db.session.add(source3)
db.session.add(source4)
db.session.add(source5)

db.session.commit()



engine=create_engine(f'postgresql+psycopg2://postgres:{config.POSTGRES_MASTER_PWD}@localhost:5432/bp')

directory = 'bp_data/supplemental' # Directory containing csv files to create tables from

faction_source_data = os.path.join(directory, 'faction_sources.csv')
faction_years_data = os.path.join(directory, 'faction_years.csv')

# Add Component Source records for Factions
with open(faction_source_data, 'r') as file:
    df = pd.read_csv(faction_source_data)

    with engine.connect() as con:
        for row in df.iterrows():
            faction_id = row[1]['id']
            if row[1]['source1'] == 'x':
                new_record = ComponentSource()
                new_record.faction_id = faction_id
                new_record.source_id = 2
                db.session.add(new_record)
                db.session.commit()
            if row[1]['source2'] == 'x':
                new_record = ComponentSource()
                new_record.faction_id = faction_id
                new_record.source_id = 4
                db.session.add(new_record)
                db.session.commit()
            if row[1]['source3'] == 'x':
                new_record = ComponentSource()
                new_record.faction_id = faction_id
                new_record.source_id = 5
                db.session.add(new_record)
                db.session.commit()

# Add Years Active data to Faction records
with open(faction_years_data, 'r') as file:
    df = pd.read_csv(faction_years_data)

    with engine.connect() as con:
        for row in df.iterrows():
            faction = Faction.query.get_or_404(row[1]['id'])
            faction.name = row[1]['name']
            faction.first_year = row[1]['first_year']
            faction.last_year = row[1]['last_year']            
            db.session.commit()