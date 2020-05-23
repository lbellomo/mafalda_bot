import os
import json
from pathlib import Path
from random import choice
from codecs import decode
from base64 import b64encode, b64decode

import tweepy
import requests

p_data = Path("crypt/")
p_json = Path("valid_comics.json")

CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]

headers_api_github = {"Authorization": f"token {GITHUB_TOKEN}"}
url_api_github = (
    f"https://api.github.com/repos/{GITHUB_REPOSITORY}/contents/{p_json.name}"
)


def remove_zero_from_start(s):
    while s.startswith("0"):
        s = s[1:]
    return s


if __name__ == "__main__":

    print("Starting ...")

    with p_json.open() as f:
        valid_comics = json.load(f)

    if not valid_comics:
        valid_comics = list(p.name for p in p_data.iterdir())

    comic = choice(valid_comics)
    valid_comics.remove(comic)

    filename = comic + ".png"
    super_secret = (p_data / comic).read_text()
    im_b = b64decode(decode(super_secret, "rot-13"))
    p_im = Path(filename)
    p_im.write_bytes(im_b)

    _, volumen, pagina, parte = comic.split("-")
    if parte == "a":
        parte = "1ra"
    elif parte == "b":
        parte = "2da"

    status = f"Vol. {remove_zero_from_start(volumen)}, pag. {remove_zero_from_start(pagina)}, {parte} parte."

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)
    media = api.media_upload(filename)
    tweet = api.update_status(status=status, media_ids=[media.media_id])

    print("Tweet done!")

    old_json_data = requests.get(url_api_github).json()
    sha = old_json_data["sha"]

    message = f"Update valid_comics.json"
    content = b64encode(json.dumps(valid_comics).encode())
    json_data = {"message": message, "content": content.decode(), "sha": sha}

    print("Uploading valid_comics.json")

    r = requests.put(url_api_github, headers=headers_api_github, json=json_data)
    r.raise_for_status()

    print("All done!")
