from aiogram import Router, types, F
from aiogram.filters import Command
from digest import generate_digest, split_long_message
from utils.lang import t
from db.json_storage import load_messages
from db.group import get_group_lang
from asyncio import sleep
import time
from db.cooldown import set_cooldown, check_cooldown
from utils.escape_html import escape_html
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = Router()

generating_digests = {}

async def send_digest_with_retries(message: types.Message, max_attempts: int = 5):
    lang = await get_group_lang(message.chat.id) or "eng"
    attempt = 0
    last_error = None
    
    logger.info(f"Starting digest generation for chat {message.chat.id} (attempts: {max_attempts})")
    
    while attempt < max_attempts:
        try:
            logger.info(f"Attempt {attempt + 1} for chat {message.chat.id}")
            
            # Логируем процесс генерации дайджеста
            logger.debug(f"Calling generate_digest for chat {message.chat.id}")
            digest = await generate_digest(message.chat.id)
            
            if not digest or not digest.strip():
                logger.warning(f"No digest generated for chat {message.chat.id}. Empty result.")
                await message.answer(t("not_enough_messages", lang))
                return False
            
            logger.info(f"Digest generated successfully. Length: {len(digest)} chars")
            
            # Логируем установку кулдауна
            await set_cooldown(message.chat.id, "digest", 14400)
            logger.debug(f"Cooldown set for chat {message.chat.id}")
            
            # Логируем разделение сообщения
            logger.debug(f"Splitting digest for chat {message.chat.id}")
            message_parts = await split_long_message(digest)
            
            if not message_parts:
                logger.warning(f"No message parts after splitting for chat {message.chat.id}")
                await message.answer(t("not_enough_messages", lang))
                return False
            
            logger.info(f"Digest split into {len(message_parts)} parts")
            
            first_message_sent = False
            sent_parts = 0
            
            for i, part in enumerate(message_parts):
                if not part.strip():
                    logger.debug(f"Part {i} is empty, skipping")
                    continue
                    
                try:
                    logger.debug(f"Sending part {i+1}/{len(message_parts)} (length: {len(part)} chars)")
                    
                    sent_message = await message.answer(
                        part, disable_notification=True, link_preview_options=types.LinkPreviewOptions(is_disabled=True)
                    )
                    sent_parts += 1
                    
                    if not first_message_sent:
                        try:
                            logger.debug(f"Pinning message {sent_message.message_id} in chat {message.chat.id}")
                            await message.bot.pin_chat_message(
                                chat_id=message.chat.id,
                                message_id=sent_message.message_id,
                                disable_notification=True
                            )
                            logger.info(f"Message {sent_message.message_id} pinned successfully")
                            first_message_sent = True
                        except Exception as pin_error:
                            logger.error(f"Failed to pin message {sent_message.message_id}: {pin_error}")
                            first_message_sent = True
                    
                    await sleep(0.5)
                    
                except Exception as send_error:
                    logger.error(f"Failed to send message part {i+1}: {send_error}")
                    continue
            
            logger.info(f"Digest sent successfully. Sent {sent_parts} out of {len(message_parts)} parts")
            return True
            
        except Exception as e:
            attempt += 1
            last_error = e
            logger.error(f"Attempt {attempt} failed for chat {message.chat.id}: {e}", exc_info=True)
            
            if attempt < max_attempts:
                wait_time = 5 * attempt
                logger.info(f"Waiting {wait_time} seconds before next attempt")
                await sleep(wait_time)
    
    logger.error(f"All {max_attempts} attempts failed for chat {message.chat.id}. Last error: {last_error}")
    await message.answer(t("digest_error", lang))
    return False

@router.message(Command("digest"))
async def manual_digest(message: types.Message):
    lang = await get_group_lang(message.chat.id) or "eng"
    logger.info(f"Received /digest command from chat {message.chat.id} (language: {lang})")

    # Проверяем, не генерируется ли уже дайджест
    if generating_digests.get(message.chat.id, False):
        logger.warning(f"Digest already generating for chat {message.chat.id}")
        return

    # Проверяем кулдаун
    cooldown = await check_cooldown(message.chat.id, "digest")
    if cooldown > 0:
        hours = cooldown // 3600
        minutes = (cooldown % 3600) // 60
        logger.info(f"Cooldown active for chat {message.chat.id}: {hours}h {minutes}m remaining")
        await message.answer(
            t("digest_cooldown", lang).format(hours=hours, minutes=minutes)
        )
        return

    # Загружаем и проверяем сообщения
    logger.debug("Loading messages from storage")
    messages = load_messages()
    
    chat_messages = [msg for msg in messages if msg.get("chat_id") == message.chat.id]
    chat_msg_count = len(chat_messages)
    
    logger.info(f"Found {chat_msg_count} messages for chat {message.chat.id}")

    if chat_msg_count < 100:
        logger.warning(f"Not enough messages for chat {message.chat.id}: {chat_msg_count}/100")
        await message.answer(
            t("not_enough_messages", lang,
              count=chat_msg_count,
              needed=100 - chat_msg_count)
        )
        return

    # Начинаем генерацию дайджеста
    generating_digests[message.chat.id] = True
    logger.info(f"Starting digest generation process for chat {message.chat.id}")
    
    generating_message = await message.answer(t("digest_generating", lang))
    logger.debug("Sent 'generating' message to user")

    try:
        logger.info("Calling send_digest_with_retries")
        success = await send_digest_with_retries(message)
        
        if success:
            logger.info(f"Digest generated and sent successfully for chat {message.chat.id}")
        else:
            logger.warning(f"Digest generation failed for chat {message.chat.id}")
            
    except Exception as e:
        logger.error(f"Unexpected error in manual_digest for chat {message.chat.id}: {e}", exc_info=True)
        await message.answer(t("digest_error", lang))
    finally:
        generating_digests.pop(message.chat.id, None)
        logger.debug(f"Cleaned up generating_digests for chat {message.chat.id}")
        
        try:
            await generating_message.delete()
            logger.debug("Deleted 'generating' message")
        except Exception as delete_error:
            logger.error(f"Failed to delete generating message: {delete_error}")