import json
from .main import JSON_PATH


def get_cities() -> dict[str, int]:
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config: dict = json.load(f)
        return config["cities"]
        

def add_city(city: str, chat_id: int):
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    
    config["cities"][city] = chat_id
        
    with open(JSON_PATH, 'w', encoding = 'utf-8') as f:
        json.dump(config, f, indent = 4, ensure_ascii = True)


def remove_city(city: str):
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)

    del config["cities"][city]
        
    with open(JSON_PATH, 'w', encoding = 'utf-8') as f:
        json.dump(config, f, indent = 4, ensure_ascii = True)