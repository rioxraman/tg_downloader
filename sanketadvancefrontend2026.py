from telethon import TelegramClient
import os
import asyncio

# =========================================
# TELEGRAM CONFIG
# =========================================

api_id = 25430351         # 2
api_hash = 'a788064d36c0b4a83b9a7963b748b4e1'
session_name = 'session_chan_extract'  # local sessio
# ============================================================import os


# ============================================================
# MESSAGE LINKS
# ============================================================

LINK1 = "https://t.me/SanketSinghCoursesFree/63"
LINK1 = "https://t.me/SanketSinghCoursesFree/63"
LINK2 = "https://t.me/SanketSinghCoursesFree/701"

channel_id = "SanketSinghCoursesFree"


# ============================================================
# DOWNLOAD SETTINGS
# ============================================================

download_dir = "sanketadvancefrontend2026"

os.makedirs(
    download_dir,
    exist_ok=True
)

CHUNK = 1024 * 1024       # 1 MB
PARALLEL = 2              # simultaneous downloads

MAX_RETRIES = 1
RETRY_DELAY = 1


# ============================================================
# TELEGRAM CLIENT
# ============================================================

client = TelegramClient(
    session_name,
    api_id,
    api_hash
)


# ============================================================
# EXTRACT MESSAGE ID
# ============================================================

def extract_msg_id(link):

    if not link:

        raise ValueError(
            "LINK1 or LINK2 is empty."
        )

    return int(
        link.rstrip("/")
        .split("/")[-1]
    )


start_id = extract_msg_id(
    LINK1
)

end_id = extract_msg_id(
    LINK2
)


if start_id > end_id:

    start_id, end_id = (
        end_id,
        start_id
    )


print(
    f"Downloading messages "
    f"{start_id} → {end_id}"
)


# ============================================================
# DOWNLOAD FILE WITH TRUE RESUME
# ============================================================

async def download_file(
    msg,
    filepath
):

    total_size = msg.file.size

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # .part = incomplete download
    # final filename = completed download
    # --------------------------------------------------------

    temp_path = filepath + ".part"


    # ========================================================
    # ALREADY COMPLETED
    # ========================================================

    if os.path.exists(filepath):

        existing_size = os.path.getsize(
            filepath
        )

        if existing_size >= total_size:

            print(
                f"✔ Already completed: "
                f"{os.path.basename(filepath)}"
            )

            return True

        else:

            print(
                f"⚠ Existing final file is incomplete."
            )

            print(
                f"    Removing incomplete final file."
            )

            os.remove(filepath)


    # ========================================================
    # RETRY LOOP
    # ========================================================

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            # ------------------------------------------------
            # CHECK PARTIAL FILE
            # ------------------------------------------------

            if os.path.exists(temp_path):

                downloaded = os.path.getsize(
                    temp_path
                )

            else:

                downloaded = 0


            # ------------------------------------------------
            # PARTIAL FILE ALREADY COMPLETE
            # ------------------------------------------------

            if downloaded >= total_size:

                os.replace(
                    temp_path,
                    filepath
                )

                print(
                    f"\n✔ Completed: "
                    f"{os.path.basename(filepath)}"
                )

                return True


            # ------------------------------------------------
            # STATUS
            # ------------------------------------------------

            print(
                f"\n    Attempt "
                f"{attempt}/{MAX_RETRIES}"
            )

            print(
                f"    Resume position: "
                f"{downloaded:,} / "
                f"{total_size:,} bytes"
            )

            print(
                f"    Resume position: "
                f"{downloaded // (1024 * 1024)} MB"
            )


            # ------------------------------------------------
            # DOWNLOAD FROM EXACT OFFSET
            # ------------------------------------------------

            with open(
                temp_path,
                "ab"
            ) as f:

                async for chunk in client.iter_download(

                    msg.media,

                    offset=downloaded,

                    chunk_size=CHUNK

                ):

                    # ----------------------------------------
                    # Write chunk
                    # ----------------------------------------

                    f.write(chunk)

                    f.flush()

                    downloaded += len(chunk)


                    # ----------------------------------------
                    # Progress
                    # ----------------------------------------

                    percent = (

                        downloaded /
                        total_size *
                        100

                    )


                    print(

                        f"    {percent:6.2f}% "
                        f"("
                        f"{downloaded // (1024 * 1024)} MB/"
                        f"{total_size // (1024 * 1024)} MB"
                        f")",

                        end="\r"

                    )


            # =================================================
            # VERIFY DOWNLOAD
            # =================================================

            final_size = os.path.getsize(
                temp_path
            )


            if final_size == total_size:

                os.replace(
                    temp_path,
                    filepath
                )

                print(
                    f"\n✔ Finished: "
                    f"{os.path.basename(filepath)}"
                )

                return True


            # ------------------------------------------------
            # File size mismatch
            # ------------------------------------------------

            print(
                f"\n⚠ Download incomplete."
            )

            print(
                f"    Current: "
                f"{final_size:,} bytes"
            )

            print(
                f"    Expected: "
                f"{total_size:,} bytes"
            )


        except Exception as e:

            print(
                f"\n⚠ Download error"
            )

            print(
                f"    Attempt: "
                f"{attempt}/{MAX_RETRIES}"
            )

            print(
                f"    Error: "
                f"{type(e).__name__}: {e}"
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
    # FAILED
    # ========================================================

    print(
        f"\n❌ FAILED: "
        f"{os.path.basename(filepath)}"
    )

    print(
        f"    Partial file preserved:"
    )

    print(
        f"    {temp_path}"
    )

    return False


# ============================================================
# MAIN
# ============================================================

async def main():

    # ========================================================
    # LOGIN
    # ========================================================

    await client.start()

    print(
        "\n✔ Telegram login successful"
    )


    # ========================================================
    # RESOLVE CHANNEL
    # ========================================================

    print(
        "\n⏳ Resolving channel..."
    )

    channel = await client.get_entity(
        channel_id
    )


    print(
        f"✔ Channel found: "
        f"{getattr(channel, 'title', 'Unknown')}"
    )


    # ========================================================
    # SCAN MESSAGE RANGE
    # ========================================================

    print(
        f"\n⏳ Scanning messages "
        f"{start_id} → {end_id}..."
    )


    msgs = []


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


    # ========================================================
    # FILE COUNT
    # ========================================================

    total = len(msgs)


    print(
        f"\n📦 Files/videos found: "
        f"{total}"
    )


    if total == 0:

        print(
            "❌ No files found."
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
            # Original filename
            # ------------------------------------------------

            original_name = (

                msg.file.name

                or f"file_{msg.id}"

            )


            original_name = os.path.basename(
                original_name
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
                    f"\n❌ Unexpected error:"
                )

                print(
                    f"    {type(e).__name__}: {e}"
                )


    # ========================================================
    # CREATE TASKS
    # ========================================================

    tasks = [

        asyncio.create_task(

            worker(
                i,
                msg
            )

        )

        for i, msg in enumerate(
            msgs,
            1
        )

    ]


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
        "    Resume: ENABLED"
    )

    print(
        "    File splitting: DISABLED"
    )

    print(
        f"    Retry attempts: "
        f"{MAX_RETRIES}"
    )


    await asyncio.gather(
        *tasks
    )


    # ========================================================
    # COMPLETE
    # ========================================================

    print(
        "\n🎉 ALL DOWNLOADS COMPLETED!"
    )


    print(
        f"📁 Location: "
        f"{os.path.abspath(download_dir)}"
    )


# ============================================================
# RUN
# ============================================================

with client:

    client.loop.run_until_complete(
        main()
    )