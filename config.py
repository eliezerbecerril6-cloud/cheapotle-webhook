import os
from dotenv import load_dotenv

load_dotenv()


# =========================
# BOT SETTINGS
# =========================

BRAND = "Cheapotle Drops"

BOT_TOKEN = os.getenv(
    "BOT_TOKEN"
)


# =========================
# DISCORD SETTINGS
# =========================

GUILD_ID = int(
    os.getenv(
        "GUILD_ID",
        "0"
    )
)

OWNER_ID = int(
    os.getenv(
        "OWNER_ID",
        "0"
    )
)


SUCCESS_CHANNEL_ID = int(
    os.getenv(
        "SUCCESS_CHANNEL_ID",
        "0"
    )
)


DEPOSIT_CHANNEL_ID = int(
    os.getenv(
        "DEPOSIT_CHANNEL_ID",
        "0"
    )
)


# =========================
# PAYMENT SETTINGS
# =========================

CASHAPP = os.getenv(
    "CASHAPP",
    "Contact Staff"
)

VENMO = os.getenv(
    "VENMO",
    "Contact Staff"
)

ZELLE = os.getenv(
    "ZELLE",
    "Contact Staff"
)


# =========================
# CHIP API SETTINGS
# =========================

CHIP_API_URL = os.getenv(
    "CHIP_API_URL",
    "https://chip-api-production.up.railway.app"
)


CHIP_API_KEY = os.getenv(
    "CHIP_API_KEY",
    ""
)
    

# =========================
# ORDER SETTINGS
# =========================

CUSTOMER_PRICE_USD = 3.00


# =========================
# TEST MODE
# =========================

TEST_MODE = False


# =========================
# COMMAND SETTINGS
# =========================

SYNC_GUILD_COMMANDS = True


# =========================
# DEBUG
# =========================
CHIP_WEBHOOK_SECRET = os.getenv("CHIP_WEBHOOK_SECRET")
DEBUG = False