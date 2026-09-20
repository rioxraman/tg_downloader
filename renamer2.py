from telethon import TelegramClient
import os

# --------------------------------
# CONFIG
api_id = 25430351         # 2
api_hash = 'a788064d36c0b4a83b9a7963b748b4e1'
session_name = 'session_chan_extract'  # local session file

channel_id = -1003499582602
# python algo - 2678359218
#pavement - 2447998854
#   verbal - 2677470120
# dbms - 2445949931
# Local folder where WRONG files already exist
folder = r"D:\Anuj Spring Prime Cohort"
# --------------------------------

os.makedirs(folder, exist_ok=True)

client = TelegramClient(session_name, api_id, api_hash)


async def main():
    print("Fetching metadata from Telegram channel...")

    # Dictionary: size → list of {index, orig, ext}
    metadata = {}

    # Get channel entity
    entity = await client.get_entity(channel_id)

    # Scan messages
    async for msg in client.iter_messages(entity):
        # Accept only messages that contain a downloadable file
        if not msg.media:
            continue
        if not msg.file:          # FIXED — prevent crashes
            continue
        if not msg.file.size:     # Some messages have file=None/size=None
            continue

        index = msg.id
        size = msg.file.size

        # Fetch Telegram filename (or fallback)
        orig_name = msg.file.name or f"file_{index}"
        ext = os.path.splitext(orig_name)[1]

        if not ext:
            ext = ".bin"

        # Add to metadata list under size
        metadata.setdefault(size, [])
        metadata[size].append({
            "index": index,
            "orig": orig_name,
            "ext": ext
        })

    print(f"Metadata collected for {len(metadata)} unique file sizes.")
    print("\nStarting renaming...\n")

    used = {}  # To track duplicates of same size

    # Process local folder files
    for wrong_filename in os.listdir(folder):
        path = os.path.join(folder, wrong_filename)

        if not os.path.isfile(path):
            continue

        size = os.path.getsize(path)

        if size not in metadata:
            print(f"SKIP (size not found in Telegram metadata): {wrong_filename}")
            continue

        taken = used.get(size, 0)
        file_list = metadata[size]

        if taken >= len(file_list):
            print(f"SKIP (more local files than Telegram files for this size): {wrong_filename}")
            continue

        tg_file = file_list[taken]
        used[size] = taken + 1

        index = tg_file["index"]
        orig_name = tg_file["orig"]

        # Final new filename
        new_name = f"{index}_{orig_name}"
        new_path = os.path.join(folder, new_name)

        # Avoid collision by adding suffixes
        counter = 1
        base, ext = os.path.splitext(new_name)
        while os.path.exists(new_path):
            new_name = f"{base}_{counter}{ext}"
            new_path = os.path.join(folder, new_name)
            counter += 1

        os.rename(path, new_path)
        print(f"Renamed → {wrong_filename}  -->  {new_name}")

    print("\nDONE ✔ All possible files were renamed.")


with client:
    client.loop.run_until_complete(main())
