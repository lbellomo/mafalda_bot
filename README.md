# Mafalda_bot 🤖

Check out the bot on twitter: [@mafalda_bot 🤖](https://twitter.com/mafalda_bot)

This repo has the code and the data for a bot that tweets a [Mafalda](https://en.wikipedia.org/wiki/Mafalda) comic from [Quino](https://en.wikipedia.org/wiki/Quino) every couple of hours.

The bot runs (every two hours) through the cron of the [github actions](https://github.com/lbellomo/mafalda_bot/blob/master/.github/workflows/main.yml). It turns out that github actions is a simple way to run the code without worrying about the infrastructure (with a very high uptime for the effort, except when the github or twitter APIs are down)

The data is kept obfuscated in the crypt dir (for fear of DMCA and other evils in the world). If for some reason you need to access the magic, [it's here](https://github.com/lbellomo/mafalda_bot/blob/master/main.py#L49).

The bot is very simple:
- Read from the [json](https://github.com/lbellomo/mafalda_bot/blob/master/valid_comics.json) which files are missing tweet (if there are none, add all the files from the crypt).
- Choose one at random and remove it from the list.
- Tweets the file.
- Commit to the repo by updating the json with the file list.

## Auto_fav

An attempt was made to publicize the bot with various methods (from telling friends to paying for advertising) but the result was terrible, less than 20 followers. To solve this, there is the auto_fav.py that looks for tweets about Mafalda in the last week and faves them in the hope that the user will see the bot and be of interest.
