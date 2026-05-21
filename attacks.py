import random
import hashlib
from datetime import datetime


def simulate_sybil_attack(vehicle_id):
    fake_nodes = random.randint(3, 10)

    return {
        "attack_type": "Sybil Attack",
        "vehicle_id": vehicle_id,
        "fake_nodes": fake_nodes,
        "status": "Detected",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def simulate_replay_attack(vehicle_id):
    old_timestamp = "2026-05-20 10:15:22"

    return {
        "attack_type": "Replay Attack",
        "vehicle_id": vehicle_id,
        "replayed_timestamp": old_timestamp,
        "status": "Blocked",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def simulate_fake_vehicle_attack(vehicle_id):
    fake_public_key = hashlib.sha256(vehicle_id.encode()).hexdigest()

    return {
        "attack_type": "Fake Vehicle Attack",
        "vehicle_id": vehicle_id,
        "fake_public_key": fake_public_key,
        "status": "Rejected",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def simulate_dos_attack(vehicle_id):
    request_count = random.randint(100, 1000)

    return {
        "attack_type": "DoS Attack",
        "vehicle_id": vehicle_id,
        "request_count": request_count,
        "status": "Mitigated",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def simulate_attack(vehicle_id, attack_type):
    if attack_type == "sybil":
        return simulate_sybil_attack(vehicle_id)

    elif attack_type == "replay":
        return simulate_replay_attack(vehicle_id)

    elif attack_type == "fake":
        return simulate_fake_vehicle_attack(vehicle_id)

    elif attack_type == "dos":
        return simulate_dos_attack(vehicle_id)

    else:
        return {
            "status": "Unknown Attack Type"
        }