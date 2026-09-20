import csv
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import UserStatusOffline, UserStatusOnline, UserStatusRecently, UserStatusLastWeek, UserStatusLastMonth

api_id = 21702005         # 1
api_hash = '9e48b2f69fa40cb379fbf356bbaf7db4'
session_name = 'session_chan_extract1'  # local session file

file = 'proshiplinks.csv'
# file = 'sample_me.csv'
# file = 'sample_ee.csv'
# file = 'sample_ece.csv'
# file = 'sample_civil.csv'
# The channel or group identifier: either username ('telegram'), or invite link, or ID
target =   "proshiplinks"
# target = -1003003611859 #me
# target = -1003062717362 #ee
# target = -1003016570681 #ece
# target = -1002936869538 #civil

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
    outfile = file
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
