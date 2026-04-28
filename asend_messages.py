import asyncio
import time
from telethon import TelegramClient
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, UserDeactivatedBanError, UserDeactivatedError, UserIsBlockedError

# =========================
# Telegram API credentials
# 2
api_id = 25430351         # int
api_hash = 'a788064d36c0b4a83b9a7963b748b4e1'
session_name = 'session_chan_extract'  # local session file

# The channel or group identifier: either username ('telegram'), or invite link, or ID

# =========================
# List of usernames to message
# (without '@')
# =========================
usernames_to_message = [
# "Ne0Sr",
# "Neo271",
# "Newnamw",
# "nia_mic",
# "Nice_niv",
# "Nikeegupta",
# "nikhiltidke101",
# "nimitta_kevalam",
# "nirj876",
# "nishitravipatel",
# "nmohammad12320",
# "notwitcher",
# "NowSee3",
# "OctoSergei",
# "Omkarrrrrrrrrrrrr",
# "oolhaas",
# "Paielnan",
# "Panchm",
# "pandeypratyush",
# "Patil67",
"PE630",
"pearljoker",
"Pikachu076",
"piyushcse",
"Prabhuti_nanera",
"prajjawalshri",
"Prasad8181",
"PrasadKulkarni",
"pratik_royy",
"Pratyush_1208",
"prgore",
"Princ3raj",
"PrIncE_StArK7",
"priy_adav",
"Priya19991",
"Priyanka_Nandedkar",
"PriyankaKumari2002",
"Priyanshu_Mandloi",
"Priyaranjan_Jha",
"PriyasShe",
"Prp7723",
"PSPPal",
"ptanwar1401",
"Puru92",
"Queen_inc",
]

# =========================
# Message to send
# =========================
message_text = (
    
    '''
    🚀 new courses 
📚 Code With Harry - Data Science  
📚 Code With Harry - Python  
📚 Namaste DSA - Akshay Saini Also node and react  

🎁 More courses for buy :
Java Full Stack | MERN Stack | Python Django | LLD & HLD | Data Engineering – in Scaler at **affordable prices**  

💡 Plus these too: Maven AI Courses to master AI & ML!

    scaler new courses
------------------------
1. scaler new neovarsity course dsa advanced dsa, os, cs, bigdata, hadopp lld,hld, lld appllications , spring ,data engineering ,project management  2025
2. scaler python full stack django with lld hld in python 2025
3. java full batch  2024-25 latest
4. full stack MERN 2025
-----------------

@riotokyos
    '''
)

# =========================
# Main Function
# =========================
async def main():
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()
    print("✅ Logged in successfully!")

    sent_count = 0
    for username in usernames_to_message:
        try:
            user = await client.get_entity(username)
            await client.send_message(user, message_text)
            print(f"✅ Message sent to: @{username}")
            sent_count += 1

            # Small delay to avoid spam detection
            await asyncio.sleep(5)

        except (UserPrivacyRestrictedError, UserIsBlockedError):
            print(f"⚠️ Skipped @{username} — privacy restricted or blocked.")
        except (UserDeactivatedError, UserDeactivatedBanError):
            print(f"❌ Skipped @{username} — user account is deactivated.")
        except FloodWaitError as e:
            print(f"⏳ FloodWait: sleeping for {e.seconds} seconds...")
            time.sleep(e.seconds)
        except Exception as e:
            print(f"❌ Error with @{username}: {e}")

    print(f"\n✅ Done. Messages sent successfully to {sent_count}/{len(usernames_to_message)} users.")
    await client.disconnect()

# Run
asyncio.run(main())
