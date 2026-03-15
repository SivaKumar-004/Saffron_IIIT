import json
import os
from typing import List, Dict

DB_PATH = os.path.join(os.path.dirname(__file__), 'farmers.json')

def _load_db() -> List[Dict]:
    if not os.path.exists(DB_PATH):
        return []
    try:
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {DB_PATH}: {e}")
        return []

def _save_db(data: List[Dict]):
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=4)

def register_farmer(phone: str, region: str, name: str = "Unknown", crop: str = "Unknown") -> bool:
    """
    Registers a farmer in the system. Ensures no duplicate phone numbers.
    """
    db = _load_db()
    # Check if phone already exists
    for farmer in db:
        if farmer.get('phone') == phone:
            # Update existing
            farmer['region'] = region
            farmer['name'] = name
            farmer['crop'] = crop
            _save_db(db)
            return True
            
    db.append({
        "phone": phone,
        "region": region,
        "name": name,
        "crop": crop
    })
    _save_db(db)
    return True

def get_farmers_by_region(region: str) -> List[Dict]:
    """
    Returns a list of all farmers registered to a specific region.
    """
    db = _load_db()
    return [f for f in db if f.get('region', '').lower() == region.lower()]
