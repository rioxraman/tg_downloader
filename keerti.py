from telethon import TelegramClient
import os
import asyncio
import re

# -----------------------------------
api_id = 21702005         # 1
api_hash = '9e48b2f69fa40cb379fbf356bbaf7db4'
session_name = 'session_chan_extract1'  # local session file

# Public channel username OR private channel ID
channel_id = "KeertiPurswaniCoursess"

# -----------------------------------
# DOWNLOAD SETTINGS
# -----------------------------------
download_dir = "krish_naik_academy"

# Telegram message URLs
file_a = None # "https://t.me/KrishNaikAcademy/761"
file_b = None #"https://t.me/KrishNaikAcademy/971"

# Index range
index_a = None
index_b = None

# -----------------------------------
# INTERNAL SETTINGS
# -----------------------------------
CHUNK = 1024 * 1024
PARALLEL = 3

# -----------------------------------
# CREATE DOWNLOAD FOLDER
# -----------------------------------
os.makedirs(download_dir, exist_ok=True)

# -----------------------------------
# TELEGRAM CLIENT
# -----------------------------------
client = TelegramClient(session_name, api_id, api_hash)


# -----------------------------------
# EXTRACT MESSAGE ID FROM URL
# Supports:
# https://t.me/channel/123
# https://t.me/c/123456/123
# -----------------------------------
def extract_msg_id(url: str):
    match = re.search(
        r"t\.me/(?:c/\d+/|[^/]+/)(\d+)",
        url
    )

    if not match:
        raise ValueError(f"Invalid Telegram URL: {url}")

    return int(match.group(1))


# -----------------------------------
# RESUME DOWNLOAD
# -----------------------------------
async def resume_download(msg, filepath):
    total_size = msg.file.size

    downloaded = (
        os.path.getsize(filepath)
        if os.path.exists(filepath)
        else 0
    )

    # Already completed
    if downloaded >= total_size:
        print(f"✔ Already completed: {os.path.basename(filepath)}")
        return

    with open(filepath, "ab") as f:

        async for chunk in client.iter_download(
            msg.media,
            offset=downloaded,
            chunk_size=CHUNK
        ):
            f.write(chunk)

            downloaded += len(chunk)

            percent = round(
                (downloaded / total_size) * 100,
                2
            )

            print(
                f"    ↳ {percent}% completed",
                end="\r"
            )

    print(f"\n✔ Finished: {os.path.basename(filepath)}")


# -----------------------------------
# MAIN FUNCTION
# -----------------------------------
async def main():
    global index_a, index_b

    await client.start()

    msgs = []

    # -----------------------------------
    # GET RANGE
    # -----------------------------------
    if file_a and file_b:

        msg_a = extract_msg_id(file_a)
        msg_b = extract_msg_id(file_b)

        start_id = min(msg_a, msg_b)
        end_id = max(msg_a, msg_b)

        print(
            f"\n🔍 Downloading media between IDs "
            f"{start_id} → {end_id}"
        )

        async for msg in client.iter_messages(
            channel_id,
            min_id=start_id - 1,
            max_id=end_id + 1
        ):
            if start_id <= msg.id <= end_id:
                if msg.file:
                    msgs.append(msg)

    else:

        print(
            "\n🔍 No URLs provided → "
            "Downloading ALL media files"
        )

        async for msg in client.iter_messages(channel_id):

            if msg.file:
                msgs.append(msg)

    # -----------------------------------
    # SORT BY MESSAGE ID
    # -----------------------------------
    msgs.sort(key=lambda m: m.id)

    total_files = len(msgs)

    print(f"\n📦 Total media files found: {total_files}")

    # -----------------------------------
    # AUTO INDEXING
    # -----------------------------------
    if index_a is None:
        index_a = 1

    if index_b is None:
        index_b = total_files

    pad_width = 4

    # -----------------------------------
    # PARALLEL LIMITER
    # -----------------------------------
    sem = asyncio.Semaphore(PARALLEL)

    # -----------------------------------
    # WORKER
    # -----------------------------------
    async def worker(idx, msg):

        async with sem:

            padded = str(idx).zfill(pad_width)

            original_name = (
                msg.file.name
                or f"file_{msg.id}"
            )

            base, ext = os.path.splitext(original_name)

            filename = (
                f"{padded}_{msg.id}_{base}_@rio{ext}"
            )

            path = os.path.join(
                download_dir,
                filename
            )

            print(
                f"\n[{padded}] "
                f"Msg {msg.id} → {filename}"
            )

            await resume_download(msg, path)

    # -----------------------------------
    # CREATE TASKS
    # -----------------------------------
    tasks = []

    for i, msg in enumerate(msgs, start=1):

        if index_a <= i <= index_b:

            tasks.append(
                asyncio.create_task(
                    worker(i, msg)
                )
            )

    # -----------------------------------
    # START DOWNLOADS
    # -----------------------------------
    await asyncio.gather(*tasks)

    print("\n🎉 ALL DOWNLOADS COMPLETED!")


# -----------------------------------
# RUN
# -----------------------------------
with client:
    client.loop.run_until_complete(main())