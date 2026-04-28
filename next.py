# extract_usernames_batches.py
import csv
import asyncio
from telethon import TelegramClient

# === Your Telegram credentials ===
api_id = 25430351         # int
api_hash = 'a788064d36c0b4a83b9a7963b748b4e1'
session_name = 'session_chan_extract'  # local session file

# The channel or group identifier: either username ('telegram'), or invite link, or ID
target = 'Scalercommunity'  # e.g. 'python' or '-1001234567890'
# === Settings ===
batch_size = 10004     # users per CSV file

client = TelegramClient(session_name, api_id, api_hash)

async def main():
    await client.start()
    print(f"✅ Connected. Extracting from: {target}")

    batch_number = 2
    user_count = 0
    total_count = 0

    # open first file
    outfile = f'tele_usernames_batch_{batch_number}.csv'
    f = open(outfile, 'w', newline='', encoding='utf-8')
    writer = csv.writer(f)
    writer.writerow(['user_id', 'username', 'first_name', 'last_name', 'phone'])

    async for user in client.iter_participants(target):
        writer.writerow([
            user.id,
            user.username or '',
            user.first_name or '',
            user.last_name or '',
            getattr(user, 'phone', '') or ''
        ])
        user_count += 1
        total_count += 1

        # every batch_size users → new file
        if user_count >= batch_size:
            f.close()
            print(f"💾 Saved batch {batch_number} with {user_count} users")
            batch_number += 1
            outfile = f'tele_usernames_batch_{batch_number}.csv'
            f = open(outfile, 'w', newline='', encoding='utf-8')
            writer = csv.writer(f)
            writer.writerow(['user_id', 'username', 'first_name', 'last_name', 'phone'])
            user_count = 0

    f.close()
    print(f"\n✅ Done. Total users extracted: {total_count}")
    print(f"Created {batch_number} CSV file(s).")

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
