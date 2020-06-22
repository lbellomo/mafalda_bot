# mafalda_bot

This repo has the code and the data for the bot to work. The bot runs every two hours through the cron of the [github actions](https://github.com/lbellomo/mafalda_bot/blob/master/.github/workflows/main.yml).

The data is kept obfuscated in the crypt dir (for fear of DMCA and other evils in the world). If for some reason you need to access the magic, [it's here](https://github.com/lbellomo/mafalda_bot/blob/master/main.py#L49).

The bot is very simple:
- Read from the [json](https://github.com/lbellomo/mafalda_bot/blob/master/valid_comics.json) which files are missing tweet (if there are none, add all the files from the crypt).
- Choose one at random and remove it from the list.
- Tweets the file.
- Commit to the repo by updating the json with the file list.

In utils there is a small script to make the bot a little more known.
