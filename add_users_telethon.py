# add_users_telethon.py
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import UserPrivacyRestrictedError, FloodWaitError

# =========================
# Telegram API credentials
api_id = 21702005         # int
api_hash = '9e48b2f69fa40cb379fbf356bbaf7db4'
session_name = 'session_chan_extract1'  # local session file

# =========================
# Group username to add users into
# (use '@groupusername' without quotes)
# =========================
group_username = "MavenAgenticAI"

# =========================
# List of usernames to add
# (without '@', just the username)
# =========================
usernames_to_add = [
  "Aabcghp",
  "aadarshyati",
  "aadeezz",
  "Aadhi010",
  "aadi0213",
  "aadi0453",
  "aadi327",
  "aaditi_20",
  "aakash_chavla",
  "Aakash244246",
  "Aakashborse1999",
  "aakashhhh162",
  "aakashraj416",
  "aakashsaini755",
  "AakashSivakumar",
  "aakrati_jadoun",
  "aala_motha",
  "aaltamas",
  "aalukachalu",
  "aanalpatil24",
  "aankitmauryaa",
  "Aaquib3857",
  "Aaravtac",
  "Aarifahamed",
  "Aark0001",
  "Aarna_27",
  "Aarti_1904",
  "aarti_jethaniya",
  "Aaryan2208",
  "Aaryendra",
  "aashit1608",
  "aastha01",
  "aastikmehta",
  "aatarsh02",
  "aayanlobo",
  "aayush1815",
  "Aayush6745",
  "Aayushi9922",
  "Aazad_voice",
  "aazeem_5",
  "ab_bhalla",
  "Ab2068",
  "Abbas_kapasi",
  "Abbhishek",
  "abc_077",
  "abc_123_456_789",
  "abc21080",
  "Abcd2xyz",
  "Abcd8211",
  "Abcde_111",
  "ABCDEF000111",
  "Abcdefg35kkl",
  "Abcdefghi123456a",
  "abcdss_1234",
  "abcdusru79",
  "Abcjklog",
  "abcxyz8887",
  "abdul_rahmaan_ar",
  "abdul_sameer786",
  "abdullah09362",
  "abh1760",
  "Abha9336",
  "Abhay0313_ji",
  "Abhay2k",
  "Abhay78613",
  "Abhaybagla04",
  "AbHaYpRaTaP007",
  "Abhaythakur_123",
  "Abhi_120799",
  "Abhi_891",
  "abhi_9_kumar",
  "Abhi_904",
  "Abhi_lekh",
  "abhi_nitmn",
  "Abhi12345Kr",
  "abhi15_NIT",
  "Abhi235789",
  "Abhi77901",
  "abhi786raj",
  "Abhi9565",
  "Abhiii_Eagle",
  "Abhiii1947",
  "abhiii234",
  "abhiiiijain",
  "AbhiiNani",
  "Abhiishek_bhardwaj",
  "abhijeet0712",
  "abhijeet098",
  "AbhikIsNoMore",
  "Abhilashmylapalli",
  "abhileshgupta",
  "AbhiM27",
  "abhinandanraj1",
  "Abhinav0503",
  "ABHINAV19",
  "Abhinav2529",
  "AbhinavNarang",
  "Abhinavtiwari23",
  "abhinskrishna",
  "Abhirocks783",
  "abhis079",
  "abhishek_2028",
  "Abhishek_987612",
  "Abhishek_shelke2",
  "abhishek002kvs",
  "abhishek005",
  "Abhishek2718",
  "abhishek767812",
  "Abhishekchoudhary134",
  "abhishekdwibedy",
  "Abhishekmalviyaa",
  "abhithakur3606",
  "abhityagi012",
  "abhrajitdas",
  "Abhyaishere",
  "Abi_Shk21",
  "abimbola0x",
  "Abinash_004_CSE_OA9",
  "Abinash1803",
  "Abkvfjj",
  "Abr1102019",
  "Abrarzx5501",
  "abserve247",
  "abulah04",
  "ac29291",
  "ac7000",
  "ACAcheiver",
  "acadaniket",
  "Accountdoesnotexistdeleted",
  "prashantrss"
];


# =========================
# Main function
# =========================
async def main():
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()
    
    # Resolve the group entity
    try:
        group_entity = await client.get_entity(group_username)
    except Exception as e:
        print(f"❌ Cannot find group: {e}")
        return

    # Resolve user entities
    users = []
    for username in usernames_to_add:
        try:
            user = await client.get_entity(username)
            users.append(user)
        except Exception as e:
            print(f"⚠️ Cannot find user '{username}': {e}")

    # Add users in batches of 10 (Telegram limits)
    batch_size = 10
    for i in range(0, len(users), batch_size):
        batch = users[i:i+batch_size]
        try:
            await client(InviteToChannelRequest(
                channel=group_entity,
                users=batch
            ))
            print(f"✅ Added batch {i // batch_size + 1}: {[u.username for u in batch]}")
        except UserPrivacyRestrictedError as e:
            print(f"⚠️ Some users have privacy restrictions, skipped batch {i // batch_size + 1}")
        except FloodWaitError as e:
            print(f"⏳ FloodWait: sleeping {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"❌ Error adding batch {i // batch_size + 1}: {e}")

    await client.disconnect()
    print("✅ Finished adding users.")

# Run
asyncio.run(main())
