import flask
from flask import redirect, jsonify
import os
import pymongo

app = flask.Flask(__name__)

# --- CONFIGURATION ---
# MongoDB URI from Render Environment
MONGODB_URI = os.environ.get("MONGODB_URI")
CLUSTER_NAME = "SmartParkingParams"
COLLECTION_NAME = "system_config"

@app.route('/')
def home():
    return "<h1>Smart Parking Gateway Active</h1><p>Magic Link Ready.</p>"

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/qr/<slot_id>')
def qr_redirect(slot_id):
    """
    Lightweight Gateway Redirection.
    """
    redirect_base = None
    
    if MONGODB_URI:
        try:
            client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
            db = client[CLUSTER_NAME]
            collection = db[COLLECTION_NAME]
            
            doc = collection.find_one({"config_id": "main_tunnel"})
            if doc and "tunnel_url" in doc:
                redirect_base = doc["tunnel_url"]
        except Exception as e:
            return f"<h1>Database Error</h1><p>{str(e)}</p>", 500
    else:
        return "<h1>Configuration Error</h1><p>MONGODB_URI not set on Render.</p>", 500

    if not redirect_base:
        return "<h1>System Offline</h1><p>No active tunnel found.</p>", 503

    # Redirect
    if slot_id.lower() == 'app':
        target = f"{redirect_base}/mobile"
    else:
        target = f"{redirect_base}/scan/{slot_id}"
        
    return redirect(target, code=302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
