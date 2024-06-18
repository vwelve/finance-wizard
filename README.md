# gpt-discord-bot

This bot gives financial analysis recommendations based on the stock market using information from yahoo finance. You can find the system message used in the [system-message.txt](https://github.com/vwelve/gpt-discord-bot/blob/dev/system-message.txt) file and you can change the content there to what provides better results.

## Requirements

* Python@3.7.1<=
* NPM (Node.JS)
* Miniconda (Optional but recommended)

## Cloning Repository

```
git clone https://github.com/vwelve/gpt-discord-bot.git
cd gpt-discord-bot
```

## Setup Environment

For this bot to work as intended you will have to create bot applications for two platforms: OpenAI and Discord. For OpenAI you will have to export your API key to your system's Environment Variables. You can find more information on how to do that on their [official documentation](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key).

The env file will store the Discord Token you need to run the bot, and should look like this:

```
# .env File
DISCORD_TOKEN = # ENTER YOUR DISCORD BOT TOKEN FROM https://discord.com/developers/applications HERE
```

### Setup Conda Environment (Optional)

Setting up a virtual environment will help keep everything consistent. In this example I use python@3.12, however, Any version python@3.7.1<= will work as well.

```
conda create -n gpt-discord-bot python=3.12
conda activate gpt-discord-bot
```

### Download Dependencies

```
python -m pip install -r requirements.txt
npm install -g pm2 # Only required if you intend on using pm2 to run your script
```

## Starting the bot

Once all the setup is completed the rest is quite simple you just need to run the bot, and setting up the bot with a daemon depending on your intentions.

```
python main.py
```
### Running with daemon (PM2)

```
which python # gives the path of the python you're using
pm2 start main.py --name "gpt-discord-bot" --interpreter=PYTHON_INTERPRETER_PATH
```






