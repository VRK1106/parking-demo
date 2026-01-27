import flask
import json
import qr_generator
import os

app = flask.Flask(__name__)

# Initialize slot states (0: available, 1: unavailable)
slots_state = {i: 0 for i in range(1, 11)}

@app.route('/scan/slot<int:slot_id>')
def scan_slot(slot_id):
    if slot_id in slots_state:
        slots_state[slot_id] = 1 # Mark as unavailable
        return f"<h1>Slot {slot_id} marked as Unavailable</h1>"
    return "Slot not found", 404

@app.route('/qrcodes')
def qrcodes():
    # Define the directory to save QR codes
    save_dir = 'qrcodes'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    generated_files = []
    
    for i in range(1, 11):
        # QR code now points to the scan URL
        scan_url = flask.request.host_url + f'scan/slot{i}'
        filename = os.path.join(save_dir, f'slot{i}.png')
        qr_generator.save_qr_image(scan_url, filename)
        generated_files.append(filename)
    
    return f"Generated {len(generated_files)} QR codes pointing to scan URLs and saved them to the '{save_dir}' directory."

@app.route('/api/slot1')
def slot1():
    if slots_state[1] == 0:
        return json.dumps({'slot1': 'available'})
    else:
        return json.dumps({'slot1': 'unavailable'})

@app.route('/api/slot2')
def slot2():
    if slots_state[2] == 0:
        return json.dumps({'slot2': 'available'})
    else:
        return json.dumps({'slot2': 'unavailable'})

@app.route('/api/slot3')
def slot3():
    if slots_state[3] == 0:
        return json.dumps({'slot3': 'available'})
    else:
        return json.dumps({'slot3': 'unavailable'})

@app.route('/api/slot4')
def slot4():
    if slots_state[4] == 0:
        return json.dumps({'slot4': 'available'})
    else:
        return json.dumps({'slot4': 'unavailable'})

@app.route('/api/slot5')
def slot5():
    if slots_state[5] == 0:
        return json.dumps({'slot5': 'available'})
    else:
        return json.dumps({'slot5': 'unavailable'})

@app.route('/api/slot6')
def slot6():
    if slots_state[6] == 0:
        return json.dumps({'slot6': 'available'})
    else:
        return json.dumps({'slot6': 'unavailable'})

@app.route('/api/slot7')
def slot7():
    if slots_state[7] == 0:
        return json.dumps({'slot7': 'available'})
    else:
        return json.dumps({'slot7': 'unavailable'})

@app.route('/api/slot8')
def slot8():
    if slots_state[8] == 0:
        return json.dumps({'slot8': 'available'})
    else:
        return json.dumps({'slot8': 'unavailable'})

@app.route('/api/slot9')
def slot9():
    if slots_state[9] == 0:
        return json.dumps({'slot9': 'available'})
    else:
        return json.dumps({'slot9': 'unavailable'})

@app.route('/api/slot10')
def slot10():
    if slots_state[10] == 0:
        return json.dumps({'slot10': 'available'})
    else:
        return json.dumps({'slot10': 'unavailable'})


if __name__ == '__main__':
    app.run(host = "0.0.0.0",port = 5000,debug=True)
