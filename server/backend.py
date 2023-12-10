from flask import Flask, request, jsonify
import db_config

app = Flask(__name__)

# Endpoint to validate license plate
@app.route('/validate_license_plate', methods=['POST'])
def validate_license_plate():
    data = request.get_json()

    if 'license_plate' in data:
        license_plate = data['license_plate']

        result = db_config.validate_license_plate(license_plate)

        return jsonify({"result": result})

    return jsonify({"error": "License plate not provided"}), 400

# Endpoint to insert license plate
@app.route('/insert_license_plate', methods=['POST'])
def insert_license_plate():
    data = request.get_json()

    if 'license_plate' in data:
        license_plate = data['license_plate']

        success = db_config.insert_license_plate(license_plate)

        if success:
            return jsonify({"message" : "License plate inserted successfully"})
        else:
            return jsonify({"message" : "Failed to insert license plate"}), 500

    return jsonify({"error": "License plate not provided"}), 400

@app.route('/get_all_plate_numbers', methods=['GET'])
def get_all_plate_numbers():
    plate_numbers = db_config.get_all_plate_numbers()

    if plate_numbers is not None:
        return jsonify({"plate_numbers": plate_numbers})
    else:
        return jsonify({"error": "Failed to retrieve plate numbers"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3001)