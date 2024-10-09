import os
import json

# Directory containing JSON files
directory = "recipes"

new_recipes = {}

# Iterate through all files in the directory
for filename in os.listdir(directory):
    # Check if the file is a JSON file
    if filename.endswith('.json'):
        file_path = os.path.join(directory, filename)
        
        # Open and read the JSON file
        with open(file_path, 'r') as recipe:
            data = json.load(recipe)
            new_recipe_resources = []
            new_recipe_name = os.path.splitext(filename)[0]
            # Check if "key" section exists
            if "key" in data:
                # Iterate through the "key" section
                for symbol, details in data["key"].items():
                    resource_count = 0 
                    resource_name = ""
                    for slot in data["pattern"]:
                        resource_count += slot.count(symbol)
                    if isinstance(details, dict):
                        for key, value in details.items():
                            resource_name = value.replace("minecraft:","")
                    new_recipe_resources.append({"item":f"{resource_name}","count":resource_count})
                new_recipes[new_recipe_name] = new_recipe_resources

with open("data/crafting.json",'w') as new_recipe_file:
    json.dump(new_recipes, new_recipe_file, indent=4)