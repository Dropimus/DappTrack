from telethon import TelegramClient, events
import config

client = TelegramClient('session_session', config.API_ID, config.API_HASH)

async def get_channel_entities():
    """Resolve usernames to full channel entities (docs: tl.telethon.dev/en/stable/modules/client.html#get_entity)."""
    entities = []
    for username in config.CHANNELS:
        try:
            entity = await client.get_entity(username)
            entities.append(entity)
            print(f"Resolved {username} → {entity.id}")
        except Exception as e:
            print(f"Failed to resolve {username}: {e}")
    return entities

async def scrape_past_posts(entity, limit=5):
    """Fetch the last `limit` messages from a channel"""
    print(f"\n[Fetching last {limit} posts from {entity.title or entity.username}]")
    async for msg in client.iter_messages(entity, limit=limit):
        if msg.text:
            print(f"↳ {msg.date} — {msg.text[:200]}")

async def main():
    # resolve channel entities
    entities = await get_channel_entities()
    if not entities:
        print("No channels resolved; exiting.")
        return

    # scrape past posts
    for ent in entities:
        await scrape_past_posts(ent)

    # register a single handler for new messages in all entities
    @client.on(events.NewMessage(chats=entities))
    async def new_message(event):
        chat = event.chat or await event.get_chat()
        name = getattr(chat, 'title', getattr(chat, 'username', 'Unknown'))
        print(f"\n[NEW POST in {name} @ {event.message.date}]")
        print(event.text or "<non-text message>")

    print("\nListening for NEW posts... ")
    await client.run_until_disconnected()

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())

