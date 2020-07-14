import sys
from pathlib import Path

import tweepy
from loguru import logger

path = Path(sys.argv[0]).parent


def read_secret():
    # TODO: change de secret format
    with open(path / "secrets") as f:
        secrets = [i.strip()[1:-1] for i in f.readlines()]

    CONSUMER_KEY = secrets[1]
    CONSUMER_SECRET = secrets[3]
    ACCESS_TOKEN = secrets[6]
    ACCESS_TOKEN_SECRET = secrets[8]

    return CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET


def create_api():
    CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET = read_secret()

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(
        auth,
        compression=True,
        retry_errors=False,
        wait_on_rate_limit=True,
        wait_on_rate_limit_notify=True,
    )
    return api


ignore_users = [
    "mafalda_bot",
    "FrasesDeMafalda",
    "Ed_delaFlor",
    "MafaldaDigital",
    "MrsMafalda31",
]
q = "mafalda AND quino exclude:nativeretweets exclude:retweets"
path_max_status_id = path / "max_status_id"

if not path_max_status_id.exists():
    max_status_id = None
else:
    max_status_id = int(path_max_status_id.read_text())

if __name__ == "__main__":

    logger.add(
        path / "auto_fav.log",
        format="{time:YYYY:MM:DD HH:mm:ss} - {level} - {message}",
        rotation="5 MB",
        retention=5,
    )

    api = create_api()

    for status in tweepy.Cursor(api.search, q=q, since_id=max_status_id).items():
        status = status._json

        if status["id"] > (max_status_id or 0):
            max_status_id = status["id"]

        if status["user"]["screen_name"] in ignore_users:
            continue

        try:
            api.create_favorite(status["id"])
        except Exception as e:
            logger.error(e)
        else:
            logger.info(f"New favorite create: {status['id']}")

    logger.info(f"New max_status_id: {max_status_id}")
    path_max_status_id.write_text(str(max_status_id))
