



import os
import csv
import time
import pandas as pd
from datetime import datetime
from langchain_google_genai import GoogleGenerativeAI  # Corrected class for version 2.0.1

# Set your environment variables for Google and LangChain API keys
os.environ["GOOGLE_API_KEY"] = "AIzaSyCUS2y6JWETjUimFm_rZpF8kW-kAhRfTXc"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# Load the dataset
df = pd.read_csv('dataset.csv')  # Update with your actual dataset path

# Try to load existing output data, or create an empty DataFrame if file doesn't exist
try:
    old_df = pd.read_csv('output.csv')
    print(f"Loaded existing output.csv with {len(old_df)} rows.")
except FileNotFoundError:
    old_df = pd.DataFrame()  # Empty DataFrame if no file exists
    print("No existing output.csv found. It will be created during this run.")

# Initialize the Google Generative AI model
llm = GoogleGenerativeAI(model="gemini-1.5-pro")  # Correct class name for version 2.0.1

# Define the prompt template
prompt_template = """
Given an ingredient named "{ingredient}", output whether it contains any harmful chemicals. 
The categories you need to classify are USA, EU, sulfates, parabens, phthalates, synthetic colors, fragrance, triclosan, toluene, talc, lead, PEG, formaldehyde, diethanolamine, alcohol, hydroquinone, other_info, and natural. 

The response should be in this format:
- USA: (yes or no)
- EU: (yes or no)
- sulfates: (yes or no)
- parabens: (yes or no)
- phthalates: (yes or no)
- synthetic colors: (yes or no)
- fragrance: (yes or no)
- triclosan: (yes or no)
- toluene: (yes or no)
- talc: (yes or no)
- lead: (yes or no)
- PEG: (yes or no)
- formaldehyde: (yes or no)
- diethanolamine: (yes or no)
- alcohol: (yes or no)
- hydroquinone: (yes or no)
- other_info: (additional information)
- natural: (yes or no)
"""

# Function to parse AI response
def parse_ai_response(ai_response):
    output_dict = {
        'usa': None,
        'eu': None,
        'sulfates': None,
        'parabens': None,
        'phthalates': None,
        'synthetic colors': None,
        'fragrance': None,
        'triclosan': None,
        'toluene': None,
        'talc': None,
        'lead': None,
        'peg': None,
        'formaldehyde': None,
        'diethanolamine': None,
        'alcohol': None,
        'hydroquinone': None,
        'other_info': None,
        'natural': None,
        'ingredient': None,
        'timestamp': None
    }

    for line in ai_response.strip().split('\n'):
        if ': ' in line:
            key, value = line.split(': ', 1)
            key = key.strip().lower().replace('**', '').replace(' ', '_')  # Normalize keys
            value = value.strip().replace('"', '""')  # Escape quotes for CSV

            # Store the value in the dictionary
            output_dict[key] = f'"{value}"' if value else None

    return output_dict

