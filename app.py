from attacks import simulate_attack
from flask import Flask, render_template, request
from database import (
    create_tables,
    insert_vehicle,
    get_all_vehicles,
    authenticate_vehicle,
    insert_auth_log,
    get_all_auth_logs,
    insert_attack_log,
    get_all_attack_logs,
    update_trust_score,
    get_blockchain_data
)

from datetime import datetime
import hashlib

app = Flask(__name__)

# Create database tables
create_tables()


# HOME PAGE
@app.route('/')
def home():
    return "Secure IoV Authentication System"


# VEHICLE REGISTRATION
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        vehicle_id = request.form['vehicle_id']
        owner_name = request.form['owner_name']
        vehicle_type = request.form['vehicle_type']
        license_number = request.form['license_number']
        public_key = request.form['public_key']

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        insert_vehicle(
            vehicle_id,
            owner_name,
            vehicle_type,
            license_number,
            public_key,
            "Trusted",
            100,
            created_at
        )

        return "Vehicle Registered Successfully!"

    return render_template('register.html')


# VIEW REGISTERED VEHICLES
@app.route('/view-vehicles')
def view_vehicles():
    vehicles = get_all_vehicles()
    return render_template('dashboard.html', vehicles=vehicles)


# VEHICLE LOGIN / AUTHENTICATION
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        vehicle_id = request.form['vehicle_id']
        public_key = request.form['public_key']

        vehicle = authenticate_vehicle(vehicle_id, public_key)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # BLOCK LOW TRUST / BLACKLISTED VEHICLES
        if vehicle == "BLOCKED":
            insert_auth_log(
                vehicle_id,
                timestamp,
                "Blocked",
                0,
                "BLOCKED_TRUST_SCORE"
            )

            return "Authentication Denied: Vehicle is Suspicious or Blacklisted"

        # SUCCESS
        elif vehicle:
            status = "Authenticated"
            validator_votes = 5

            block_data = vehicle_id + timestamp + status
            block_hash = hashlib.sha256(block_data.encode()).hexdigest()

            insert_auth_log(
                vehicle_id,
                timestamp,
                status,
                validator_votes,
                block_hash
            )

            return "Vehicle Authentication Successful!"

        # INVALID LOGIN
        else:
            insert_auth_log(
                vehicle_id,
                timestamp,
                "Failed",
                0,
                "INVALID_AUTH"
            )

            return "Authentication Failed!"

    return render_template('login.html')

# AUTH LOGS
@app.route('/auth-logs')
def auth_logs():
    logs = get_all_auth_logs()
    return render_template('auth_logs.html', logs=logs)


# ATTACK PAGE
@app.route('/attacks')
def attacks():
    return render_template('attacks.html')


# SIMULATE ATTACK
@app.route('/simulate-attack', methods=['GET', 'POST'])
def simulate_attack_route():
    if request.method == 'POST':
        vehicle_id = request.form['vehicle_id']
        attack_type = request.form['attack_type']

        result = simulate_attack(vehicle_id, attack_type)

        insert_attack_log(
            vehicle_id,
            result['attack_type'],
            result['status'],
            str(result),
            result['timestamp']
        )

        if result['status'] == 'Detected':
            update_trust_score(vehicle_id, 20)

        return render_template('attacks.html', result=result)

    return render_template('attacks.html')

# ATTACK LOGS
@app.route('/attack-logs')
def attack_logs():
    logs = get_all_attack_logs()
    return render_template('attack_logs.html', logs=logs)


# SECURITY DASHBOARD
@app.route('/security-dashboard')
def security_dashboard():
    auth_logs = get_all_auth_logs()
    attack_logs = get_all_attack_logs()

    total_auth = len(auth_logs)
    total_attacks = len(attack_logs)

    detected_attacks = 0

    for log in attack_logs:
        if log[3] == "Detected":
            detected_attacks += 1

    return render_template(
        'security_dashboard.html',
        total_auth=total_auth,
        total_attacks=total_attacks,
        detected_attacks=detected_attacks
    )


# BLOCKCHAIN VIEW
@app.route('/blockchain')
def blockchain():
    blocks = get_blockchain_data()
    return render_template('blockchain.html', blocks=blocks)


# RUN APP
if __name__ == '__main__':
    app.run(debug=False)