import os
import pymongo
import time
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.environ.get("MONGODB_URI")
CLUSTER_NAME = "SmartParkingParams"
COLLECTION_NAME = "system_config"

def verify():
    if not MONGODB_URI:
        print("Error: MONGODB_URI not found.")
        return

    client = pymongo.MongoClient(MONGODB_URI)
    db = client[CLUSTER_NAME]
    collection = db[COLLECTION_NAME]
    
    doc = collection.find_one({"config_id": "main_tunnel"})
    
    if doc:
        print("--- MongoDB Document Found ---")
        print(f"Tunnel URL: {doc.get('tunnel_url')}")
        last_updated = doc.get('last_updated')
        print(f"Last Updated Timestamp: {last_updated}")
        
        current_time = time.time()
        diff = current_time - last_updated
        print(f"Seconds since update: {diff:.2f}")
        
        if diff < 120: # Updated in last 2 mins
            print("SUCCESS: Record was updated recently.")
        else:
            print("WARNING: Record is old.")
    else:
        print("Error: No config document found.")

if __name__ == "__main__":
    verify()
