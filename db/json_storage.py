import json
from pathlib import Path
from datetime import datetime
import re

STORAGE_PATH = Path("messages.json")
MAX_MESSAGES = 1000
MAX_MESSAGE_LENGTH = 500

STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
if not STORAGE_PATH.exists():
    STORAGE_PATH.write_text("[]", encoding="utf-8")

def is_meaningless_message(text: str) -> bool:
    text = text.strip()
    
    if len(text) > MAX_MESSAGE_LENGTH:
        return True
    
    return False

def load_messages():
    with open(STORAGE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_messages(messages: list):
    if len(messages) > MAX_MESSAGES:
        messages = messages[-MAX_MESSAGES:]

    total_length = 0
    trimmed = []

    for msg in reversed(messages):
        content = msg.get("content", "")
        total_length += len(content)
        if total_length > 25000:
            break
        trimmed.append(msg)

    trimmed = list(reversed(trimmed))

    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, ensure_ascii=False, indent=2)

def clear_processed_messages(chat_id: int):
    messages = load_messages()
    remaining_messages = [msg for msg in messages if msg.get("chat_id") != chat_id]
    save_messages(remaining_messages)

def update_user_gender(user_id: int, gender: str):
    with open("messages.json", "r", encoding="utf-8") as f:
        messages = json.load(f)

    for msg in messages:
        if msg["user_id"] == user_id:
            msg["gender"] = gender

    with open("messages.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)

def get_user_gender(user_id: int) -> str:
    messages = load_messages()
    for msg in reversed(messages):
        if msg.get("user_id") == user_id:
            return msg.get("gender", "auto")
    return "auto"

def save_message_entry(entry: dict):
    if is_meaningless_message(entry.get("content", "")):
        return False
    
    user_id = entry.get("user_id")
    if user_id is not None:
        entry["gender"] = get_user_gender(user_id)
    
    messages = load_messages()
    messages.append(entry)
    save_messages(messages)
    return True