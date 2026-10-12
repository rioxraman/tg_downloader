import os
import asyncio

from telethon import TelegramClient

# TELEGRAM CONFIG
# =========================================

api_id = 25430351         # 2
api_hash = 'a788064d36c0b4a83b9a7963b748b4e1'
session_name = 'session_chan_extract'  # local sessio

# Keep this as an INTEGER, not a string.

channel_id = -1003757020330


# ============================================================
# DOWNLOAD CONFIGURATION
# ============================================================

download_dir = "pwjrfmpaperone2025"

os.makedirs(
    download_dir,
    exist_ok=True
)

# Size of each download request
CHUNK = 1024 * 1024       # 1 MB

# Number of simultaneous downloads
PARALLEL = 2

# Retry failed downloads
MAX_RETRIES = 10

# Initial retry delay
RETRY_DELAY = 10


# ============================================================
# TELEGRAM CLIENT
# ============================================================

client = TelegramClient(
    session_name,
    api_id,
    api_hash
)


# ============================================================
# RESOLVE CHANNEL
# ============================================================

async def resolve_channel():

    print(
        "\n⏳ Looking for channel in Telegram dialogs..."
    )

    # --------------------------------------------------------
    # Search through dialogs available to this account
    # --------------------------------------------------------

    async for dialog in client.iter_dialogs():

        entity = dialog.entity

        # Only compare channels/groups with an ID
        if not hasattr(entity, "id"):
            continue

        # ----------------------------------------------------
        # Telegram channel IDs are exposed without -100
        # ----------------------------------------------------

        if entity.id == abs(channel_id):

            print(
                f"✔ Channel found: "
                f"{dialog.name}"
            )

            print(
                f"    Telegram ID: "
                f"{entity.id}"
            )

            return entity

    # --------------------------------------------------------
    # Not found
    # --------------------------------------------------------

    print(
        "\n❌ Channel was not found "
        "in your Telegram dialogs."
    )

    print(
        f"    Requested ID: {channel_id}"
    )

    print(
        "\nMake sure the Telegram account used by "
        "this session has access to the channel."
    )

    return None


# ============================================================
# CHECK DOWNLOADABLE MEDIA
# ============================================================

def is_downloadable(msg):

    # --------------------------------------------------------
    # No media
    # --------------------------------------------------------

    if not msg.media:
        return False

    # --------------------------------------------------------
    # No downloadable file
    # --------------------------------------------------------

    if msg.file is None:
        return False

    # --------------------------------------------------------
    # PHOTO
    # --------------------------------------------------------

    if msg.photo:
        return True

    # --------------------------------------------------------
    # VIDEO
    # --------------------------------------------------------

    if msg.video:
        return True

    # --------------------------------------------------------
    # AUDIO
    # --------------------------------------------------------

    if msg.audio:
        return True

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    if msg.document:

        mime_type = (
            msg.file.mime_type or ""
        ).lower()

        filename = (
            msg.file.name or ""
        ).lower()

        if mime_type == "application/pdf":
            return True

        if filename.endswith(".pdf"):
            return True

    # --------------------------------------------------------
    # Everything else
    # --------------------------------------------------------

    return False


# ============================================================
# DETERMINE FILE TYPE
# ============================================================

def get_file_type(msg):

    if msg.photo:
        return "PHOTO"

    if msg.video:
        return "VIDEO"

    if msg.audio:
        return "AUDIO"

    if msg.document:

        mime_type = (
            msg.file.mime_type or ""
        ).lower()

        filename = (
            msg.file.name or ""
        ).lower()

        if (
            mime_type == "application/pdf"
            or filename.endswith(".pdf")
        ):
            return "PDF"

    return "UNKNOWN"


# ============================================================
# GET SAFE FILENAME
# ============================================================

