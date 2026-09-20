import csv
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import UserStatusOffline, UserStatusOnline, UserStatusRecently, UserStatusLastWeek, UserStatusLastMonth

# Replace with your credentials from https://my.telegram.org
# Replace these with your values from my.telegram.org
api_id = 21701200225         # int
api_hash = '9e48b222f6923236bbaf7db4'
session_name = 'session_chan_extract1'  # local session file

# The channel or group identifier: either username ('telegram'), or invite link, or ID
target = 'Shortdramafull'  # e.g. 'python' or '-1001234567890'

client = TelegramClient(session_name, api_id, api_hash)


def get_last_seen(status):
    """Convert Telegram UserStatus object into readable last seen info"""
    if isinstance(status, UserStatusOnline):
        return "Online now"
    elif isinstance(status, UserStatusOffline):
        return status.was_online.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(status, UserStatusRecently):
        return "Recently"
    elif isinstance(status, UserStatusLastWeek):
        return "Last week"
    elif isinstance(status, UserStatusLastMonth):
        return "Last month"
    else:
        return "Hidden or long ago"


async def main():
    await client.start()
    outfile = 'tele_usernames_shortrel.csv'
    with open(outfile, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['user_id', 'username', 'first_name', 'last_name', 'phone', 'last_seen'])

        async for user in client.iter_participants(target):
            last_seen = get_last_seen(user.status)
            writer.writerow([
                user.id,
                user.username or '',
                user.first_name or '',
                user.last_name or '',
                getattr(user, 'phone', '') or '',
                last_seen
            ])

    print(f"✅ Done — saved to {outfile}")
    await client.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
