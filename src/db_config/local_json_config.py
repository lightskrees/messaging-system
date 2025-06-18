import json
import os
from datetime import datetime

from src.config import Config as settings

BASE_DIR = "./local_messages"
os.makedirs(settings.LOCAL_DB_DIR, exist_ok=True)


def user_log_file(sender: str, receiver: str) -> str:

    # the log file structure for local storage:

    #     local_messages /
    #     ├── chris/
    #     │   └── eddy.json ← messages chris sent to Eddy
    #
    #     ├── eddy/
    #     │   └── chris.json ← messages Chris sent to Eddy
    #
    user_dir = os.path.join(settings.LOCAL_DB_DIR, sender)
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, f"{receiver}.json")


def register_sent_messages(sender: str, receiver: str, message: str):
    path = user_log_file(sender, receiver)
    message_info = {"from": sender, "to": receiver, "message": message, "timestamp": datetime.now().isoformat()}
    if os.path.exists(path):
        with open(path, "r") as f:
            messages = json.load(f)
    else:
        messages = []

    messages.append(message_info)

    with open(path, "w") as f:
        json.dump(messages, f, indent=2)
