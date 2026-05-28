import os
import urllib.parse
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables in priority order
active_env = None
for env_name in ["sai.env", "yash.env", ".env"]:
    env_path = Path(__file__).resolve().parent / env_name
    if env_path.exists():
        load_dotenv(env_path, override=True)
        active_env = env_name
        break
else:
    load_dotenv()
    active_env = ".env (fallback)"

print("=" * 60)
print(f"        ALPHAForge NOTIFICATION CONNECTION TESTER")
print(f"        Active Config File Loaded: {active_env}")
print("=" * 60)

# WhatsApp settings
WA_PHONE = os.environ.get("WA_PHONE", "")
WA_APIKEY = os.environ.get("WA_APIKEY", "")

# Telegram settings
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

print(f"[WhatsApp] Phone Number: {WA_PHONE or '<NOT CONFIGURED>'}")
print(f"[WhatsApp] CallMeBot Key: {WA_APIKEY or '<NOT CONFIGURED>'}")
print(f"[Telegram] Bot Token:    {TELEGRAM_TOKEN[:10] + '...' if TELEGRAM_TOKEN else '<NOT CONFIGURED>'}")
print(f"[Telegram] Chat ID:      {TELEGRAM_CHAT_ID or '<NOT CONFIGURED>'}")
print("-" * 60)

test_msg = "🧪 *AlphaForge Test Alert*\nIf you are reading this, your AlphaForge notification connection is working perfectly!"

# 1. Test WhatsApp if configured
if WA_PHONE and WA_APIKEY:
    print("🚀 Sending WhatsApp test message...")
    try:
        encoded = urllib.parse.quote(test_msg)
        url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={encoded}&apikey={WA_APIKEY}"
        response = urllib.request.urlopen(url, timeout=10)
        if response.getcode() == 200:
            print("✅ WhatsApp Success! Check your phone.")
        else:
            print(f"❌ WhatsApp Failed! HTTP Status: {response.getcode()}")
    except Exception as e:
        print(f"❌ WhatsApp Error: {e}")
else:
    print("⚠️ WhatsApp is not configured (skipping test).")

print("-" * 60)

# 2. Test Telegram if configured
if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
    print("🚀 Sending Telegram test message...")
    try:
        encoded = urllib.parse.quote(test_msg)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={encoded}"
        response = urllib.request.urlopen(url, timeout=10)
        if response.getcode() == 200:
            print("✅ Telegram Success! Check your Telegram app.")
        else:
            print(f"❌ Telegram Failed! HTTP Status: {response.getcode()}")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
else:
    print("⚠️ Telegram is not configured (skipping test).")

print("=" * 60)
