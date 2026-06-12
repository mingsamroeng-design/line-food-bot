import os
import json
import copy


# ==========================
# Database File
# ==========================

DATA_DIR = "data"

DB_FILE = os.path.join(
    DATA_DIR,
    "db.json"
)


# ==========================
# Create data folder
# ==========================

if not os.path.exists(DATA_DIR):

    os.makedirs(DATA_DIR)


# ==========================
# Create db.json
# ==========================

if not os.path.exists(DB_FILE):

    with open(
        DB_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            {},
            f,
            ensure_ascii=False,
            indent=4,
        )


# ==========================
# Load Database
# ==========================

def load_db():

    with open(
        DB_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ==========================
# Save Database
# ==========================

def save_db(db):

    with open(
        DB_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            db,
            f,
            ensure_ascii=False,
            indent=4,
        )


# ==========================
# Push History
# Multi-Level Undo
# ==========================

def push_history(group_id):

    db = load_db()

    if group_id not in db:
        return

    bill = db[group_id]

    history = bill.setdefault(
        "_history",
        []
    )

    snapshot = copy.deepcopy(bill)

    # ไม่เก็บ history ซ้อนใน history
    snapshot.pop(
        "_history",
        None,
    )

    history.append(snapshot)

    # เก็บย้อนหลังสูงสุด 20 ขั้น
    MAX_HISTORY = 20

    if len(history) > MAX_HISTORY:

        history.pop(0)

    save_db(db)