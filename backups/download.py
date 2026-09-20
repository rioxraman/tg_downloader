from telethon import TelegramClient
import os
import asyncio
import re

api_id = 25430351
api_hash = "a788064d36c0b4a83b9a7963b748b4e1"
session_name = "session_chan_extract"

channel_id = -1001967540831     # Channel ID

# -------------------------------
# USER SETTINGS
# -------------------------------
file_a = None   # example: "https://t.me/c/1967540831/697"
file_b = None   # example: "https://t.me/c/1967540831/703"

index_a = None    # start index (0001). None = auto
index_b = None   # end index. None = auto
# -------------------------------

download_dir = "scaler elite x"
os.makedirs(download_dir, exist_ok=True)

client = TelegramClient(session_name, api_id, api_hash)

CHUNK = 1024 * 1024
PARALLEL = 3


def extract_msg_id(url: str):
    match = re.search(r"/c/\d+/(\d+)$", url)
    if not match:
        raise ValueError(f"Invalid Telegram URL: {url}")
    return int(match.group(1))


async def resume_download(msg, filepath):
    total_size = msg.file.size
    downloaded = os.path.getsize(filepath) if os.path.exists(filepath) else 0

    if downloaded >= total_size:
        print(f"✔ Already completed: {os.path.basename(filepath)}")
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
    global index_a, index_b
    await client.start()

    msgs = []

    # --------------------------------------
    # 1️⃣ Determine message range
    # --------------------------------------
    if file_a and file_b:
        msg_a = extract_msg_id(file_a)
        msg_b = extract_msg_id(file_b)
        start_id = min(msg_a, msg_b)
        end_id = max(msg_a, msg_b)

        print(f"🔍 Downloading message files between IDs {start_id} → {end_id}")

        async for msg in client.iter_messages(
            channel_id, min_id=start_id - 1, max_id=end_id + 1
        ):
            if start_id <= msg.id <= end_id and msg.file:
                msgs.append(msg)
    else:
        print("🔍 No URLs provided → downloading ALL media messages in channel")

        async for msg in client.iter_messages(channel_id):
            if msg.file:
                msgs.append(msg)

    # Sort by actual Telegram message ID
    msgs.sort(key=lambda m: m.id)

    total_files = len(msgs)
    print(f"📦 Total media files found: {total_files}")

    # --------------------------------------
    # 2️⃣ Indexing (0001 → ...)
    # --------------------------------------
    if index_a is None or index_b is None:
        index_a = 1
        index_b = total_files

    pad_width = 4  # 0001 padding
    sem = asyncio.Semaphore(PARALLEL)

    # --------------------------------------
    # 3️⃣ Worker downloader
    # --------------------------------------
    async def worker(idx, msg):
        async with sem:
            padded = str(idx).zfill(pad_width)

            orig = msg.file.name or f"file_{msg.id}"
            base, ext = os.path.splitext(orig)

            filename = f"{padded}_{msg.id}_{base}_@rio{ext}"
            path = os.path.join(download_dir, filename)

            print(f"\n[{padded}] Msg {msg.id} → {filename}")
            await resume_download(msg, path)

    # Create tasks only within index_a → index_b
    tasks = []
    for i, msg in enumerate(msgs, 1):
        if index_a <= i <= index_b:
            tasks.append(asyncio.create_task(worker(i, msg)))

    await asyncio.gather(*tasks)
    print("\n🎉 ALL DOWNLOADS COMPLETED!")


with client:
    client.loop.run_until_complete(main())
