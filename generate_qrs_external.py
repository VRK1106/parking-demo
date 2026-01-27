import qr_generator
import os

def generate_external_qrs(base_url):
    # Ensure base_url has no trailing slash to avoid double slashes
    if base_url.endswith('/'):
        base_url = base_url[:-1]
        
    save_dir = 'qrcodes_external'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    print(f"Generating QR codes for base URL: {base_url}")
    print(f"Saving to directory: {save_dir}")

    generated_files = []
    
    for i in range(1, 11):
        # Construct the scan URL for the hosted app
        scan_url = f"{base_url}/scan/slot{i}"
        filename = os.path.join(save_dir, f'slot{i}.png')
        
        qr_generator.save_qr_image(scan_url, filename)
        generated_files.append(filename)
        print(f"Generated: {filename} -> {scan_url}")
    
    print(f"\nSuccessfully generated {len(generated_files)} QR codes.")

if __name__ == "__main__":
    import sys
    
    print("--- Parking Slot QR Code Generator ---")
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter the base URL of your hosted application (e.g., https://my-app.onrender.com): ")
    
    if url:
        generate_external_qrs(url)
    else:
        print("No URL provided. Exiting.")
