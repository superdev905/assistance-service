
def format_business_details(details: dict) -> dict:
    if not details:
        return None

    return {"address": details["address"],
            "latitude": details["latitude"],
            "longitude": details["longitude"],
            "business_name": details["business_name"],
            "rut": details["rut"],
            }


def format_construction_details(details: dict) -> dict:
    if not details:
        return None

    return {"address": details["address"],
            "latitude": details["latitude"],
            "longitude": details["longitude"],
            "name": details["name"],
            }
