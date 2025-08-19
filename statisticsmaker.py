import json
from pathlib import Path
from typing import Dict, List, Set, Any

def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    """Read JSON data from a local file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise Exception(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in {file_path}: {str(e)}")

def compute_differences(old_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[str]]:
    """Compute differences between two player data JSONs."""
    differences = []
    bosses: Set[str] = set()

    # Convert arrays to maps for lookup by player name
    old_data_map = {player['n']: player for player in old_data}
    new_data_map = {player['n']: player for player in new_data}

    # Collect all player names and boss IDs
    all_players = set(old_data_map.keys()) | set(new_data_map.keys())
    for player in old_data:
        if 'pa' in player:
            bosses.update(player['pa'].keys())
    for player in new_data:
        if 'pa' in player:
            bosses.update(player['pa'].keys())

    for player_name in sorted(all_players):
        old_player = old_data_map.get(player_name, {})
        new_player = new_data_map.get(player_name, {})
        player_diff = {'name': player_name}

        # Compare top-level fields (bpa, mpa)
        for field in ['bpa', 'mpa']:
            old_value = float(old_player.get(field, None)) if old_player.get(field) is not None else None
            new_value = float(new_player.get(field, None)) if new_player.get(field) is not None else None
            player_diff[field] = {
                'old': old_value,
                'new': new_value,
                'changed': old_value != new_value
            }

        # Compare pa fields
        player_diff['pa'] = {}
        for boss in sorted(bosses):
            old_boss_data = old_player.get('pa', {}).get(boss, {})
            new_boss_data = new_player.get('pa', {}).get(boss, {})

            # Handle rankPercent (float)
            old_rank_percent = old_boss_data.get('rankPercent', None)
            new_rank_percent = new_boss_data.get('rankPercent', None)
            old_rank_percent = float(old_rank_percent) if old_rank_percent is not None else None
            new_rank_percent = float(new_rank_percent) if new_rank_percent is not None else None

            # Handle rank (integer or non-numeric)
            old_rank = old_boss_data.get('rank', None)
            new_rank = new_boss_data.get('rank', None)
            try:
                old_rank = int(old_rank) if old_rank is not None and old_rank != '-' else None
                new_rank = int(new_rank) if new_rank is not None and new_rank != '-' else None
                rank_changed = old_rank != new_rank
            except (ValueError, TypeError):
                # If rank is non-numeric (e.g., '-'), keep as-is and compare directly
                old_rank = old_rank if old_rank is not None else None
                new_rank = new_rank if new_rank is not None else None
                rank_changed = old_rank != new_rank

            player_diff['pa'][boss] = {
                'rankPercent': {
                    'old': old_rank_percent,
                    'new': new_rank_percent,
                    'changed': old_rank_percent != new_rank_percent
                },
                'rank': {
                    'old': old_rank,
                    'new': new_rank,
                    'changed': rank_changed
                }
            }

        differences.append(player_diff)

    return differences, sorted(bosses)

def save_differences(differences: List[Dict[str, Any]], bosses: List[str], output_file: str):
    """Save differences to a JSON file."""
    output = {
        'differences': differences,
        'bosses': bosses
    }
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Differences saved to {output_file}")
    except Exception as e:
        print(f"Error saving to {output_file}: {str(e)}")

def main():
    # Local file paths
    OLD_FILE = 'player_data_20250818_231021.json'
    NEW_FILE = 'player_data_20250818_231026.json'
    OUTPUT_FILE = 'player_differences.json'

    print(f"Reading local files: {OLD_FILE}, {NEW_FILE}")
    try:
        old_data = read_json_file(OLD_FILE)
        new_data = read_json_file(NEW_FILE)
    except Exception as e:
        print(f"Error: {str(e)}")
        return

    try:
        differences, bosses = compute_differences(old_data, new_data)
        save_differences(differences, bosses, OUTPUT_FILE)
    except Exception as e:
        print(f"Error processing data: {str(e)}")

if __name__ == '__main__':
    main()
