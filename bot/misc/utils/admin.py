import json
from .main import JSON_PATH


def admin_exists(user_id: int):
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)

    return user_id in config['admins']