# Function to get AI output for a given ingredient with retry on failure
def get_ai_output(llm, ingredient, max_retries=5, retry_delay=30):
    retries = 0
    formatted_prompt = prompt_template.format(ingredient=ingredient)

    while retries < max_retries:
        try:
            # Attempt to invoke the LLM
            response = llm.invoke(formatted_prompt)
            print(f"AI output for ingredient '{ingredient}':\n{response}\n")  # Print the AI output
            return response
        except Exception as e:
            retries += 1
            if 'ResourceExhausted' in str(e):
                print(f"ResourceExhausted: Quota exhausted while processing {ingredient}. Retrying in {retry_delay} seconds... (Attempt {retries}/{max_retries})")
            else:
                print(f"Error while processing {ingredient}: {e}. Retrying in {retry_delay} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(retry_delay)
    
    print(f"Failed to process {ingredient} after {max_retries} attempts.")
    return None  # Return None if it failed after all retries

# Batch size (You can modify this depending on API quota and limits)
batch_size = 2
sleep_time = 30  # Time to wait between batches (seconds)

# Define the expected columns
expected_columns = [
    'usa', 'eu', 'sulfates', 'parabens', 'phthalates',
    'synthetic colors', 'fragrance', 'triclosan', 'toluene',
    'talc', 'lead', 'peg', 'formaldehyde', 'diethanolamine',
    'alcohol', 'hydroquinone', 'other_info', 'natural'
]

# Function to process a batch and append results to CSV
def process_batch(batch, old_df):
    results = []
    
    for index, row in batch.iterrows():
        ingredient = row['name']
        ai_response = get_ai_output(llm, ingredient)
        output_dict = {
            'USA': 'Unknown',
            'EU': 'Unknown',
            'sulfates': 'Unknown',
            'parabens': 'Unknown',
            'phthalates': 'Unknown',
            'synthetic_colors': 'Unknown',
            'fragrance': 'Unknown',
            'triclosan': 'Unknown',
            'toluene': 'Unknown',
            'talc': 'Unknown',
            'lead': 'Unknown',
            'PEG': 'Unknown',
            'formaldehyde': 'Unknown',
            'diethanolamine': 'Unknown',
            'alcohol': 'Unknown',
            'hydroquinone': 'Unknown',
            'other_info': '',
            'natural': 'Unknown',
            'ingredient': '',
            'timestamp': ''
        }

        # Manually populate the dictionary by splitting lines and mapping them to categories
        for line in ai_response.strip().split("\n"):
            line = line.strip('- ')
            if ":**" in line:
                key, value = line.split(":**", 1)
                key = key.strip(" *").lower().replace(" ", "_")
                value = value.split("(")[0].strip()  # Take only the main value before any extra info in parentheses
                
                if key in output_dict:
                    output_dict[key] = value

        # Add ingredient name and timestamp explicitly
        # ingredient_name = "(1-methyl 2-(5-methylhex-4-en-2-yl)cyclopropyl)methanol"
        output_dict['ingredient'] = ingredient
        output_dict['timestamp'] = datetime.now().isoformat()

        # Convert parsed data into a DataFrame
        output_df = pd.DataFrame([output_dict])

        # Specify CSV file name
        # csv_file_name = 'output.csv'

        # # Check if the file exists and read the existing data
        # if os.path.isfile(csv_file_name):
        #     try:
        #         existing_df = pd.read_csv(csv_file_name, on_bad_lines='skip')
        #     except pd.errors.ParserError as e:
        #         print(f"Error reading CSV file: {e}")
        #         exit(1)

        #     # Check if the ingredient already exists in the DataFrame
        #     existing_row = existing_df[existing_df['ingredient'] == ingredient]
            
        #     if not existing_row.empty:
        #         # We found a matching row
        #         existing_values = existing_row.iloc[0]  # Get the first matching row as a Series
        #         updated = False
                
        #         # Check each field for changes
        #         for key in output_dict.keys():
        #             if key != 'timestamp' and key in existing_values.index:
        #                 if existing_values[key] != output_dict[key]:
        #                     updated = True
        #                     break
                
        #         # If updates were made, update the timestamp
        #         if updated:
        #             output_dict['timestamp'] = datetime.now().isoformat()  # Update timestamp if any value changes
        #             existing_df.update(pd.DataFrame([output_dict]))  # Update existing DataFrame
        #         else:
        #             # If no updates were made, keep the existing row's timestamp
        #             output_dict['timestamp'] = existing_values['timestamp']

        # # Create a new DataFrame from the output dictionary
        # output_df = pd.DataFrame([output_dict])

        # # Append the updated or existing row to the CSV
        # output_df.to_csv(csv_file_name, index=False, mode='a', header=not os.path.isfile(csv_file_name))


        # Initialize output_dict with "none" for each expected column
        # output_dict = {col: 'none' for col in expected_columns}
        # output_dict['ingredient'] = f'"{ingredient}"'  # Add ingredient name

        # if ai_response is None:
        #     # If API call failed, set timestamp and continue
        #     output_dict['timestamp'] = datetime.now().isoformat()
        #     results.append(output_dict)
        #     continue  # Skip to the next ingredient

        # # Parse AI response to structured data
        # parsed_response = parse_ai_response(ai_response)

        # # Update output_dict with parsed data
        # output_dict.update(parsed_response)

        # # Check if the ingredient already exists in the old data
        # if not old_df.empty and ingredient in old_df['ingredient'].values:
        #     old_row = old_df.loc[old_df['ingredient'] == ingredient]

        #     # Compare the new output with the old one
        #     if all(old_row[col].values[0] == output_dict.get(col, 'none') for col in expected_columns):
        #         # If the response is the same, keep the old timestamp
        #         output_dict['timestamp'] = old_row['timestamp'].values[0]
        #     else:
        #         # If the response has changed, update the timestamp
        #         output_dict['timestamp'] = datetime.now().isoformat()
        #         print(f"Updated response for ingredient: {ingredient}")
        # else:
        #     # New ingredient, assign a new timestamp
        #     output_dict['timestamp'] = datetime.now().isoformat()
        #     print(f"Added new ingredient: {ingredient}")

        # Append the output_dict to results list
        results.append(output_dict)
    
    return results

# Iterate through each ingredient in the dataset in batches
for i in range(0, len(df), batch_size):
    batch = df.iloc[i:i + batch_size]

    # Process the current batch and get the results
    batch_results = process_batch(batch, old_df)

    # Convert batch results to a DataFrame
    batch_df = pd.DataFrame(batch_results)

    if not batch_df.empty:
        # Append to existing output.csv without overwriting
        if os.path.exists('output.csv'):
            batch_df.to_csv('output.csv', mode='a', header=False, index=False, quoting=csv.QUOTE_ALL)
        else:
            batch_df.to_csv('output.csv', mode='w', header=True, index=False, quoting=csv.QUOTE_ALL)
        print(f"Appended {len(batch_df)} records to output.csv.")

    # Sleep between batches to avoid hitting the API rate limits
    print(f"Processed batch {i // batch_size + 1}. Sleeping for {sleep_time} seconds...")
    time.sleep(sleep_time)

print("Batch processing completed!")
