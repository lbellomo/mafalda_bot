import sys
import time
from pathlib import Path

import tweepy
from loguru import logger


def read_secret(path_secret="secret"):
    # TODO: change de secret format
    with open(path_secret) as f:
        secrets = [i.strip()[1:-1] for i in f.readlines()]

    CONSUMER_KEY = secrets[1]
    CONSUMER_SECRET = secrets[3]
    ACCESS_TOKEN = secrets[6]
    ACCESS_TOKEN_SECRET = secrets[8]

    return CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET


def create_api(path_secret):
    CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET = read_secret(
        path_secret
    )

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


def get_jsons(result):
    return [i._json for i in result]


def save_knows_users_ids(path_know_users_ids):
    """
    Save to a csv file 'know_users_ids'.

    path_know_users_ids: pathlib.Path
        Path to the file.
    """
    with path_know_users_ids.open("w") as f:
        for user_id in know_users_ids:
            f.write(f"{user_id}\n")


def search_knows_users_ids(path_know_users_ids):
    """
    If the file exists, read the file. Else recreate the file
    from the last favs and all the followers.

    path_know_users_ids: pathlib.Path
        Path to the file.
    """
    if path_know_users_ids.is_file():
        with path_know_users_ids.open() as f:
            know_users_ids = set(line.strip() for line in f.readlines())

    else:
        know_users_ids = set(
            result._json["user"]["id"]
            for result in tweepy.Cursor(api.favorites).items()
        )
        me = api.me()._json
        me_followers_ids = api.followers_ids(me["id"])
        know_users_ids.update(set(me_followers_ids))
        # the bot id
        know_users_ids.update(set(["1264287566284705794"]))

    return know_users_ids


def filter_result(result, know_users_ids):
    """Util to filter tweets in the search."""
    result = result._json
    if (
        "retweeted_status" in result
        or result["user"]["id_str"] in know_users_ids
        or result["favorited"]
    ):
        return False
    else:
        return True


def reduce_result(result):
    """Util to extract the useful info from the tweet."""
    result = result._json
    new_result = {}
    new_result["id"] = result["id"]
    new_result["user"] = {}
    new_result["user"]["id_str"] = result["user"]["id_str"]
    new_result["user"]["screen_name"] = result["user"]["screen_name"]

    return new_result


def get_result():
    know_users_ids = search_knows_users_ids(path_know_users_ids)
    last_favs = get_jsons(api.favorites())

    if last_favs:
        since_id = last_favs[0]["id"]
    else:
        since_id = None

    # We only a bit of information, not all the  tweet.
    search_results = [
        reduce_result(result)
        for result in tweepy.Cursor(
            api.search, q=q, since_id=since_id, count=100
        ).items()
        if filter_result(result, know_users_ids)
    ]
    return search_results


path = Path(sys.argv[0]).parent
path_know_users_ids = path / "know_users_ids.csv"

logger.add(
    path / "auto_fav.log",
    format="{time:YYYY:MM:DD HH:mm:ss} - {level} - {message}",
    rotation="5 MB",
    retention=5,
)

api = create_api(path_secret=path / "secrets")
q = "(mafalda AND quino) OR (#mafalda -#quino) OR (-#mafalda #quino)"

search_results = get_result()

logger.info(f"Find {len(search_results)} new tweets to fav")


new_favs = 0
skipped_favs = 0
new_users_ids = set()

try:

    for result in reversed(search_results):
        user_id = result["user"]["id_str"]
        if user_id in new_users_ids:
            logger.info(f"This user {user_id} have a tweet with a fav alredy, skip.")
            skipped_favs += 1
            continue

        api.create_favorite(result["id"])
        new_users_ids.update([user_id])
        logger.info(
            f"New fav: user id {user_id} screen_name {result['user']['screen_name']}, tweet_id {result['id']}"
        )
        new_favs += 1
        # tenemos mil en una ventana de 24 horas
        # aprox uno cada 90 seg
        # (60*60*24) / 1000 ~= 86.4
        time.sleep(90)

except Exception as error:
    logger.error(f"Error: {str(error)}")

know_users_ids.update(new_users_ids)
save_knows_users_ids(path_know_users_ids)
logger.info(f"Total favs: {new_favs}. Total skipped: {skipped_favs}")