def get_filename(msg):

    # --------------------------------------------------------
    # Telegram-provided filename
    # --------------------------------------------------------

    original_name = (
        msg.file.name
        or ""
    )

    original_name = os.path.basename(
        original_name
    )

    # --------------------------------------------------------
    # Photo without filename
    # --------------------------------------------------------

    if not original_name:

        if msg.photo:

            original_name = (
                f"photo_{msg.id}.jpg"
            )

        elif msg.video:

            original_name = (
                f"video_{msg.id}.mp4"
            )

        elif msg.audio:

            original_name = (
                f"audio_{msg.id}.mp3"
            )

        else:

            original_name = (
                f"file_{msg.id}"
            )

    return original_name


# ============================================================
# DOWNLOAD FILE
# ============================================================

async def download_file(
    msg,
    filepath
):

    total_size = msg.file.size

    # Temporary file
    temp_path = filepath + ".part"


    # ========================================================
    # RETRY LOOP
    # ========================================================

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            # ------------------------------------------------
            # Check existing partial file
            # ------------------------------------------------

            downloaded = (

                os.path.getsize(temp_path)

                if os.path.exists(temp_path)

                else 0
            )


            # ------------------------------------------------
            # Already downloaded
            # ------------------------------------------------

            if downloaded >= total_size:

                os.replace(
                    temp_path,
                    filepath
                )

                print(
                    f"\n✔ Already completed:"
                )

                print(
                    f"    {os.path.basename(filepath)}"
                )

                return True


            # ------------------------------------------------
            # Attempt information
            # ------------------------------------------------

            print(
                f"    Attempt "
                f"{attempt}/{MAX_RETRIES}"
            )

            print(
                f"    Resume: "
                f"{downloaded // (1024 * 1024)} MB / "
                f"{total_size // (1024 * 1024)} MB"
            )


            # ------------------------------------------------
            # Open temporary file
            # ------------------------------------------------

            with open(
                temp_path,
                "ab"
            ) as f:


                # --------------------------------------------
                # Download
                # --------------------------------------------

                async for chunk in client.iter_download(

                    msg.media,

                    offset=downloaded,

                    chunk_size=CHUNK,

                    request_size=CHUNK

                ):

                    f.write(chunk)

                    downloaded += len(chunk)


                    # ----------------------------------------
                    # Progress
                    # ----------------------------------------

                    percent = round(

                        downloaded /
                        total_size *
                        100,

                        2
                    )


                    print(

                        f"    ↳ {percent}% "
                        f"("
                        f"{downloaded // (1024 * 1024)} MB/"
                        f"{total_size // (1024 * 1024)} MB"
                        f")",

                        end="\r"
                    )


            # ------------------------------------------------
            # Verify downloaded size
            # ------------------------------------------------

            if not os.path.exists(
                temp_path
            ):

                raise RuntimeError(
                    "Temporary file disappeared."
                )


            final_size = os.path.getsize(
                temp_path
            )


            # ------------------------------------------------
            # Complete
            # ------------------------------------------------

            if final_size >= total_size:

                os.replace(
                    temp_path,
                    filepath
                )

                print(
                    f"\n✔ Finished:"
                )

                print(
                    f"    {os.path.basename(filepath)}"
                )

                return True


            # ------------------------------------------------
            # Incomplete
            # ------------------------------------------------

            print(
                f"\n⚠ Incomplete download:"
            )

            print(
                f"    Current: "
                f"{final_size // (1024 * 1024)} MB"
            )

            print(
                f"    Expected: "
                f"{total_size // (1024 * 1024)} MB"
            )


        except Exception as e:

            # ------------------------------------------------
            # Error
            # ------------------------------------------------

            print(
                f"\n⚠ Download error "
                f"(attempt "
                f"{attempt}/{MAX_RETRIES})"
            )

            print(
                f"    {type(e).__name__}: {e}"
            )


        # ====================================================
        # RETRY
        # ====================================================

        if attempt < MAX_RETRIES:

            delay = min(
                RETRY_DELAY * attempt,
                60
            )

            print(
                f"    ⏳ Retrying in "
                f"{delay} seconds..."
            )

            await asyncio.sleep(
                delay
            )


    # ========================================================
    # FINAL FAILURE
    # ========================================================

    print(
        "\n❌ FAILED:"
    )

    print(
        f"    {os.path.basename(filepath)}"
    )

    return False


