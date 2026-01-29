
import socket
import time
import re
import sqlite3
import os
import requests
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
import subprocess
import threading
import sys
import shutil

load_dotenv()

DB_NAME = "parking.db"
# MONGODB_URI should be set in environment variables
MONGODB_URI = os.environ.get("MONGODB_URI") 
CLUSTER_NAME = "SmartParkingParams"
COLLECTION_NAME = "system_config"

# Cloudflare Configuration
CLOUDFLARED_URL_WINDOWS = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
CLOUDFLARED_EXE = "cloudflared.exe"

class NetworkManager:
    _tunnel_process = None
    _public_url = None
    _lock = threading.Lock()

    @staticmethod
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    @staticmethod
    def _download_cloudflared():
        """Downloads cloudflared.exe if not present."""
        if not os.path.exists(CLOUDFLARED_EXE):
            print(f"[NetworkManager] cloudflared.exe not found. Downloading from {CLOUDFLARED_URL_WINDOWS}...")
            try:
                # Use verify=False to avoid SSL cert issues in some envs, but ideally use True
                response = requests.get(CLOUDFLARED_URL_WINDOWS, stream=True)
                response.raise_for_status()
                with open(CLOUDFLARED_EXE, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
                print("[NetworkManager] Download complete.")
            except Exception as e:
                print(f"[NetworkManager] Failed to download cloudflared: {e}")
                return False
        return True

    @staticmethod
    def _start_tunnel_thread():
        """Runs the tunnel in a background thread and captures the URL."""
        cmd = [CLOUDFLARED_EXE, "tunnel", "--url", "http://localhost:5000"]
        
        # Use subprocess to run the command
        # We need to capture stderr because cloudflared prints the URL there
        NetworkManager._tunnel_process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            bufsize=1
        )
        
        print(f"[NetworkManager] Cloudflare Tunnel Started (PID: {NetworkManager._tunnel_process.pid})")
        
        # Regex to find the URL
        url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
        
        # Read stderr line by line to find the URL
        while True:
            line = NetworkManager._tunnel_process.stderr.readline()
            if not line:
                break
            
            # print(f"[Cloudflared] {line.strip()}") # Optional: debug output
            
            match = url_pattern.search(line)
            if match:
                found_url = match.group(0)
                print(f"\n[NetworkManager] FOUND TUNNEL URL: {found_url}\n")
                
                with NetworkManager._lock:
                    NetworkManager._public_url = found_url
                
                # Sync immediately once found
                NetworkManager.sync_to_cloud(found_url)
                
                # We can stop reading aggressively now, but we need to keep the process alive
                # In a real app we might want to keep logging
                
    @staticmethod
    def get_public_url_auto():
        """
        Orchestrates the download and execution of the tunnel.
        """
        # 1. Download if needed
        if not NetworkManager._download_cloudflared():
            return None
            
        # 2. Start in background if not already running
        if NetworkManager._tunnel_process is None:
            t = threading.Thread(target=NetworkManager._start_tunnel_thread, daemon=True)
            t.start()
            
            # 3. Wait for URL (with timeout)
            print("[NetworkManager] Waiting for Tunnel URL...")
            attempts = 0
            while attempts < 30: # Wait up to 30 seconds
                with NetworkManager._lock:
                    if NetworkManager._public_url:
                        return NetworkManager._public_url
                time.sleep(1)
                attempts += 1
                
            print("[NetworkManager] Timed out waiting for Tunnel URL.")
            return None
        else:
            with NetworkManager._lock:
                return NetworkManager._public_url

    @staticmethod
    def update_db(local_ip, public_url):
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS network_config (
                            id INTEGER PRIMARY KEY CHECK (id = 1),
                            local_ip TEXT,
                            public_url TEXT,
                            last_updated TIMESTAMP
                        )''')
            c.execute("DELETE FROM network_config")
            c.execute("INSERT INTO network_config (id, local_ip, public_url, last_updated) VALUES (1, ?, ?, CURRENT_TIMESTAMP)", 
                      (local_ip, public_url))
            conn.commit()

    @staticmethod
    def sync_to_cloud(public_url):
        if not MONGODB_URI:
            print("[NetworkManager] WARNING: MONGODB_URI not set. Cloud sync skipped.")
            return

        try:
            client = MongoClient(MONGODB_URI)
            db = client[CLUSTER_NAME]
            collection = db[COLLECTION_NAME]
            
            result = collection.update_one(
                {"config_id": "main_tunnel"}, 
                {"$set": {"tunnel_url": public_url, "last_updated": time.time()}},
                upsert=True
            )
            print(f"[NetworkManager] Cloud Sync Success. Tunnel URL Updated.")
        except Exception as e:
            print(f"[NetworkManager] Cloud Sync FAILED: {e}")

    @staticmethod
    def initialize():
        local_ip = NetworkManager.get_local_ip()
        
        # New Auto Logic
        print("[NetworkManager] Initializing Auto-Tunnel...")
        public_url = NetworkManager.get_public_url_auto()
        
        if not public_url:
            print("[NetworkManager] Tunnel failed. Generating Local-Only QRs.")
            public_url = f"http://{local_ip}:5000"
            
        NetworkManager.update_db(local_ip, public_url)
        return local_ip, public_url

if __name__ == "__main__":
    NetworkManager.initialize()
    # Keep alive for testing
    while True:
        time.sleep(1)
