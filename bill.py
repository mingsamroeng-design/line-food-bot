from database import load_db, save_db


def create_bill(group_id):

    db = load_db()

    db[group_id] = {
        "members": [],
        "items": [],
        "vat": 0,
        "service": 0
    }

    save_db(db)


def add_member(group_id, name):

    db = load_db()

    db.setdefault(
        group_id,
        {
            "members": [],
            "items": [],
            "vat": 0,
            "service": 0
        }
    )

    if name not in db[group_id]["members"]:
        db[group_id]["members"].append(name)

    save_db(db)


def add_item(group_id, name, price, eaters):

    db = load_db()

    db.setdefault(
        group_id,
        {
            "members": [],
            "items": [],
            "vat": 0,
            "service": 0
        }
    )

    db[group_id]["items"].append(
        {
            "name": name,
            "price": float(price),
            "eaters": eaters
        }
    )

    save_db(db)


def set_vat(group_id, percent):

    db = load_db()

    db[group_id]["vat"] = float(percent)

    save_db(db)


def set_service(group_id, percent):

    db = load_db()

    db[group_id]["service"] = float(percent)

    save_db(db)


def calculate(group_id):

    db = load_db()

    bill = db[group_id]

    result = {}

    subtotal = 0

    for member in bill["members"]:
        result[member] = 0

    for item in bill["items"]:

        subtotal += item["price"]

        share = item["price"] / len(item["eaters"])

        for eater in item["eaters"]:
            result[eater] += share

    service = subtotal * bill["service"] / 100

    vat = (subtotal + service) * bill["vat"] / 100

    extra = service + vat

    if len(bill["members"]) == 0:
        return {}, subtotal, service, vat

    per_person = extra / len(bill["members"])

    for member in bill["members"]:
        result[member] += per_person

    return result, subtotal, service, vat

def get_bill(group_id):

    db = load_db()

    db.setdefault(
        group_id,
        {
            "members": [],
            "items": [],
            "vat": 0,
            "service": 0
        }
    )

    save_db(db)

    return db[group_id]

def reset_bill(group_id):

    db = load_db()

    db[group_id] = {
        "members": [],
        "items": [],
        "vat": 0,
        "service": 0
    }

    save_db(db)

def remove_item(group_id, item_name):

    db = load_db()

    if group_id not in db:
        return False

    bill = db[group_id]

    old_count = len(bill["items"])

    bill["items"] = [
        item
        for item in bill["items"]
        if item["name"] != item_name
    ]

    save_db(db)

    return len(bill["items"]) != old_count

def remove_member(group_id, member_name):

    db = load_db()

    if group_id not in db:
        return False

    bill = db[group_id]

    # ลบสมาชิกออกจากรายชื่อ
    if member_name in bill["members"]:
        bill["members"].remove(member_name)
    else:
        return False

    # ลบสมาชิกออกจากรายการอาหารทุกเมนู
    for item in bill["items"]:

        if member_name in item["eaters"]:
            item["eaters"].remove(member_name)

    # ถ้าเมนูไหนไม่มีคนกินแล้ว ให้ลบเมนูนั้นทิ้ง
    bill["items"] = [
        item
        for item in bill["items"]
        if len(item["eaters"]) > 0
    ]

    save_db(db)

    return True