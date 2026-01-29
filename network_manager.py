
import socket

import time
import re
import sqlite3

import os
import requests
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "parking.db"
# MONGODB_URI should be set in environment variables
# Example: mongodb+srv://<user>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_URI = os.environ.get("MONGODB_URI") 
CLUSTER_NAME = "SmartParkingParams"
COLLECTION_NAME = "system_config"

class NetworkManager:
    @staticmethod
    def get_local_ip():
        """
        Determines the local LAN IP address.
        """
        try:
            # Connect to an external server (doesn't actually send data) to get the routing IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    @staticmethod
    def get_public_url():
        """
        Returns the hardcoded Render URL.
        """
        url = "https://parking-demo-uepk.onrender.com"
        print(f"[NetworkManager] Using Hardcoded URL: {url}")
        return url

    @staticmethod
    def update_db(local_ip, public_url):
        """
        Stores the network config in the local SQLite database.
        """
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            # Create table if not exists
            c.execute('''CREATE TABLE IF NOT EXISTS network_config (
                            id INTEGER PRIMARY KEY CHECK (id = 1),
                            local_ip TEXT,
                            public_url TEXT,
                            last_updated TIMESTAMP
                        )''')
            
            # Upsert (Insert or Replace)
            # SQLite specific syntax for single row config
            c.execute("DELETE FROM network_config") # Clear old
            c.execute("INSERT INTO network_config (id, local_ip, public_url, last_updated) VALUES (1, ?, ?, CURRENT_TIMESTAMP)", 
                      (local_ip, public_url))
            conn.commit()
        print(f"[NetworkManager] Network Config Saved: IP={local_ip}, URL={public_url}")

    @staticmethod
    def sync_to_cloud(public_url):
        """
        Syncs the current public tunnel URL to MongoDB Atlas.
        This allows the static Render app to know where to redirect.
        """
        if not MONGODB_URI:
            print("[NetworkManager] WARNING: MONGODB_URI not set. Cloud sync skipped.")
            return

        try:
            client = MongoClient(MONGODB_URI)
            db = client[CLUSTER_NAME]
            collection = db[COLLECTION_NAME]
            
            # Upsert the config document
            # We use a fixed _id or a known filter to look it up
            result = collection.update_one(
                {"config_id": "main_tunnel"}, 
                {"$set": {"tunnel_url": public_url, "last_updated": time.time()}},
                upsert=True
            )
            print(f"[NetworkManager] Cloud Sync Success. Matched: {result.matched_count}, Modified: {result.modified_count}")
        except Exception as e:
            print(f"[NetworkManager] Cloud Sync FAILED: {e}")

    @staticmethod
    def initialize():
        local_ip = NetworkManager.get_local_ip()
        
        # 1. Start Tunnel Infrastructure (Docker Removed)
        print("[NetworkManager] Skipping Tunnel Logic (Docker Removed).")
        # If you were using 'cloudflared' directly, you could start it here.
        
        # 2. Extract URL
        public_url = NetworkManager.get_public_url()
        
        # Fallback if no public URL (e.g. running locally without tunnel)
        if not public_url:
            print("[NetworkManager] Warning: No public tunnel found. QRs will be local-only.")
            public_url = f"http://{local_ip}:5000"
            
        NetworkManager.update_db(local_ip, public_url)
        
        # 3. Sync to MongoDB (Cloud Dictionary)
        print("[NetworkManager] Syncing to Cloud Dictionary...")
        NetworkManager.sync_to_cloud(public_url)
        
        return local_ip, public_url

if __name__ == "__main__":
    # Test run
    NetworkManager.initialize()
