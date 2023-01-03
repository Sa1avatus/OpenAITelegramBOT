# OpenAITelegramBOT

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/Sa1avatus/OpenAITelegramBOT/blob/main/README.md)
[![ru](https://img.shields.io/badge/lang-ru-green.svg)(https://github.com/Sa1avatus/OpenAITelegramBOT/blob/main/README.ru.md)


## Installation


1. If Python is not installed, [install it from here](https://www.python.org/downloads/)

2. Clone the repository

3. Enter the project directory

   ```bash
   $ cd OpenAITelegramBOT
   ```

4. Create a virtual environment

   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

5. Install dependencies

   ```bash
   $ pip install -r requirements.txt
   ```
   
   If the python-telegram-bot module is not installed, install it manually:
   ```bash
   pip install python-telegram-bot -U --pre
   ```

6. Create a copy of the .env environment file

   ```bash
   $ cp .env.example .env
   ```

7. Go to the [BotFather](https://telegram.me/BotFather) link (you should have the Telegram app installed) and create a new bot by sending the /newbot command. Follow the instructions until you receive the username and token for your bot.

8. Go to the [OpenAI](https://beta.openai.com/account/api-keys) link (you must be registered and logged in) and create an API key

9. Fill in the necessary information in the created .env file

10. Start the application

   ```bash
   $ python main.py 

   ```

