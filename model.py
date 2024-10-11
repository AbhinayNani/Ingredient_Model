import requests
import csv
import pandas as pd
import os
import time

# Load your dataset
df = pd.read_csv('./dataset.csv')

# API endpoint
api_url = 'http://127.0.0.1:5000/parse'

# Output CSV file
output_file = './output.csv'

# Define the column headers based on the API response
headers = [
    'ingredient', 'USA', 'EU', 'sulfates', 'parabens', 'phthalates', 
    'synthetic_colors', 'fragrance', 'triclosan', 'toluene', 'talc', 
    'lead', 'PEG', 'formaldehyde', 'diethanolamine', 'alcohol', 
    'hydroquinone', 'other_info', 'natural'
]

# Check if the file already exists
file_exists = os.path.isfile(output_file)

# Open the CSV file in append mode
with open(output_file, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    # If the file doesn't exist, write the headers
    if not file_exists:
        writer.writerow(headers)

    # Iterate over the rows of your dataset
    for index, row in df.iterrows():
        data = {
            'string': row['name']
        }
        # Make the API call
        try:
            response = requests.post(api_url, json=data)
            response.raise_for_status()  # Raises HTTPError for bad responses
            response_data = response.json() 
            
            # Extract values from the API response
            row_data = [
                response_data.get('ingredient', ''),
                response_data.get('USA', ''),
                response_data.get('EU', ''),
                response_data.get('sulfates', ''),
                response_data.get('parabens', ''),
                response_data.get('phthalates', ''),
                response_data.get('synthetic_colors', ''),
                response_data.get('fragrance', ''),
                response_data.get('triclosan', ''),
                response_data.get('toluene', ''),
                response_data.get('talc', ''),
                response_data.get('lead', ''),
                response_data.get('PEG', ''),
                response_data.get('formaldehyde', ''),
                response_data.get('diethanolamine', ''),
                response_data.get('alcohol', ''),
                response_data.get('hydroquinone', ''),
                response_data.get('other_info', ''),
                response_data.get('natural', '')
            ]
        except requests.RequestException as e:
            print(f"Error with id {row['id']}: {e}")
            row_data = [''] * len(headers)  # Empty data if there's an error

        # Append the result to the CSV
        writer.writerow(row_data)
        
        # Optional: Add a delay to avoid hitting rate limits
        time.sleep(0.1)  # Adjust the sleep time as needed

print(f"API responses appended to {output_file}.")
