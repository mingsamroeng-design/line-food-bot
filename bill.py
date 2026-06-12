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