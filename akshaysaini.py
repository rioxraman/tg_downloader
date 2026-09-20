from telethon import TelegramClient
import os
import asyncio

# =========================================
# TELEGRAM CONFIG
# =========================================

api_id = 25430351         # 2
api_hash = 'a788064d36c0b4a83b9a7963b748b4e1'
session_name = 'session_chan_extract'  # local sessio

# =========================================
# MESSAGE LINKS
# =========================================

LINK1 = "https://t.me/c/2270245564/187/902"
LINK2 = "https://t.me/c/2270245564/187/1024"

channel_id = -1002270245564

download_dir = "pw_cs26"
os.makedirs(download_dir, exist_ok=True)

# =========================================
# DOWNLOAD SETTINGS
# =========================================

CHUNK = 1024 * 1024       # 1 MB
PARALLEL = 3              # videos/files simultaneously
PARTS = 3                 # split large files into 3 parts

# Split only files ABOVE 300 MB
SPLIT_LIMIT = 300 * 1024 * 1024

client = TelegramClient(
    session_name,
    api_id,
    api_hash
)


# =========================================
# EXTRACT MESSAGE ID
# =========================================

def extract_msg_id(link):
    return int(link.rstrip("/").split("/")[-1])


start_id = extract_msg_id(LINK1)
end_id = extract_msg_id(LINK2)

if start_id > end_id:
    start_id, end_id = end_id, start_id

print(f"Downloading messages {start_id} → {end_id}")


# =========================================
# NORMAL DOWNLOAD
# =========================================

async def normal_download(msg, filepath):

    total_size = msg.file.size

    # Resume existing file
    downloaded = (
        os.path.getsize(filepath)
        if os.path.exists(filepath)
        else 0
    )

    if downloaded >= total_size:

        print(
            f"✔ Already completed: "
            f"{os.path.basename(filepath)}"
        )

        return

    print(
        f"    Starting/resuming: "
        f"{downloaded // (1024 * 1024)} MB"
    )

    with open(filepath, "ab") as f:

        async for chunk in client.iter_download(
            msg.media,
            offset=downloaded,
            chunk_size=CHUNK
        ):

            f.write(chunk)

            downloaded += len(chunk)

            percent = round(
                downloaded / total_size * 100,
                2
            )

            print(
                f"    ↳ {percent}% "
                f"({downloaded // (1024 * 1024)}MB/"
                f"{total_size // (1024 * 1024)}MB)",
                end="\r"
            )

    print(
        f"\n✔ Finished: "
        f"{os.path.basename(filepath)}"
    )


# =========================================
# DOWNLOAD ONE PART
# =========================================

async def download_part(
    msg,
    filepath,
    start,
    end,
    part_number
):

    total_part_size = end - start + 1

    # Resume this individual part
    downloaded = (
        os.path.getsize(filepath)
        if os.path.exists(filepath)
        else 0
    )

    if downloaded >= total_part_size:

        print(
            f"      ✔ Part {part_number} "
            f"already completed"
        )

        return

    current_offset = start + downloaded

    print(
        f"      Part {part_number}: "
        f"{start // (1024 * 1024)}MB → "
        f"{end // (1024 * 1024)}MB"
    )

    with open(filepath, "ab") as f:

        async for chunk in client.iter_download(
            msg.media,
            offset=current_offset,
            chunk_size=CHUNK
        ):

            remaining = (
                total_part_size - downloaded
            )

            if remaining <= 0:
                break

            if len(chunk) > remaining:
                chunk = chunk[:remaining]

            f.write(chunk)

            downloaded += len(chunk)

            percent = round(
                downloaded / total_part_size * 100,
                2
            )

            print(
                f"      Part {part_number}: "
                f"{percent}%",
                end="\r"
            )

    print(
        f"\n      ✔ Part {part_number} "
        f"finished"
    )


# =========================================
# SPLIT LARGE VIDEO INTO 3 FILES
# =========================================

async def split_video(msg, filepath):

    total_size = msg.file.size

    # Divide total file into 3 approximately
    # equal byte ranges
    part_size = total_size // PARTS

    base, ext = os.path.splitext(filepath)

    tasks = []

    for i in range(PARTS):

        start = i * part_size

        if i == PARTS - 1:
            end = total_size - 1
        else:
            end = (i + 1) * part_size - 1

        part_filename = (
            f"{base}_part{i + 1}{ext}"
        )

        task = asyncio.create_task(
            download_part(
                msg,
                part_filename,
                start,
                end,
                i + 1
            )
        )

        tasks.append(task)

    # Download all 3 parts simultaneously
    await asyncio.gather(*tasks)

    print(
        f"✔ All 3 parts completed for "
        f"{os.path.basename(filepath)}"
    )


# =========================================
# MAIN
# =========================================

async def main():

    await client.start()

    print("✔ Telegram login successful")

    print("⏳ Resolving channel...")

    channel = await client.get_entity(
        channel_id
    )

    print(
        f"✔ Channel found: "
        f"{getattr(channel, 'title', 'Unknown')}"
    )

    print(
        f"\n⏳ Scanning messages "
        f"{start_id} → {end_id}..."
    )

    msgs = []

    # =====================================
    # GET EXACT MESSAGE RANGE
    # =====================================

    async for msg in client.iter_messages(
        channel,
        min_id=start_id - 1,
        max_id=end_id + 1,
        reverse=True
    ):

        if msg.id < start_id:
            continue

        if msg.id > end_id:
            continue

        if msg.file:

            msgs.append(msg)

    total = len(msgs)

    print(
        f"📦 Files/videos found: {total}"
    )

    # =====================================
    # DOWNLOAD WORKER
    # =====================================

    sem = asyncio.Semaphore(PARALLEL)

    async def worker(index, msg):

        async with sem:

            orig = (
                msg.file.name
                or f"file_{msg.id}"
            )

            base, ext = os.path.splitext(orig)

            filename = (
                f"{index:03d}_"
                f"{base}_@rio"
                f"{ext}"
            )

            path = os.path.join(
                download_dir,
                filename
            )

            size_mb = round(
                msg.file.size /
                (1024 * 1024),
                2
            )

            print(
                f"\n[{index}/{total}] "
                f"MSG {msg.id}"
            )

            print(
                f"    File: {filename}"
            )

            print(
                f"    Size: {size_mb} MB"
            )

            # =================================
            # LARGE FILE
            # =================================

            if msg.file.size > SPLIT_LIMIT:

                print(
                    "    🔥 ABOVE 300 MB"
                )

                print(
                    "    ✂ Splitting into "
                    "3 separate parts"
                )

                await split_video(
                    msg,
                    path
                )

            # =================================
            # NORMAL FILE
            # =================================

            else:

                print(
                    "    ⬇ Normal download"
                )

                await normal_download(
                    msg,
                    path
                )

    # =====================================
    # START DOWNLOADS
    # =====================================

    tasks = [
        asyncio.create_task(
            worker(i, msg)
        )
        for i, msg in enumerate(
            msgs,
            1
        )
    ]

    await asyncio.gather(*tasks)

    print(
        "\n🎉 ALL DOWNLOADS COMPLETED!"
    )


# =========================================
# RUN
# =========================================

with client:

    client.loop.run_until_complete(
        main()
    )