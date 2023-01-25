import requests, json, csv
from bs4 import BeautifulSoup

def getHTMLdocument(url):
    """ Function to extract html document from given url. """
    # request for HTML document of given url
    response = requests.get(url)
    # response will be provided in JSON format
    return response.text

def extract_data_from_string(string):
    """ Extracts table data from a Force Builder script tag. """
    # find index where data starts
    data_start_index = string.find('[')
    # find index where data ends
    data_end_index = string.rfind(';')
    # slice string to select only the desired data
    data = string[data_start_index : data_end_index]
    return data

def extract_name(string):
    """ Extracts table name from a Force Builder script tag. """
    # find index where name starts
    name_start_index = (string.find('bp')) + 2
    # find index where name ends
    name_end_index = (string.rfind('=')) - 1
    # slice string to select only the table name
    name = string[name_start_index : name_end_index]
    return name

def write_data_to_csv(name, json_data):
    """ Extracts desired data from script tag, creates csv file and writes to it. """
    with open(f'bp_data/{name}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        count = 0
        for d in json_data:
            # Create headers from data
            if count == 0:
                header = d.keys()
                writer.writerow(header)
                count += 1
            # Write current row of data to csv
            writer.writerow(d.values())

def process_data(string):
    """ Extracts desired data from script tag, creates csv file and writes to it. """
    data = extract_data_from_string(string)
    name = extract_name(string)
    # Convert data to json format
    json_data = json.loads(data)
    write_data_to_csv(name, json_data)

def handle_artillery_data(string):
    data = extract_data_from_string(string)
    name = extract_name(string)
    json_data = json.loads(data)
    artillery = []
    characters = []
    misc = []
    for row in json_data:
        if row['name'].startswith('Character'):
            characters.append(row)
        elif row['name'].startswith('Fortifications') or row['name'].startswith('Terrain') or row['name'].startswith('Force') or row['name'].startswith('Commander Horse') or row['name'].startswith('Poisoned Arrows') or row['name'].startswith('Torches'):
            misc.append(row)
        else:
            artillery.append(row)
    write_data_to_csv(name, artillery)
    write_data_to_csv('character', characters)
    write_data_to_csv('misc', misc)

# assign URL
url_to_scrape = "https://forcebuilder.bloodandplunder.com/"
  
# create document
html_document = getHTMLdocument(url_to_scrape)
  
# create soap object
soup = BeautifulSoup(html_document, 'html.parser')

# select script tag content
scripts = soup('script')

# iterate through script tags in html
for script in scripts:
    # determine if script tag contains needed data
    if script.text.startswith('data_bp'):
        # get contents of script tag (represents a single table)
        text = script.text
        if script.text.startswith('data_bpartillery'):
            handle_artillery_data(text)
        # extract data from script tag and write to csv file
        else:
            process_data(text)