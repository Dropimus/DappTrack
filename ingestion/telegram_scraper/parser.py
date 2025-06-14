import re

def is_airdrop_related(text):
    text = text.lower()
    keywords = ["airdrop", "claim", "reward", "bounty", "task", "free", "drop", "alpha", "farm", "TGE", ""]
    return any(k in text for k in keywords)
