import sqlite3
import os

# Database path
DB_PATH = os.path.join("database", "vehicles.db")


# Create database connection
def create_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    return conn


# Create all tables
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Vehicles table
    cursor.execute("""
   CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id TEXT PRIMARY KEY,
    owner_name TEXT NOT NULL,
    vehicle_type TEXT NOT NULL,
    license_number TEXT NOT NULL,
    public_key TEXT NOT NULL,
    trust_status TEXT NOT NULL,
    trust_score INTEGER NOT NULL,
    created_at TEXT NOT NULL
)
    """)

    # Authentication logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auth_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        status TEXT NOT NULL,
        validator_votes INTEGER,
        block_hash TEXT
    )
    """)

    # Attack logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attack_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id TEXT NOT NULL,
        attack_type TEXT NOT NULL,
        status TEXT NOT NULL,
        details TEXT,
        timestamp TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# Insert vehicle
def insert_vehicle(
    vehicle_id,
    owner_name,
    vehicle_type,
    license_number,
    public_key,
    trust_status,
    trust_score,
    created_at
):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO vehicles (
            vehicle_id,
            owner_name,
            vehicle_type,
            license_number,
            public_key,
            trust_status,
            trust_score,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vehicle_id,
            owner_name,
            vehicle_type,
            license_number,
            public_key,
            trust_status,
            trust_score,
            created_at
        ))

        conn.commit()

    finally:
        conn.close()

# Get all vehicles
def get_all_vehicles():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM vehicles")
    vehicles = cursor.fetchall()

    conn.close()
    return vehicles


# Authenticate vehicle
def authenticate_vehicle(vehicle_id, public_key):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM vehicles
        WHERE vehicle_id = ? AND public_key = ?
    """, (vehicle_id, public_key))

    vehicle = cursor.fetchone()

    conn.close()

    if not vehicle:
        return None

    trust_score = vehicle[6]   # trust_score column

    if trust_score < 50:
        return "BLOCKED"

    return vehicle


# Insert authentication log
def insert_auth_log(vehicle_id, timestamp, status, validator_votes, block_hash):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO auth_logs (
            vehicle_id,
            timestamp,
            status,
            validator_votes,
            block_hash
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            vehicle_id,
            timestamp,
            status,
            validator_votes,
            block_hash
        ))

        conn.commit()

    finally:
        conn.close()


# Get all authentication logs
def get_all_auth_logs():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM auth_logs")
    logs = cursor.fetchall()

    conn.close()
    return logs


# Insert attack log
def insert_attack_log(vehicle_id, attack_type, status, details, timestamp):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO attack_logs (
            vehicle_id,
            attack_type,
            status,
            details,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            vehicle_id,
            attack_type,
            status,
            details,
            timestamp
        ))

        conn.commit()

    finally:
        conn.close()


# Get all attack logs
def get_all_attack_logs():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attack_logs")
    logs = cursor.fetchall()

    conn.close()
    return logs

def get_blockchain_data():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM auth_logs")
    logs = cursor.fetchall()

    conn.close()

    blocks = []

    previous_hash = "GENESIS_BLOCK"

    for i, log in enumerate(logs):
        block = {
            "block_number": i + 1,
            "vehicle_id": log[1],
            "timestamp": log[2],
            "status": log[3],
            "previous_hash": previous_hash,
            "current_hash": log[5]
        }

        previous_hash = log[5]
        blocks.append(block)

    return blocks

def update_trust_score(vehicle_id, penalty):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT trust_score FROM vehicles WHERE vehicle_id=?",
        (vehicle_id,)
    )

    result = cursor.fetchone()

    if result:
        current_score = result[0]

        # Reduce trust score
        new_score = current_score - penalty

        if new_score < 0:
            new_score = 0

        # Decide trust status
        if new_score >= 50:
            new_status = "Trusted"

        elif new_score > 20:
            new_status = "Suspicious"

        else:
            new_status = "Blacklisted"

        cursor.execute("""
            UPDATE vehicles
            SET trust_score = ?, trust_status = ?
            WHERE vehicle_id = ?
        """, (
            new_score,
            new_status,
            vehicle_id
        ))

        conn.commit()

    conn.close()