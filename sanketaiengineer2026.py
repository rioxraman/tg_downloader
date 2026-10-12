from telethon import TelegramClient
import os
import asyncio
from telethon.tl.types import MessageMediaWebPage
# =========================================
# TELEGRAM CONFIG
# =========================================

api_id = 25430351         # 2
api_hash = 'a788064d36c0b4a83b9a7963b748b4e1'
session_name = 'session_chan_extract'  # local sessio

# =========================================
# MESSAGE LINKS
channel_id = "@SanketAiEngineer"


# ============================================================
# DOWNLOAD SETTINGS
# ============================================================

download_dir = "sanketaiengineerbootcamp2026"
os.makedirs(download_dir, exist_ok=True)

CHUNK = 1024 * 1024       # 1 MB
PARALLEL = 3              # simultaneous downloads


# ============================================================
# TELEGRAM CLIENT
# ============================================================

client = TelegramClient(
    session_name,
    api_id,
    api_hash
)


# ============================================================
# DOWNLOAD FILE
# ============================================================

async def download_file(msg, filepath):

    total_size = msg.file.size

    # --------------------------------------------------------
    # Check existing file
    # --------------------------------------------------------

    downloaded = (
        os.path.getsize(filepath)
        if os.path.exists(filepath)
        else 0
    )

    # --------------------------------------------------------
    # Already completed
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Download / Resume
    # --------------------------------------------------------

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
                f"({downloaded // (1024 * 1024)} MB/"
                f"{total_size // (1024 * 1024)} MB)",
                end="\r"
            )

    print(
        f"\n✔ Finished: "
        f"{os.path.basename(filepath)}"
    )


# ============================================================
# CHECK WHETHER MESSAGE HAS REAL DOWNLOADABLE MEDIA
# ============================================================

def is_downloadable(msg):

    # No media
    if not msg.media:
        return False

    # Web-page preview
    if isinstance(
        msg.media,
        MessageMediaWebPage
    ):
        return False

    # Must have a Telethon file
    if not msg.file:
        return False

    return True


# ============================================================
# MAIN
# ============================================================

async def main():

    # --------------------------------------------------------
    # Login
    # --------------------------------------------------------

    await client.start()

    print(
        "\n✔ Telegram login successful"
    )

    # --------------------------------------------------------
    # Resolve channel
    # --------------------------------------------------------

    print(
        "⏳ Resolving channel..."
    )

    channel = await client.get_entity(
        channel_id
    )

    print(
        f"✔ Channel found: "
        f"{getattr(channel, 'title', 'Unknown')}"
    )

    # --------------------------------------------------------
    # Scan ALL messages
    # --------------------------------------------------------

    print(
        "\n⏳ Scanning ALL messages "
        "in the channel..."
    )

    msgs = []

    async for msg in client.iter_messages(
        channel,
        reverse=True
    ):

        if is_downloadable(msg):
            msgs.append(msg)

    total = len(msgs)

    print(
        f"\n📦 Downloadable files found: "
        f"{total}"
    )

    if total == 0:

        print(
            "❌ No downloadable files found."
        )

        return

    # --------------------------------------------------------
    # Semaphore
    # --------------------------------------------------------

    sem = asyncio.Semaphore(
        PARALLEL
    )

    # ========================================================
    # WORKER
    # ========================================================

    async def worker(index, msg):

        async with sem:

            # ------------------------------------------------
            # Original filename
            # ------------------------------------------------

            original_name = (
                msg.file.name
                or f"file_{msg.id}"
            )

            # ------------------------------------------------
            # Filename
            # ------------------------------------------------

            base, ext = os.path.splitext(
                original_name
            )

            filename = (
                f"{index:03d}_"
                f"{base}_@rio"
                f"{ext}"
            )

            filepath = os.path.join(
                download_dir,
                filename
            )

            # ------------------------------------------------
            # File size
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Download
            # ------------------------------------------------

            try:

                await download_file(
                    msg,
                    filepath
                )

            except Exception as e:

                print(
                    f"\n❌ Failed: "
                    f"{filename}"
                )

                print(
                    f"    Error: {e}"
                )

    # ========================================================
    # CREATE DOWNLOAD TASKS
    # ========================================================

    tasks = [
        asyncio.create_task(
            worker(index, msg)
        )
        for index, msg in enumerate(
            msgs,
            1
        )
    ]

    # ========================================================
    # DOWNLOAD
    # ========================================================

    await asyncio.gather(
        *tasks
    )

    # ========================================================
    # COMPLETE
    # ========================================================

    print(
        "\n🎉 ALL DOWNLOADS COMPLETED!"
    )


# ============================================================
# RUN
# ============================================================

with client:

    client.loop.run_until_complete(
        main()
    )