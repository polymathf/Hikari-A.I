import json
from pathlib import Path
import asyncio
import math
import time
from asyncio import sleep
from openai import AsyncOpenAI, APIError, RateLimitError, APIConnectionError
from aiogram import Bot, types

from db.group import get_group_style
from config import PROMPT_STYLES, DEEPSEEK_API_KEYS, DEEPSEEK_BASE_URL, model

from db.group import get_group_lang
from db.json_storage import clear_processed_messages, load_messages
from utils.escape_html import escape_html


class APIClientManager:
    """Менеджер для управления несколькими API ключами"""
    
    def __init__(self):
        self.api_keys = DEEPSEEK_API_KEYS
        self.current_key_index = 0
        self.failed_keys = set()
    
    def get_current_key(self):
        """Получить текущий активный ключ"""
        return self.api_keys[self.current_key_index]
    
    def rotate_key(self):
        """Переключиться на следующий доступный ключ"""
        original_index = self.current_key_index
        
        # Пытаемся найти рабочий ключ
        while True:
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            
            # Если ключ не в списке нерабочих и мы не прошли полный круг
            if self.current_key_index not in self.failed_keys:
                break
            
            # Если все ключи нерабочие
            if self.current_key_index == original_index:
                raise Exception("Все API ключи нерабочие")
        
        return self.get_current_key()
    
    def mark_key_as_failed(self, key_index):
        """Пометить ключ как нерабочий"""
        self.failed_keys.add(key_index)
    
    def reset_failed_keys(self):
        """Сбросить список нерабочих ключей"""
        self.failed_keys.clear()


# Глобальный менеджер API ключей
api_manager = APIClientManager()


async def calculate_digest_time(chat_id: int) -> float:
    from db.group import get_group_add_time
    
    add_time = await get_group_add_time(chat_id)
    if add_time is None:
        return 0
    
    offset = (chat_id % 86400)
    
    now = time.time()
    
    next_digest = math.floor((now - add_time) / 86400) * 86400 + add_time + offset
    
    if next_digest < now:
        next_digest += 86400
    
    return next_digest


async def split_long_message(message: str, max_length: int = 4096) -> list[str]:
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]


async def generate_digest_with_retry(chat_id: int, max_retries: int = len(DEEPSEEK_API_KEYS)):
    """Генерировать дайджест с повторными попытками при ошибках API"""
    
    messages = load_messages()
    chat_messages = [msg for msg in messages if msg.get("chat_id") == chat_id]
    
    if len(chat_messages) < 100:
        return None
    
    lang = await get_group_lang(chat_id)
    style = await get_group_style(chat_id) or "default"
    
    prompt_file = f"prompts/{PROMPT_STYLES[style]['files'][lang]}"
    
    if not Path(prompt_file).exists():
        prompt_file = f"prompts/prompt_{lang}.txt"
        if not Path(prompt_file).exists():
            prompt_file = "prompts/prompt_eng.txt"

    def sanitize_message(msg):
        sanitized = msg.copy()
        sanitized.pop("chat_id", None)
        sanitized.pop("user_id", None)
        if "reply_to" in sanitized and isinstance(sanitized["reply_to"], dict):
            sanitized["reply_to"].pop("user_id", None)
        return sanitized

    sanitized_messages = [sanitize_message(msg) for msg in chat_messages]
    
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_text = f.read()

    messages_for_api = [
        {"role": "system", "content": prompt_text},
        {"role": "user", "content": json.dumps(sanitized_messages, ensure_ascii=False)}
    ]

    # Пытаемся использовать разные ключи при ошибках
    for attempt in range(max_retries):
        try:
            # Получаем текущий ключ
            current_key = api_manager.get_current_key()
            current_index = api_manager.current_key_index
            
            # Инициализация клиента с текущим ключом
            client = AsyncOpenAI(
                api_key=current_key,
                base_url=DEEPSEEK_BASE_URL,
            )

            response = await client.chat.completions.create(
                model=model,
                messages=messages_for_api,
                temperature=0.3,
                top_p=0.95,
                max_tokens=8192,
                stream=False
            )
            
            full_response = ""
            if response.choices and response.choices[0].message:
                full_response = response.choices[0].message.content
            
            clear_processed_messages(chat_id)
            return full_response
            
        except (RateLimitError, APIError, APIConnectionError) as e:
            print(f"API Error with key {current_index}: {e}")
            
            # Помечаем текущий ключ как нерабочий
            api_manager.mark_key_as_failed(current_index)
            
            # Пытаемся переключиться на следующий ключ
            try:
                api_manager.rotate_key()
            except Exception as rotate_error:
                print(f"Все ключи нерабочие: {rotate_error}")
                break
            
            # Задержка перед следующей попыткой
            if attempt < max_retries - 1:
                await sleep(2 ** attempt)  # Экспоненциальная задержка
        
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    
    return None


async def generate_digest(chat_id: int):
    """Обертка для обратной совместимости"""
    return await generate_digest_with_retry(chat_id)


async def send_digest_with_retries(bot: Bot, chat_id: int, max_attempts: int = 5):
    attempt = 0
    last_error = None
    
    while attempt < max_attempts:
        try:
            digest = await generate_digest_with_retry(chat_id)
            if not digest:
                return False
                
            message_parts = await split_long_message(digest)
            first_message_sent = False
            
            for part in message_parts:
                sent_message = await bot.send_message(
                    chat_id,
                    part,
                    disable_notification=True, link_preview_options=types.LinkPreviewOptions(is_disabled=True)
                )

                if not first_message_sent:
                    try:
                        await bot.pin_chat_message(
                            chat_id=chat_id,
                            message_id=sent_message.message_id,
                            disable_notification=True
                        )
                        first_message_sent = True
                    except Exception:
                        first_message_sent = True
                await sleep(0.5)
            
            return True
            
        except Exception as e:
            attempt += 1
            last_error = e
            print(f"Send digest attempt {attempt} failed: {e}")
            
            if attempt < max_attempts:
                await sleep(5 * attempt)
    
    print(f"Failed to send digest after {max_attempts} attempts: {last_error}")
    return False


async def digest_scheduler(bot: Bot):
    while True:
        await asyncio.sleep(86400)
        from db.group import get_active_groups
        
        active_groups = await get_active_groups()
        for chat_id in active_groups:
            try:
                await send_digest_with_retries(bot, chat_id)
            except Exception as e:
                print(f"Error processing digest for chat {chat_id}: {e}")
                pass