import requests
import time

def get_slot_status(slot_id):
    """
    Fetches the status of a specific slot from the external sensor API.
    
    Args:
        slot_id (str): The slot identifier (e.g., 'Slot1').
        
    Returns:
        str: 'available' or 'unavailable' (or 'error' if request fails).
    """
    try:
        # Extract the number from 'SlotX' or 'S00X' if necessary.
        # The specific requirement is to match 'Slot1' -> 'api/slot1'
        # Assuming input is like 'Slot1', 'Slot2', etc.
        
        # Simple extraction of digits, assuming slot_id ends in number
        # If slot_id is "Slot1", we want "1"
        slot_num_str = ''.join(filter(str.isdigit, slot_id))
        
        if not slot_num_str:
            return "error"
            
        slot_num = int(slot_num_str)
        
        url = f"https://parking-demo-2.onrender.com/api/slot{slot_num}"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            # The API returns dict like {'slot1': 'available'}
            # We need to extract the value.
            key = f"slot{slot_num}"
            return data.get(key, "unknown")
        else:
            print(f"[Sensor] API Error {response.status_code} for {url}")
            return "error"
            
    except Exception as e:
        print(f"[Sensor] Exception: {e}")
        return "error"

if __name__ == "__main__":
    # Test
    print(f"Slot1 Status: {get_slot_status('Slot1')}")

def sync_all_slots():
    """
    Fetches status for all 10 slots.
    Returns: dict { 'Slot1': 'available', 'Slot2': 'unavailable', ... }
    """
    statuses = {}
    print("[Sensor] Syncing all slots from external API...")
    for i in range(1, 11):
        slot_id = f"Slot{i}"
        status = get_slot_status(slot_id)
        statuses[slot_id] = status
        print(f"  > {slot_id}: {status}")
        time.sleep(0.5)
    return statuses
