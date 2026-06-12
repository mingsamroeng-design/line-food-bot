import json
import os
import copy

DB_FILE = "data/bills.json"


def load_db():
    if not os.path.exists(DB_FILE):
        return {}

    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

def backup_bill(group_id):

    db = load_db()

    if group_id not in db:
        return

    db[group_id]["_backup"] = copy.deepcopy(db[group_id])

    save_db(db) 

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

    # ไม่ให้ snapshot ซ้อน history
    snapshot.pop("_history", None)

    history.append(snapshot)

    # เก็บย้อนหลังสูงสุด 20 ครั้ง
    if len(history) > 20:
        history.pop(0)

    save_db(db)       