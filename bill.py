from database import (
    load_db,
    save_db,
    push_history,
)


# ==========================
# Create Bill
# ==========================
def create_bill(group_id):

    db = load_db()

    db[group_id] = {
        "members": [],
        "items": [],
        "vat": 0,
        "service": 0,
        "_history": [],
    }

    save_db(db)


# ==========================
# Reset Bill
# ==========================
def reset_bill(group_id):

    db = load_db()

    if group_id not in db:
        return

    push_history(group_id)

    db = load_db()

    db[group_id]["members"] = []

    db[group_id]["items"] = []

    db[group_id]["vat"] = 0

    db[group_id]["service"] = 0

    save_db(db)


# ==========================
# Get Bill
# ==========================
def get_bill(group_id):

    db = load_db()

    if group_id not in db:

        create_bill(group_id)

        db = load_db()

    return db[group_id]


# ==========================
# Add Member
# ==========================
def add_member(group_id, member_name):

    db = load_db()

    if group_id not in db:
        create_bill(group_id)
        db = load_db()

    push_history(group_id)

    db = load_db()

    bill = db[group_id]

    if member_name not in bill["members"]:

        bill["members"].append(member_name)

        save_db(db)


# ==========================
# Remove Member
# ==========================
def remove_member(group_id, member_name):

    db = load_db()

    if group_id not in db:
        return False

    if member_name not in db[group_id]["members"]:
        return False

    push_history(group_id)

    db = load_db()

    bill = db[group_id]

    bill["members"].remove(member_name)

    # ลบชื่อออกจากรายการอาหาร
    for item in bill["items"]:

        if member_name in item["eaters"]:

            item["eaters"].remove(member_name)

    # ลบเมนูที่ไม่มีคนกิน
    bill["items"] = [

        item

        for item in bill["items"]

        if len(item["eaters"]) > 0

    ]

    save_db(db)

    return True


# ==========================
# Add Item
# ==========================
def add_item(
    group_id,
    item_name,
    price,
    eaters,
):

    db = load_db()

    if group_id not in db:
        create_bill(group_id)
        db = load_db()

    push_history(group_id)

    db = load_db()

    bill = db[group_id]

    bill["items"].append(

        {

            "name": item_name,

            "price": float(price),

            "eaters": list(eaters),

        }

    )

    save_db(db)


# ==========================
# Remove Item
# ==========================
def remove_item(
    group_id,
    item_name,
):

    db = load_db()

    if group_id not in db:
        return False

    bill = db[group_id]

    found = False

    for item in bill["items"]:

        if item["name"] == item_name:

            found = True

            break

    if not found:
        return False

    push_history(group_id)

    db = load_db()

    bill = db[group_id]

    bill["items"] = [

        item

        for item in bill["items"]

        if item["name"] != item_name

    ]

    save_db(db)

    return True


# ==========================
# Set VAT
# ==========================
def set_vat(group_id, percent):

    db = load_db()

    if group_id not in db:
        create_bill(group_id)
        db = load_db()

    push_history(group_id)

    db = load_db()

    db[group_id]["vat"] = float(percent)

    save_db(db)


# ==========================
# Set Service
# ==========================
def set_service(group_id, percent):

    db = load_db()

    if group_id not in db:
        create_bill(group_id)
        db = load_db()

    push_history(group_id)

    db = load_db()

    db[group_id]["service"] = float(percent)

    save_db(db)


# ==========================
# Calculate
# ==========================
def calculate(group_id):

    db = load_db()

    if group_id not in db:
        return {}, 0, 0, 0

    bill = db[group_id]

    members = bill["members"]

    result = {}

    for member in members:
        result[member] = 0.0

    subtotal = 0.0

    for item in bill["items"]:

        price = float(item["price"])

        eaters = item["eaters"]

        subtotal += price

        if len(eaters) == 0:
            continue

        share = price / len(eaters)

        for person in eaters:

            if person not in result:
                result[person] = 0.0

            result[person] += share

    service = (
        subtotal
        * bill["service"]
        / 100
    )

    vat = (
        (subtotal + service)
        * bill["vat"]
        / 100
    )

    total_extra = service + vat

    if subtotal > 0:

        ratio = total_extra / subtotal

        for person in result:

            result[person] *= (
                1 + ratio
            )

    return (
        result,
        subtotal,
        service,
        vat,
    )


# ==========================
# Multi-Level Undo
# ==========================
def undo_bill(group_id):

    db = load_db()

    if group_id not in db:
        return False

    bill = db[group_id]

    history = bill.get(
        "_history",
        []
    )

    if len(history) == 0:
        return False

    previous = history.pop()

    # เก็บ history ที่เหลือไว้
    previous["_history"] = history

    db[group_id] = previous

    save_db(db)

    return True