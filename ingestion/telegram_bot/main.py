from telethon import TelegramClient, events
from config import API_ID, API_HASH, SESSION_NAME, TARGET_CHANNELS
from parser import is_airdrop_related
from producer import send_to_queue
from loguru import logger

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.NewMessage())
async def handler(event):
    try:
        sender = await event.get_input_chat()
        if hasattr(sender, 'channel_id'):
            channel_id = sender.channel_id
            if str(channel_id) in TARGET_CHANNELS:
                text = event.message.message
                if is_airdrop_related(text):
                    data = {
                        "channel_id": channel_id,
                        "text": text,
                        "timestamp": str(event.message.date)
                    }
                    logger.info(f"[Airdrop Found] {text[:60]}...")
                    send_to_queue(data)
    except Exception as e:
        logger.error(f"Error processing message: {e}")

client.start()
logger.info("Scraper started...")
client.run_until_disconnected()
