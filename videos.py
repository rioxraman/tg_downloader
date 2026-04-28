from telethon import TelegramClient
import os

# Your Telegram API credentials
api_id = 25430351
api_hash = 'a788064d36c0b4a83b9a7963b748b4e1'

# Session file
session_name = 'session_chan_extract'

# Target channel or group ID/username
target = -1003295276194  # replace with your channel/group ID or username

# Output folder
download_dir = "videos"
os.makedirs(download_dir, exist_ok=True)

# Initialize client
client = TelegramClient(session_name, api_id, api_hash)

async def main():
    await client.start()
    print("Connected… downloading videos only")

    async for msg in client.iter_messages(target):
        # Check if message contains a video
        if msg.video:
            filename = msg.file.name or f"video_{msg.id}.mp4"
            filepath = os.path.join(download_dir, filename)

            print(f"Downloading: {filename}")
            await msg.download_media(file=filepath)

    print("Done!")

# Run the client
with client:
    client.loop.run_until_complete(main())
