from config import get_cities


def validate_phone(phone: str):
    if phone.replace('+', '').isnumeric() and len(phone) == 13 and phone.startswith('+380'):
        return True
    return False



