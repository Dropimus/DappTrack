from os import getenv
from json import dump
from asyncio import run, sleep
from twscrape import API, logger
from twscrape.logger import set_log_level
from re import sub, MULTILINE
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv
from traceback import print_exc
import csv
from transformers import pipeline

# Set logging level for twscrape (optional, useful for debugging)
set_log_level("INFO")  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
    logger.info(f"Loaded .env from: {dotenv_path}")
else:
    logger.warning(
        "Could not find .env file. Please create one with your credentials: TWITTER_USERNAME, PASSWORD, EMAIL, COOKIES"
    )
# Ensure you have a .env file with the following variables set:
# USERNAME, PASSWORD, EMAIL, COOKIES
# If you don't have a .env file, create one with the following content:
# TWITTER_USERNAME=your_username
# PASSWORD=your_password
# EMAIL=your_email
# COOKIES=your_cookies
# If you have cookies, you can set them as a string in the .env file.
# If you don't have cookies, get the cookies from your browser when logged into the account.
USERNAME = getenv("TWITTER_USERNAME")
PASSWORD = getenv("PASSWORD")
EMAIL = getenv("EMAIL")
COOKIES = getenv("COOKIES")

# Keywords for airdrop detection (make this list comprehensive)
AIRDROP_KEYWORDS = [
    "airdrop",
    "claim",
    "free crypto",
    "token distribution",
    "whitelist",
    "snapshot",
    "mint",
    "early access",
    "DAO vote",
    "governance token",
    "retroactive",
    "rewards program",
    "form",
    "eligibility",
    "official announcement",
    "join now",
    "testnet rewards",
    "mainnet launch",
    "tokenomics",
    "community rewards",
    "public sale",
    "IDO",
    "fair launch",
]

# Negative/scam keywords (to filter out, expand this list!)
SCAM_KEYWORDS = [
    "send eth to",
    "dm me",
    "private sale",
    "guaranteed returns",
    "investment opportunity",
    "pump and dump",
    "only x left",
    "urgent",
    "wallet connect",
    "gas fee",
    "transaction fee",  # "gas fee" can be legitimate, but often used in scams.
]

# Max posts to check per followed account
MAX_POSTS_PER_ACCOUNT = 5


# --- Helper Functions for Tweet Analysis ---
def clean_tweet(text):
    # Remove URLS
    # text = sub(r"http\S+|www\S+|https\S+", "", text, flags=MULTILINE)
    text = sub(r"@\w+", "", text)
    # Keeping hashtags for now as they can be relevant, but you could remove them.
    # text = re.sub(r'#\w+', '', text)
    text = sub(r'[^a-zA-Z0-9\s.,!?\'"-]', "", text)  # Keep basic punctuation
    text = text.lower()
    text = sub(r"\s+", " ", text).strip()
    return text


def analyze_tweet(tweet_text):
    """
    Analyzes a tweet using Hugging Face's zero-shot classification pipeline.
    """
    cleaned_text = clean_tweet(tweet_text)
    # Load the zero-shot classification pipeline
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    # Define candidate labels
    candidate_labels = ["airdrop announcement", "not airdrop announcement"]

    # Classify the tweet
    result = classifier(cleaned_text, candidate_labels)

    # Extract the label and confidence score
    predicted_label = result["labels"][0]
    confidence_score = result["scores"][0]

    return predicted_label, confidence_score


async def setup_twscraper(setup: bool, api: API):
    if setup:
        await api.pool.add_account(
            USERNAME,
            PASSWORD,
            EMAIL,
            "12345678",
            cookies=COOKIES,
        )
    await api.pool.login_all()


