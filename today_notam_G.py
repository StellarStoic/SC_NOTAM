# Copyright (c) [2023] [StellarStoic on Github]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import re
import os
import json

SAVE_JSON_FILES = False  # Set to False if you don't want to save NOTAMS in JSON files

# Function to convert feet to meters
def feet_to_meters(feet):
    return round(feet * 0.3048, 1)

# The URL of the page you want to scrape
url = "https://www.sloveniacontrol.si/Strani/Summary-C.aspx"

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code != 200:
    print("Failed to retrieve the page:", response.status_code)
    exit()

# Get the HTML content of the page
html_content = response.text

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find all elements with the NOTAM class
notam_data_elements = soup.find_all(class_="kzps-notam-item")

# Check if any NOTAM data elements were found
if not notam_data_elements:
    print("No NOTAM data elements found.")
else:
    # Get today's date
    today = datetime.now(pytz.timezone('Europe/Ljubljana')).date()

    # Initialize a dictionary to store NOTAMs for each day
    notams_by_day = {today: []}

    # Regular expression for matching date strings
    date_pattern = re.compile(r'^(PERM|\d{2}\.\d{2}\.\d{4}( \d{2}:\d{2}( EST| CET)?)?)$')

    # Loop through each NOTAM data element
    for notam_data in notam_data_elements:
        # Extract the NOTAM number
        notam_number = notam_data.find('h1').get_text()

        # Initialize start_date and end_date to None
        start_date = None
        end_date = None

        # Initialize a flag to indicate whether to skip the NOTAM
        skip_notam = False
        
        # Extract only these second and third letters of a NOTAM Q code
        # https://skybrary.aero/sites/default/files/bookshelf/3298.pdf 
        notam_details = notam_data.find_all('p')
        for detail in notam_details:
            if detail.get_text().startswith('Q)'):
                q_code = detail.get_text().split('/')[1]
                if not (q_code.startswith('QR') or q_code.startswith('QW') or q_code.startswith('QOR')):
                    skip_notam = True  # Set the flag to skip the NOTAM
                    break  # Exit the inner loop

        # Skip this NOTAM if the flag is set
        if skip_notam:
            continue


        # Extract the NOTAM details from every NOTAM
        notam_details = notam_data.find_all('p')

        # Initialize variables to store the data
        q_data = ''
        a_data = ''
        b_data = ''
        c_data = ''
        d_data = ''
        e_data = ''
        f_data = ''
        g_data = ''
        timestamp = []

        # Loop through the NOTAM details and extract the information
        for detail in notam_details:
            # Check if the detail starts with 'Q)', 'A)', 'B)', 'C)', 'D)', or 'E)' and extract the data
            if detail.get_text().startswith('Q)'):
                q_data = detail.get_text()
            elif detail.get_text().startswith('A)'):
                a_data = detail.get_text()
            elif detail.get_text().startswith('B)'):
                b_data = detail.get_text()
            elif detail.get_text().startswith('C)'):
                c_data = detail.get_text()
            elif detail.get_text().startswith('D)'):
                d_data = detail.get_text()
            elif detail.get_text().startswith('E)'):
                e_data = detail.get_text()

            # Find F) and G) data
            if detail.find('span', string=re.compile(r'^F\)\s')) is not None:
                f_data = detail.find('span', string=re.compile(r'^F\)\s')).get_text()
            if detail.find('span', class_='kzps-notam-item-b', string=re.compile(r'^G\)\s')) is not None:
                g_data = detail.find('span', class_='kzps-notam-item-b', string=re.compile(r'^G\)\s')).get_text()

            # Check if F) and G) data contain 'FL' or 'FT' and convert the altitude from feet to meters
            # The check for '(' is to avoid trying to convert already converted values
            if 'FL' in f_data and '(' not in f_data: 
                flight_level = int(f_data.split('FL')[1].strip())  # Split on 'FL' and take the second part
                feet = flight_level * 100  # Convert flight level to feet
                f_meters = feet_to_meters(feet)  # Convert feet to meters
                if f_meters > 3000:  # Check if the altitude is more than 3000m
                    skip_notam = True  # Set the flag to skip the NOTAM
                    break  # Exit the inner loop
                f_data = f"{f_data} ({f_meters} m)"  # Append the converted value to the F) data
            elif 'FT' in f_data and '(' not in f_data: 
                feet = int(re.search(r'\d+', f_data).group())  # Extract the numeric part of the F) data
                f_meters = feet_to_meters(feet)  # Convert feet to meters
                if f_meters > 3000:  # Check if the altitude is more than 3000m
                    skip_notam = True  # Set the flag to skip the NOTAM
                    break  # Exit the inner loop
                f_data = f"{f_data} ({f_meters} m)"  # Append the converted value to the F) data

            # Do the same for G) data
            if 'FL' in g_data and '(' not in g_data: 
                flight_level = int(g_data.split('FL')[1].strip())  # Split on 'FL' and take the second part
                feet = flight_level * 100  # Convert flight level to feet
                g_meters = feet_to_meters(feet)  # Convert feet to meters
                g_data = f"{g_data} ({g_meters} m)"  # Append the converted value to the G) data
            elif 'FT' in g_data and '(' not in g_data: 
                feet = int(re.search(r'\d+', g_data).group())  # Extract the numeric part of the G) data
                g_meters = feet_to_meters(feet)  # Convert feet to meters
                g_data = f"{g_data} ({g_meters} m)"  # Append the converted value to the G) data

            # Find timestamp data
            timestamp_element = notam_data.find('p', class_='notam-hide')
            if timestamp_element is not None:
                timestamp_str = timestamp_element.get_text().split(': ')[1].strip()

                # Define multiple timestamp formats because sometimes the sloveniacontrol curators uses space between dots in a date 
                timestamp_formats = ["%d. %m. %Y %H:%M:%S", "%d.%m.%Y %H:%M:%S", "%d. %m.%Y %H:%M:%S", "%d.%m. %Y %H:%M:%S"]

                timestamp = None

                # Try each format until a match is found
                for timestamp_format in timestamp_formats:
                    try:
                        timestamp = datetime.strptime(timestamp_str, timestamp_format).strftime("%d.%m.%Y %H:%M:%S")
                        break  # Exit the loop if a match is found
                    except ValueError:
                        continue  # Continue to the next format if a ValueError occurs

                if timestamp is None:
                    print("Error parsing imestamp/Čas objave):", timestamp_str)

        # Skip this NOTAM if the flag is set
        if skip_notam:
            continue

        # Process the NOTAM details
        kml_filename = notam_number.replace('/', '-')
        kml_link = f"https://www.sloveniacontrol.si/NOTAM/{kml_filename}.kml"

        # Store the data in a tuple
        notam_data_tuple = (notam_number, q_data, a_data, b_data, c_data, d_data, e_data, f_data, g_data, timestamp, kml_link)
        
        # Function to save NOTAM data to a JSON file
        def save_notam_to_json(notam_data_tuple):
            # Create a directory to store NOTAM JSON files if it doesn't exist
            directory = "JSONs"
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Define the JSON file name based on the NOTAM ID
            notam_id = notam_data_tuple[0].replace("/", "-")  # Replace forward slash with hyphen
            json_file = os.path.join(directory, f"{notam_id}.json")
            
            # Create a dictionary for the NOTAM
            notam_dict = {
                "NOTAM_ID": notam_data_tuple[0],
                "Q_Code": notam_data_tuple[1],
                "Location": notam_data_tuple[2],
                "none": notam_data_tuple[3],
                "none": notam_data_tuple[4],
                "Day_Time": notam_data_tuple[5],
                "Description": notam_data_tuple[6],
                "Lower_Altitude": notam_data_tuple[7],
                "Upper_Altitude": notam_data_tuple[8],
                "Published_timestamp": notam_data_tuple[9],
                "KML_Link": notam_data_tuple[10]
            }            
            # Write the NOTAM data to the JSON file
            with open(json_file, "w") as f:
                json.dump(notam_dict, f, ensure_ascii=False, indent=4)


        # Loop through the NOTAM details and find the start and end dates
        for detail in notam_details:
            if detail.find(class_='kzps-notam-item-b') is not None:
                # Check if the text contains a date
                potential_date_str = detail.find(class_='kzps-notam-item-b').get_text().strip()
                if potential_date_str.startswith('B)'):  # Check if the string starts with 'B) '
                    start_date_str = potential_date_str[3:]  # Remove the 'B) ' prefix
                    if date_pattern.match(start_date_str):  # Check if the date string matches the pattern
                        try:
                            start_date = datetime.strptime(start_date_str, "%d.%m.%Y %H:%M")
                            start_date = pytz.timezone('Europe/Ljubljana').localize(start_date)
                        except ValueError:
                            print("Error parsing start date for NOTAM:", notam_number)
                            continue
            if detail.find(class_='kzps-notam-item-c') is not None:
                end_date_str = detail.find(class_='kzps-notam-item-c').get_text().strip()[3:]  # Remove the 'C) ' prefix
                if date_pattern.match(end_date_str):  # Check if the date string matches the pattern
                    try:
                        if end_date_str == 'PERM':
                            end_date = start_date + timedelta(hours=1000)
                        else:
                            # Handle "EST" abbreviation in the end date
                            if "EST" in end_date_str:
                                end_date_str = end_date_str.replace(" EST", "")
                            end_date = datetime.strptime(end_date_str, "%d.%m.%Y %H:%M")
                            end_date = pytz.timezone('Europe/Ljubljana').localize(end_date)
                    except ValueError:
                        print("Error parsing end date for NOTAM:", notam_number)
                        continue
        # Check if the NOTAM has valid start and end dates
        if start_date is not None and end_date is not None:
            # Check if the NOTAM is for today
            if start_date.date() <= today <= end_date.date():
                notams_by_day[today].append(notam_data_tuple)

    # Print the NOTAMs for today with feet to meters conversion for F) and G) data
    print("\n----------------------------------------")
    date_label = today.strftime('%A %d.%m.%Y')
    print(date_label)
    if notams_by_day[today]:
        for notam_data_tuple in notams_by_day[today]:
            print("----------------------------------------\n")
            notam_number, q_data, a_data, b_data, c_data, d_data, e_data, f_data, g_data, timestamp, kml_link = notam_data_tuple
            print(f"NOTAM Number: {notam_number}")
            if q_data:
                print(q_data)
            if a_data:
                print(a_data)
            if b_data:
                print(b_data)
            if c_data:
                print(c_data)
            if d_data:
                print(d_data)
            if e_data:
                print(e_data)
            if f_data:
                print(f_data)
            if g_data:
                print(g_data)
            if timestamp:
                print(f"Čas objave: {timestamp}")
            print(f"KML File: {kml_link}")
            
            # Save the NOTAM data to a JSON file
            if SAVE_JSON_FILES:
                save_notam_to_json(notam_data_tuple) 

    else:
        print("No NOTAMs. Yay!")
