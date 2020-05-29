# discord-pontoon-bot

Simple discord bot created in Python using [discord.py](https://github.com/Rapptz/discord.py)

[Invite](https://discord.com/oauth2/authorize?client_id=690113537032585236&scope=bot&permissions=0) it to your discord channel!


## Pontoon?

[Pontoon](https://en.wikipedia.org/wiki/Pontoon_(card_game)) is a card game similar to Blackjack.
I based my code on the rules of Pontoon found [here](https://www.cra.gov.sg/docs/default-source/game-rule-documents/rws/rws-game-rules---pontoon-v3.pdf).


## Prerequisites

-python3

-[discord.py](https://github.com/Rapptz/discord.py)


## Installation

[discord.py](https://github.com/Rapptz/discord.py) can be installed through ```pip```.

```pip install discord.py```


Using the command line, ```cd``` to your favourite directory.

```
git clone https://github.com/duplicitous-dungbeetle/discord-pontoon-bot.git
cd discord-pontoon-bot

```
Add your own discord bot's token into line 11 in pontoon.py
(Find out how to create your own discord bot [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token))

Then run the script.

```
python3 pontoon.py
```

## Others

You can also host it on [Heroku](http://www.heroku.com), [Repl.it](https://repl.it/), or other platforms.

To host it on Heroku:
Create a [Heroku](http://www.heroku.com) account and create a new app
Download the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

Then run these commands:

Step 1: The Files
```
git clone https://github.com/duplicitous-dungbeetle/discord-pontoon-bot.git
cd discord-pontoon-bot
echo worker: python pontoon.py > Procfile
pip freeze > requirements.txt
```
Step 2a: Heroku login
```
heroku login -i
```
Then type in your username and password

Step 2b: Heroku
```
heroku git:remote -a your_heroku_app_name_here
git init
git add .
git commit -am "my first commit!! i can type anything here!!"
git push heroku master
```
Step 3:

Go to your app's page on your Heroku account, go to the Resources tab, and turn on the worker dyno.



## Comments

Am new to programming, if you have any suggestions/feedback/ideas for me to improve please share it with me.

If there are bugs, please tell inform me too.


