"""
data_store.py — Zariya B2B Persistence Layer
Abstracted JSON I/O, ready for Google Cloud Storage migration.
"""

import json
import os
import uuid
from datetime import datetime

# ── File paths ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")

os.makedirs(DATA_DIR, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# LOCAL JSON HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _read_json(filepath: str, default):
    """Read a JSON file; return default if missing or corrupt."""
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return default


def _write_json(filepath: str, data) -> None:
    """Write data to a JSON file atomically."""
    tmp = filepath + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, filepath)


# ══════════════════════════════════════════════════════════════════════════════
# USERS
# ══════════════════════════════════════════════════════════════════════════════

def load_users() -> dict:
    """Return users dict keyed by Google email."""
    return _read_json(USERS_FILE, {})


def save_users(users: dict) -> None:
    _write_json(USERS_FILE, users)


def get_user(email: str) -> dict | None:
    return load_users().get(email)


def register_user(email: str, profile: dict) -> None:
    """Upsert a user profile."""
    users = load_users()
    users[email] = {**profile, "email": email, "registered_at": datetime.utcnow().isoformat()}
    save_users(users)


def is_registered(email: str) -> bool:
    return email in load_users()


# ══════════════════════════════════════════════════════════════════════════════
# INVENTORY
# ══════════════════════════════════════════════════════════════════════════════

def load_inventory() -> list:
    """Return list of product dicts."""
    return _read_json(INVENTORY_FILE, [])


def save_inventory(products: list) -> None:
    _write_json(INVENTORY_FILE, products)


def add_product(product: dict) -> str:
    """Add a product; returns new product id."""
    inventory = load_inventory()
    product_id = f"prod_{uuid.uuid4().hex[:8]}"
    inventory.append({**product, "id": product_id, "created_at": datetime.utcnow().isoformat()})
    save_inventory(inventory)
    return product_id


def remove_product(product_id: str) -> bool:
    inventory = load_inventory()
    new_inv = [p for p in inventory if p.get("id") != product_id]
    if len(new_inv) == len(inventory):
        return False
    save_inventory(new_inv)
    return True


def update_product(product_id: str, updates: dict) -> bool:
    inventory = load_inventory()
    for i, p in enumerate(inventory):
        if p.get("id") == product_id:
            inventory[i] = {**p, **updates, "updated_at": datetime.utcnow().isoformat()}
            save_inventory(inventory)
            return True
    return False


def get_products_by_wholesaler(email: str) -> list:
    return [p for p in load_inventory() if p.get("added_by") == email]


# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE CLOUD STORAGE STUBS  (swap these in for production)
# ══════════════════════════════════════════════════════════════════════════════

def upload_to_gcs(bucket_name: str, blob_name: str, data: str) -> None:
    """
    STUB — upload JSON string to GCS.
    Production implementation:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(data, content_type='application/json')
    """
    pass  # noqa


def download_from_gcs(bucket_name: str, blob_name: str) -> str | None:
    """
    STUB — download blob from GCS, return as string.
    Production implementation:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        return blob.download_as_text()
    """
    return None  # noqa
