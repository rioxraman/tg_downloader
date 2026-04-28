# extract_usernames_telethon.py
import csv
import asyncio
from telethon import TelegramClient

# Replace these with your values from my.telegram.org

api_id = 25430351         # int
api_hash = 'a788064d36c0b4a83b9a7963b748b4e1'
session_name = 'session_chan_extract'  # local session file

# The channel or group identifier: either username ('telegram'), or invite link, or ID

# The channel or group identifier: either username ('telegram'), or invite link, or ID
target = "Shortdramafull" #cse  # e.g. 'python' or '-1001234567890'

client = TelegramClient(session_name, api_id, api_hash)

async def main():
    await client.start()  # will prompt for phone / code once
    outfile = 'tele_usernames_shortreels.csv'
    with open(outfile, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['user_id', 'username', 'first_name', 'last_name', 'phone'])  # phone may be None

        # iter_participants handles large lists and pagination
        async for user in client.iter_participants(target,aggressive=True):
            writer.writerow([
                user.id,
                user.username or '',
                user.first_name or '',
                user.last_name or '',
                getattr(user, 'phone', '') or ''
            ])
    print(f'Done — saved to {outfile}')
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
