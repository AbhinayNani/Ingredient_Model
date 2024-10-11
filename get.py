# import csv

# def fetch_row_by_ingredient(file_path, ingredient_name, column_name):
#     with open(file_path, mode='r', newline='', encoding='utf-8') as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             if row[column_name] == ingredient_name:
#                 return row
#     return None  # Return None if no match is found

# # Usage
# file_path = './ingredients_output.csv'  
# ingredient_name = '1 dimethicone' 
# column_name = 'ingredient' 

# result_row = fetch_row_by_ingredient(file_path, ingredient_name, column_name)
# if result_row:
#     print("Row found:", result_row)
# else:
#     print(f"No row found with ingredient: {ingredient_name}")
from flask import Flask, request, jsonify
import csv

app = Flask(__name__)

# Function to fetch rows based on ingredients from a CSV file
def fetch_rows_by_ingredients(file_path, ingredients, column_name):
    matching_rows = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row[column_name] in ingredients:
                formatted_row = {
                    'ingredient': row[column_name],
                    'USA': row.get('USA', 'no'),
                    'EU': row.get('EU', 'no'),
                    'sulfates': row.get('sulfates', 'no'),
                    'parabens': row.get('parabens', 'no'),
                    'synthetic_colors': row.get('synthetic_colors', 'no'),
                    'fragrance': row.get('fragrance', 'no'),
                    'triclosan': row.get('triclosan', 'no'),
                    'toluene': row.get('toluene', 'no'),
                    'talc': row.get('talc', 'no'),
                    'lead': row.get('lead', 'no'),
                    'PEG': row.get('PEG', 'yes'),
                    'formaldehyde': row.get('formaldehyde', 'no'),
                    'diethanolamine': row.get('diethanolamine', 'no'),
                    'alcohol': row.get('alcohol', 'no'),
                    'hydroquinone': row.get('hydroquinone', 'no'),
                    'other_info': row.get('other_info', 'None'),
                    'natural': row.get('natural', 'no'),
                }
                matching_rows.append(formatted_row)
    return matching_rows

# Route to handle POST requests with a list of ingredients
@app.route('/get', methods=['POST'])
def get_ingredients():
    print("Received a request")
    try:
        data = request.json
        ingredients = data.get('ingredients')
        
        if not ingredients:
            return jsonify({"error": "No ingredients provided"}), 400

        file_path = './ingredients_output.csv'
        column_name = 'ingredient'

        matching_rows = fetch_rows_by_ingredients(file_path, ingredients, column_name)

        if not matching_rows:
            return jsonify({"message": "No matching ingredients found"}), 404

        return jsonify({"matching_rows": matching_rows}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)

