# extract_split_csv.py
import csv
import asyncio
import time
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import User
# Replace these with your values from my.telegram.org

api_id = 25430351         # int
api_hash = 'a788064d36c0b4a83b9a7963b748b4e1'
session_name = 'session_chan_extract'  # local session file


#The channel or group identifier: either username ('telegram'), or invite 
message_limit = 50000000
target = -1001325205872
# --- Split size: how many unique users per file ---
split_size = 200  # e.g., 5000 users per CSV

client = TelegramClient(session_name, api_id, api_hash)
FILENAME = "abhi_members"

async def main():
    await client.start()
    print(f"✅ Connected. Scanning messages from '{target}'...")

    seen = set()
    part_number = 1
    count_in_file = 0
    total_count = 0

    # Create first output file
    file_name = f"{FILENAME}{part_number}.csv"
    f = open(file_name, "w", newline="", encoding="utf-8")
    writer = csv.writer(f)
    writer.writerow(["user_id", "username", "first_name", "last_name"])

    async for msg in client.iter_messages(target, limit=message_limit):
        sender = msg.sender
        if isinstance(sender, User) and sender.id not in seen:
            seen.add(sender.id)
            writer.writerow([
                sender.id,
                sender.username or "",
                sender.first_name or "",
                sender.last_name or ""
            ])
            count_in_file += 1
            total_count += 1

            if total_count % 100 == 0:
                print(f"Collected {total_count} unique users...")

            # Split into multiple CSVs when size is reached
            if count_in_file >= split_size:
                f.close()
                print(f"💾 Saved {count_in_file} users to {file_name}")
                part_number += 1
                file_name = f"{FILENAME}{part_number}.csv"
                f = open(file_name, "w", newline="", encoding="utf-8")
                writer = csv.writer(f)
                writer.writerow(["user_id", "username", "first_name", "last_name"])
                count_in_file = 0

        # Handle Telegram rate limiting
        try:
            await asyncio.sleep(0.1)
        except FloodWaitError as e:
            print(f"⚠️ FloodWait: sleeping {e.seconds} seconds...")
            time.sleep(e.seconds)

    # Save last open file
    f.close()
    print(f"\n✅ Done! Total unique users: {len(seen)}")
    print(f"📂 Created {part_number} CSV file(s).")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())