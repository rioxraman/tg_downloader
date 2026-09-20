
from telethon import TelegramClient
import os
import asyncio

api_id = 25430351         # 2
api_hash = 'a788064d36c0b4a83b9a7963b748b4e1'
session_name = 'session_chan_extract'  # local session file
channel_id = -1003810850200  # your private channel

# 2755841354
download_dir = "namaste dsa"
os.makedirs(download_dir, exist_ok=True)

client = TelegramClient(session_name, api_id, api_hash)

CHUNK = 1024 * 1024   # 1 MB
PARALLEL = 3          # parallel downloads


async def resume_download(msg, filepath):
    total_size = msg.file.size
    downloaded = os.path.getsize(filepath) if os.path.exists(filepath) else 0

    if downloaded >= total_size:
        print(f"✔ Completed earlier: {os.path.basename(filepath)}")
        return

    f = open(filepath, "ab")

    async for chunk in client.iter_download(
        msg.media, offset=downloaded, chunk_size=CHUNK
    ):
        f.write(chunk)
        downloaded += len(chunk)

        percent = round((downloaded / total_size) * 100, 2)
        print(f"    ↳ {percent}% completed", end="\r")

    f.close()
    print(f"\n✔ Finished: {os.path.basename(filepath)}")


async def main():
    await client.start()

    print("⏳ Scanning messages…")

    msgs = []

    # ⭐ NO TOPIC FILTER — downloads the whole channel
    async for msg in client.iter_messages(channel_id):
        if msg.file:
            msgs.append(msg)

    msgs.reverse()  # oldest first

    total = len(msgs)
    print(f"📦 Total files found: {total}")

    sem = asyncio.Semaphore(PARALLEL)

    async def worker(i, msg):
        async with sem:
            orig = msg.file.name or f"file_{msg.id}"
            base, ext = os.path.splitext(orig)
            filename = f"{i:03d}_{base}_@ben{ext}"
            path = os.path.join(download_dir, filename)

            print(f"\n[{i}/{total}] Downloading {filename}")
            await resume_download(msg, path)

    tasks = [asyncio.create_task(worker(i, msg)) for i, msg in enumerate(msgs, 1)]
    await asyncio.gather(*tasks)

    print("\n🎉 ALL DOWNLOADS COMPLETED!")


with client:
    client.loop.run_until_complete(main())
