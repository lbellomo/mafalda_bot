import os
import sys
import time
from pathlib import Path
from random import choice
from codecs import decode
from base64 import b64decode

import tweepy

p_data = Path("crypt/")

max_errors_count = 5

CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]


def remove_zero_from_start(s):
    while s.startswith("0"):
        s = s[1:]
    return s


if __name__ == "__main__":

    print("Starting ...")

    valid_comics = list(p.name for p in p_data.iterdir())

    comic = choice(valid_comics)

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

    status = f"Vol. {remove_zero_from_start(volumen)}, pag. {remove_zero_from_start(pagina)}, {parte} parte. #Mafalda #Quino"

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)
    media = api.media_upload(filename)

    errors_count = 0

    while True:
        try:
            tweet = api.update_status(status=status, media_ids=[media.media_id])
        except Exception as e:
            print(f"Error found: {e}")
            errors_count += 1
            if errors_count == max_errors_count:
                print("Max number of errors reached with twitter API!")
                sys.exit(1)

            time.sleep(errors_count + 1)
        else:
            break

    print("Tweet done!")