# ============================================================
# MAIN
# ============================================================

async def main():

    # ========================================================
    # LOGIN
    # ========================================================

    print(
        "\n⏳ Starting Telegram..."
    )

    await client.start()

    print(
        "✔ Telegram login successful"
    )


    # ========================================================
    # RESOLVE CHANNEL
    # ========================================================

    channel = await resolve_channel()

    if channel is None:

        return


    # ========================================================
    # SCAN ALL MESSAGES
    # ========================================================

    print(
        "\n⏳ Scanning ALL messages..."
    )

    msgs = []


    async for msg in client.iter_messages(

        channel,

        reverse=True

    ):

        if is_downloadable(msg):

            msgs.append(msg)


    # ========================================================
    # COUNT
    # ========================================================

    total = len(msgs)


    print(
        f"\n📦 Media/PDF files found: "
        f"{total}"
    )


    if total == 0:

        print(
            "❌ No videos, photos, audio "
            "or PDFs found."
        )

        return


    # ========================================================
    # SEMAPHORE
    # ========================================================

    sem = asyncio.Semaphore(
        PARALLEL
    )


    # ========================================================
    # WORKER
    # ========================================================

    async def worker(
        index,
        msg
    ):

        async with sem:

            # ------------------------------------------------
            # Filename
            # ------------------------------------------------

            original_name = get_filename(
                msg
            )


            # ------------------------------------------------
            # Split extension
            # ------------------------------------------------

            base, ext = os.path.splitext(
                original_name
            )


            # ------------------------------------------------
            # Final filename
            # ------------------------------------------------

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
            # Information
            # ------------------------------------------------

            file_type = get_file_type(
                msg
            )


            size_mb = round(

                msg.file.size /
                (1024 * 1024),

                2

            )


            print(
                "\n"
                "=================================================="
            )


            print(
                f"[{index}/{total}] "
                f"MSG {msg.id}"
            )


            print(
                f"    Type: {file_type}"
            )


            print(
                f"    File: {filename}"
            )


            print(
                f"    Size: {size_mb} MB"
            )


            print(
                "=================================================="
            )


            # ------------------------------------------------
            # Download
            # ------------------------------------------------

            try:

                success = await download_file(

                    msg,

                    filepath

                )


                if success:

                    print(
                        "    ✔ SUCCESS"
                    )

                else:

                    print(
                        "    ❌ FAILED"
                    )


            except Exception as e:

                print(
                    "\n❌ Unexpected error:"
                )

                print(
                    f"    {type(e).__name__}: {e}"
                )


    # ========================================================
    # CREATE TASKS
    # ========================================================

    tasks = []


    for index, msg in enumerate(

        msgs,

        1

    ):

        tasks.append(

            asyncio.create_task(

                worker(

                    index,

                    msg

                )

            )

        )


    # ========================================================
    # START DOWNLOADS
    # ========================================================

    print(
        "\n🚀 Starting downloads..."
    )


    print(
        f"    Parallel downloads: "
        f"{PARALLEL}"
    )


    print(
        f"    Retry attempts: "
        f"{MAX_RETRIES}"
    )


    print(
        f"    Download folder:"
    )


    print(
        os.path.abspath(
            download_dir
        )
    )


    await asyncio.gather(
        *tasks
    )


    # ========================================================
    # COMPLETE
    # ========================================================

    print(
        "\n"
        "=================================================="
    )


    print(
        "🎉 ALL DOWNLOAD TASKS FINISHED!"
    )


    print(
        f"📁 Location:"
    )


    print(
        os.path.abspath(
            download_dir
        )
    )


    print(
        "=================================================="
    )


# ============================================================
# RUN
# ============================================================

with client:

    client.loop.run_until_complete(
        main()
    )