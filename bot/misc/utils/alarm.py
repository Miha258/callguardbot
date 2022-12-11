import json
from re import S
from typing import Any
# from .main import JSON_PATH
JSON_PATH = 'C:\Coding\guardbot\AiogramTemplate-main\config.json'

def add_new_alarm(id: int, max: int, customer_id: int, reason: str):
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)

    config["alarms"][str(id)] = {
        "guards": [],
        "arrived_guards": 0,
        "max": max,
        "customer": customer_id,
        "status": 'Триває набір охоронців',
        "reason": reason
    }
    
    with open(JSON_PATH, 'w', encoding = 'utf-8') as f:
        json.dump(config, f, indent = 4, ensure_ascii=True)


def is_alarm_exists(id: int):
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)

    alarm = config["alarms"].get(str(id))
    if alarm:
        return True
    return False
    

def add_guard_to_alarm(id: int, guard_id: int):
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    
    alarm: list = config["alarms"].get(str(id))
    if alarm:
        alarm["guards"].append(guard_id)
        config["alarms"][str(id)]["guards"] = alarm["guards"]
        
        with open(JSON_PATH, 'w', encoding = 'utf-8') as f:
            json.dump(config, f, indent = 4, ensure_ascii=True)


def get_count_of_active_guards(alarm_id: int):
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)

    return list(config["accepted_alarms"].values()).count(str(alarm_id))


def remove_alarm(id: int):
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    
    alarm: list = config["alarms"].get(str(id))
    if alarm:
        del config["alarms"][str(id)]

        with open(JSON_PATH, 'w', encoding = 'utf-8') as f:
            json.dump(config, f, indent = 4, ensure_ascii = True)


def get_alarm_guards(id: int) -> list[int] | None:
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    
    alarm: list = config["alarms"].get(str(id))
    if alarm:
        return alarm["guards"]
    return None


def get_max_alarm_guards(id: int) -> int | None:
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    
    alarm: list = config["alarms"].get(str(id))
    if alarm:
        return alarm["max"]
    return None


def get_alarm_customer(id: int) -> str | None:
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    
    alarm: list = config["alarms"].get(str(id))
    if alarm:
        return alarm["customer"]
    return None


def get_alarm_reason(id: int) -> str | None:
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    
    alarm: list = config["alarms"].get(str(id))
    if alarm:
        return alarm["reason"]
    return None



def get_alarm_by_customer_id(user_id: int) -> int | None:
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    
    alarms: dict[str, Any] = config["alarms"]
    user = list(filter(lambda alarm: int(alarm[1]['customer']) == user_id, alarms.items()))
    if user:
        return int(user[0][0])

        
def add_to_accepted_alarms(guard_id: int, alarm_id: int):
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    
    config["accepted_alarms"][str(guard_id)] = str(alarm_id)
    
    with open(JSON_PATH, 'w', encoding = 'utf-8') as f:
        json.dump(config, f, indent = 4, ensure_ascii=True)


def get_from_accepted_alarms(guard_id: int) -> str | None:
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)

    accepted_alarm: str = config["accepted_alarms"].get(str(guard_id))
    return accepted_alarm
  

def remove_from_accepted_alarms(guard_id: int):
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    
    if config["accepted_alarms"].get(str(guard_id)):
        del config["accepted_alarms"][str(guard_id)]

    with open(JSON_PATH, 'w', encoding = 'utf-8') as f:
        json.dump(config, f, indent = 4, ensure_ascii=True)


def set_alarm_status(id: int, status: str):
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    
    alarm: list = config["alarms"].get(str(id))
    if alarm:
        config["alarms"][str(id)]["status"] = status
        
        with open(JSON_PATH, 'w', encoding = 'utf-8') as f:
            json.dump(config, f, indent = 4, ensure_ascii=True)


def get_alarm_status(id: int) -> str | None:
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    
    alarm: list = config["alarms"].get(str(id))
    if alarm:
        return config["alarms"][str(id)]["status"]
    return None

def update_count_of_arrived_guards(id: int) -> str | None:
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    
    alarm: list = config["alarms"].get(str(id))
    if alarm:
        currently_arrived_guards = config["alarms"][str(id)]["arrived_guards"]
        config["alarms"][str(id)]["arrived_guards"] = currently_arrived_guards + 1
        
        with open(JSON_PATH, 'w', encoding = 'utf-8') as f:
            json.dump(config, f, indent = 4, ensure_ascii=True)


def get_count_of_arrived_guards(id: int) -> str | None:
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    
    alarm: list = config["alarms"].get(str(id))
    if alarm:
        return config["alarms"][str(id)]["arrived_guards"]
    return None


def get_alarm_notation(reason: str) -> str:
    with open(JSON_PATH, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    
    return config["guards_notations"][reason]
        

