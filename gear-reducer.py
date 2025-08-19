import json
import uuid

def reduce_gear_data(input_file, output_file):
    # Read the input JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Initialize the reduced data structure
    reduced_data = {
        "players": [],
        "errors": data.get("errors", [])
    }
    
    # Process each player
    for player in data.get("players", []):
        reduced_player = {
            "name": player.get("name"),
            "equipment": {
                "equipped_items": []
            }
        }
        
        # Process equipped items
        for item in player.get("equipment", {}).get("equipped_items", []):
            reduced_item = {
                "item": {
                    "id": item.get("item", {}).get("id")
                },
                "enchantments": []
            }
            
            # Include enchantments if present
            for enchantment in item.get("enchantments", []):
                reduced_enchantment = {
                    "display_string": enchantment.get("display_string"),
                    "enchantment_id": enchantment.get("enchantment_id"),
                    "enchantment_slot": enchantment.get("enchantment_slot")
                }
                reduced_item["enchantments"].append(reduced_enchantment)
            
            reduced_player["equipment"]["equipped_items"].append(reduced_item)
        
        reduced_data["players"].append(reduced_player)
    
    # Write the reduced data to the output file
    with open(output_file, 'w') as f:
        json.dump(reduced_data, f, indent=4)

if __name__ == "__main__":
    input_file = "gear.json"
    output_file = "gear_reduced.json"
    reduce_gear_data(input_file, output_file)
    print(f"Reduced JSON data has been written to {output_file}")
