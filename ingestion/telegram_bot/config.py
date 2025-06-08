from dotenv import load_dotenv
import os

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
TARGET_CHANNELS = os.getenv("TARGET_CHANNELS").split(",")
SESSION_NAME = "session/airdrop_user"
