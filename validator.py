from config import get_cities


def validate_phone(phone: str):
    if phone.isnumeric() and len(phone) == 9:
        return True
    return False
