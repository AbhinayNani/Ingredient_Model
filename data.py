import pandas as pd
import json

# Load the dataset
df = pd.read_csv('./dataset.csv')  # Replace with your actual dataset file

# Concatenate all values in the 'name' column into a single string, separated by commas
concatenated_string = '; '.join(df['name'].tolist())

# Create the final JSON structure
result = {"string": concatenated_string}

# Convert the dictionary to a JSON string
json_result = json.dumps(result, indent=4)

# Print the final JSON result
print(json_result)

# Optionally, write the JSON result to a file
with open('aout.json', 'w') as file:
    file.write(json_result)