# --- Main Scraper Logic ---
async def get_and_check_tweets(api):
    await setup_twscraper(False, api)

    # Find the user ID of the monitoring account
    monitor_user = await api.user_by_login(USERNAME)
    if not monitor_user:
        logger.error(
            f"Account '{USERNAME}' not found or could not be logged in. Please check your DB and credentials."
        )
        return

    monitor_user_id = monitor_user.id
    logger.info(f"Monitoring following of user: @{USERNAME} (ID: {monitor_user_id})")

    # 1. Get the list of accounts the monitor_user is following
    followed_accounts = []
    logger.info("Fetching followed accounts...")
    # Use twscrape's `followers` or `following` methods.
    # It might require iterating if the user follows many accounts.
    # The `following` method usually fetches who a user *follows*.
    # Iterating through `api.following()` will yield `User` objects.
    async for user in api.following(monitor_user_id):
        followed_accounts.append(
            {
                "id": user.id,
                "username": user.username,
                "followers_count": user.followersCount,
            }
        )
        logger.debug(f"Found followed account: @{user.username}")
        # Add a delay to avoid hammering X's servers, even with twscrape
        await sleep(0.5)  # Small delay

    logger.info(
        f"Found {len(followed_accounts)} accounts that @{USERNAME} is following."
    )

    # 2. For each followed account, get their top N recent posts and check for airdrops
    analyzed_tweets = []
    checked_count = 0

    for i, account in enumerate(followed_accounts[:19]):
        checked_count += 1
        logger.info(
            f"({checked_count}/{len(followed_accounts[:19])}) Checking posts for @{account['username']}..."
        )
        try:
            # Use api.user_tweets() to get tweets from a specific user.
            # It yields Tweet objects.
            tweet_count = 0
            async for tweet in api.user_tweets(
                account["id"], limit=MAX_POSTS_PER_ACCOUNT
            ):
                tweet_count += 1
                # tweet_text = (
                #     tweet.full_text if hasattr(tweet, "full_text") else tweet.text
                # )  # Ensure full text
                tweet_text = tweet.rawContent
                tweet_url = (
                    f"https://twitter.com/{account['username']}/status/{tweet.id}"
                )
                # logger.info(f"Tweet from @{account['username']}:\n{tweet_text}")
                predicted_label, confidence_score = analyze_tweet(tweet_text)

                if predicted_label == "airdrop announcement":
                    logger.warning(
                        f"  --> POTENTIAL AIRDROP DETECTED from @{account['username']}: {tweet_url}"
                    )
                else:
                    logger.debug(
                        f"  - No airdrop detected in tweet {tweet.id} from @{account['username']}: predicted label: {predicted_label} with score: {confidence_score}"
                    )
                analyzed_tweets.append(
                    {
                        "account_username": account["username"],
                        "tweet_text": tweet_text,
                        "predicted_label": predicted_label,
                        "confidence_score": confidence_score,
                        "tweet_url": tweet_url,
                        "tweet_id": tweet.id,
                        "created_at": tweet.date,
                    }
                )

                await sleep(2)  # Small delay between tweets from same user

        except Exception as e:
            logger.error(f"Error checking tweets for @{account['username']}: {e}")
            print_exc()

        # Add a more substantial delay between checking different accounts
        await sleep(10)  # Delay for 10 seconds between accounts

    logger.info(f"\n--- Airdrop Scan Complete ---")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analyzed_tweets_{timestamp}.json"

    # IMPORTANT: Convert datetime objects to string for JSON serialization
    # JSON can't directly serialize datetime objects.
    serializable_airdrops = []
    for ad in analyzed_tweets:
        ad_copy = ad.copy()  # Create a copy to avoid modifying the original list item
        if isinstance(ad_copy["created_at"], datetime):
            ad_copy["created_at"] = ad_copy[
                "created_at"
            ].isoformat()  # ISO 8601 format for dates
        serializable_airdrops.append(ad_copy)

    try:
        with open(filename, "w", encoding="utf-8") as f:
            dump(serializable_airdrops, f, indent=4, ensure_ascii=False)
        logger.info(f"Successfully saved {len(analyzed_tweets)} airdrops to {filename}")
    except IOError as e:
        logger.error(f"Error saving airdrops to JSON file {filename}: {e}")

    # Save tweets to CSV
    csv_filename = f"tweets_{timestamp}.csv"
    try:
        with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Text", "Label"])  # Write header
            for tweet in analyzed_tweets:
                writer.writerow([tweet["tweet_text"], 0])
        logger.info(f"Successfully saved tweets to {csv_filename}")
    except IOError as e:
        logger.error(f"Error saving tweets to CSV file {csv_filename}: {e}")


if __name__ == "__main__":
    run(get_and_check_tweets(API()))
