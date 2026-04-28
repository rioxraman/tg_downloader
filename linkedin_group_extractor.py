import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

# --- CONFIG ---
GROUP_URL = "https://www.linkedin.com/groups/25827/"
OUTPUT_FILE = "linkedin_group_members.csv"
SCROLL_PAUSE_TIME = 2

# --- Setup Chrome driver ---
chrome_options = Options()
chrome_options.add_argument("--headless")  # remove this if you want to watch browser actions
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")

service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

print(f"🌐 Opening LinkedIn group: {GROUP_URL}")
driver.get(GROUP_URL)
time.sleep(5)

# --- Scroll to load members ---
print("🔄 Scrolling to load all visible members...")
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

print("✅ Page fully loaded.")

# --- Extract member cards ---
print("🕵️ Extracting member info...")

members = []
cards = driver.find_elements(By.XPATH, "//a[contains(@href, '/in/')]")

for card in cards:
    try:
        profile_link = card.get_attribute("href").split("?")[0]
        name = card.text.strip()

        # Try to find nearby headline/bio text
        parent = card.find_element(By.XPATH, "./ancestor::div[1]")
        text_blocks = [t.strip() for t in parent.text.split("\n") if len(t.strip()) > 2]
        headline = ""
        if len(text_blocks) > 1:
            for t in text_blocks:
                if t != name and len(t.split()) > 2 and len(t) < 120:
                    headline = t
                    break

        members.append({
            "name": name,
            "headline": headline,
            "profile_link": profile_link
        })
    except Exception as e:
        continue

print(f"✅ Extracted {len(members)} profiles")

# --- Save results ---
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "headline", "profile_link"])
    writer.writeheader()
    writer.writerows(members)

print(f"💾 Saved data to: {OUTPUT_FILE}")

driver.quit()
print("🏁 Done.")
