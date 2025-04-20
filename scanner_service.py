# /Users/khaja_21/Desktop/blood_group/scanner_service.py
from flask import Flask, jsonify
import base64
import MxFace.SDK  # Replace with actual SDK module name

app = Flask(__name__)

# Define the API key (replace with your actual key)
API_KEY = "12345-ABCDE-67890"  # Replace with the key provided by Mantra

@app.route('/capture_fingerprint')
def capture_fingerprint():
    try:
        # Initialize the MFS500 scanner with the API key
        scanner = MxFace.SDK.Scanner(api_key=API_KEY)  # Adjust based on SDK docs
        # Capture fingerprint
        fingerprint_data = scanner.Capture()  # Adjust method name as per SDK
        
        # Convert raw data to Base64
        base64_image = base64.b64encode(fingerprint_data).decode('utf-8')
        return jsonify({
            'status': 'success',
            'image': base64_image
        })
    except MxFace.SDK.ScannerNotDetectedError:  # Adjust exception name
        return jsonify({'status': 'error', 'message': 'Scanner not detected'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(host='localhost', port=5001, debug=True)