import os
import logging
import openai
from telegram.ext import filters
from telegram.ext import MessageHandler, CallbackQueryHandler
from telegram.ext import Application, CommandHandler
import telegram
import redis
from settings import main as s
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    filename='log_file.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class DialogBot(object):
    def __init__(self, token):
        self.application = Application.builder().token(token).build()
        handler1 = MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message)
        handler2 = CallbackQueryHandler(self.handle_callback)
        handler3 = CommandHandler('start', self.start_command)
        handler4 = CommandHandler('help', self.help_command)
        handler5 = CommandHandler('lang', self.lang_command)
        self.application.add_handler(handler1)
        self.application.add_handler(handler2)
        self.application.add_handler(handler3)
        self.application.add_handler(handler4)
        self.application.add_handler(handler5)
        self.chat_options = {}

    def start(self):
        self.application.run_polling()

    async def lang_command(self, update, context):
        chat_id = update.message.chat_id
        item1 = telegram.InlineKeyboardButton(f'🇷🇺 Русский', callback_data=f'lang#RU')
        item2 = telegram.InlineKeyboardButton(f'🇬🇧 English', callback_data=f'lang#EN')
        keyboard = telegram.InlineKeyboardMarkup([[item1, item2]])
        lang = 'EN' if not self.get_value(chat_id, 'lang') else self.get_value(chat_id, 'lang')
        answer = s.LANG_MESSAGE.get(lang)
        await context.bot.sendMessage(chat_id=chat_id, text=answer, reply_markup=keyboard)

    async def start_command(self, update, context):
        chat_id = update.message.chat_id
        lang = 'EN' if not self.get_value(chat_id, 'lang') else self.get_value(chat_id, 'lang')
        #red.flushdb() #TEST!!!
        #self.set_value(chat_id, 'tokens', os.getenv('USER_TOKENS')) #TEST!!!
        self.set_value(chat_id, 'conversation', '')
        if not self.get_value(chat_id, 'tokens'):
            self.set_value(chat_id, 'tokens', os.getenv('USER_TOKENS'))
            self.set_value(chat_id, 'user', update.message.chat.username)
        if not self.get_value(chat_id, 'lang'):
            await self.lang_command(update, context)
        else:
            tokens = int(self.get_value(chat_id, 'tokens')) if int(self.get_value(chat_id, 'tokens')) > 0 else 0
            answer = s.START_MESSAGE[lang].replace('%tokens%', str(tokens))
            await context.bot.sendMessage(chat_id=chat_id, text=answer, reply_markup=get_markup())

    async def help_command(self, update, context):
        chat_id = update.message.chat_id
        lang = 'EN' if not self.get_value(chat_id, 'lang') else self.get_value(chat_id, 'lang')
        text = s.HELP_MESSAGE.get(lang)
        answer = f'{text}'
        await context.bot.sendMessage(chat_id=chat_id, text=answer)

    def get_value(self, key, value):
        try:
            if red:
                str_value = red.hget(key, value).decode("utf-8")
            else:
                str_value = self.chat_options[key].get(value)
        except Exception as e:
            str_value = None
        return str_value

    def set_value(self, key, value1, value2):
        try:
            if red:
                red.hset(key, value1, value2)
            else:
                self.chat_options[key].update({value1: value2})
        except Exception as e:
            pass
        return None

    async def handle_message(self, update, context):
        chat_id = update.message.chat_id
        lang = 'EN' if not self.get_value(chat_id, 'lang') else self.get_value(chat_id, 'lang')
        str_conv = self.get_value(chat_id, 'conversation')
        str_conv = f'{str_conv}\n{update.message.text}'
        self.set_value(chat_id, 'conversation', str_conv)
        try:
            if int(self.get_value(chat_id, 'tokens')) > 0:
                model = self.get_value(chat_id, 'model')
                if model == 'dalle':
                    answer = self.dalle_model(chat_id, update.message.text)
                else:
                    answer = self.gpt3_model(chat_id, update.message.text, model)
            else:
                answer = s.NO_TOKENS[lang]
        except Exception as e:
            return self.start_command(update, context)
        await context.bot.sendMessage(chat_id=chat_id, text=answer)

    async def handle_callback(self, update, context):
        chat_id = update.callback_query.message.chat_id
        reply_markup = None
        lang = 'EN' if not self.get_value(chat_id, 'lang') else self.get_value(chat_id, 'lang')
        if int(self.get_value(chat_id, 'tokens')) <= 0:
            answer = s.NO_TOKENS[lang]
        else:
            if (update.callback_query.data.split('#')[0] == 'model'):
                model = update.callback_query.data.split('#')[1]
                self.set_value(chat_id, 'model', model)
                answer = s.ASK_MODEL[lang]
            elif (update.callback_query.data.split('#')[0] == 'lang'):
                lang = update.callback_query.data.split('#')[1]
                self.set_value(chat_id, 'lang', lang)
                answer = s.START_MESSAGE[lang].replace('%tokens%', self.get_value(chat_id, 'tokens'))
                reply_markup = get_markup()
            else:
                answer = 'Else'
        await context.bot.sendMessage(chat_id=chat_id, text=answer, reply_markup=reply_markup)

    def dalle_model(self, chat_id, text):
        response = openai.Image.create(
            prompt=text,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        used_tokens = self.get_used_tokens(chat_id, 'DALL*E', 20000)
        str_text = self.get_text_model_usage(chat_id, 'DALL*E', used_tokens)
        return f'{image_url}\n\n{str_text}'

    def gpt3_model(self, chat_id, text, model):
        str_conv = self.get_value(chat_id, 'conversation')
        text = f'{str_conv}\n{text}' if len(f'{str_conv}\n{text}') < 1000 else f'{str_conv}\n{text}'[-1000:]
        max_tokens = 2048 - len(text) - 100
        response = completion.create(
            prompt='"""\n{}\n"""'.format(text),
            model=model,
            temperature=0.9,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:"])
        used_tokens = self.get_used_tokens(chat_id, model, response["usage"]["total_tokens"])
        str_text = self.get_text_model_usage(chat_id, model, used_tokens)
        str_response = response["choices"][0]["text"]
        str_conv = f'{str_conv}\n{str_response}'
        self.set_value(chat_id, 'conversation', str_conv)
        #print(f'str_conv: {str_conv}')
        return f'{str_response}\n\n{str_text}'

    def get_used_tokens(self, chat_id, model, used_tokens):
        if model == 'text-davinci-003':
            used_tokens = used_tokens * 20 #цена 1к токена в Давинчи 2 цента
        elif model == 'text-curie-001':
            used_tokens = used_tokens * 2 #цена 1к токена в Curie 0.2 цента
        elif model == 'text-babbage-001':
            used_tokens = int(used_tokens / 2) #цена 1к токена в Babbage 0.05 цента
        elif model == 'text-ada-001':
            used_tokens = int(used_tokens / 2.5) #цена 1к токена в Babbage 0.04 цента
        elif model == 'dalle':
            used_tokens = 20000   #цена 1 картинки в ДАЛЛИ 2 цента
        else:
            used_tokens = used_tokens
        tokens = int(self.get_value(chat_id, 'tokens'))
        self.set_value(chat_id, 'tokens', tokens - used_tokens)
        return used_tokens

    def get_text_model_usage(self, chat_id, model, used_tokens):
        lang = 'EN' if not self.get_value(chat_id, 'lang') else self.get_value(chat_id, 'lang')
        tokens = int(self.get_value(chat_id, 'tokens'))
        used_model = f'{s.USED_MODEL[lang]} {model}'
        used_tokens_str = f'{s.USED_TOKENS[lang]} {used_tokens}'
        remain_tokens_str = f'{s.REMAIN_TOKENS[lang]} {tokens if tokens > 0 else 0}'
        return f'{used_model}\n{used_tokens_str}\n{remain_tokens_str}'


def get_markup():
    item1 = telegram.InlineKeyboardButton(f'GPT-3 Davinchi', callback_data=f'model#text-davinci-003')
    item2 = telegram.InlineKeyboardButton(f'GPT-3 Curie', callback_data=f'model#text-curie-001')
    item3 = telegram.InlineKeyboardButton(f'GPT-3 Babbage', callback_data=f'model#text-babbage-001')
    item4 = telegram.InlineKeyboardButton(f'GPT-3 Ada', callback_data=f'model#text-ada-001')
    item5 = telegram.InlineKeyboardButton(f'DALL·E', callback_data=f'model#dalle')
    item6 = telegram.InlineKeyboardButton(f'Codex Davinchi', callback_data=f'model#code-davinci-002')
    item7 = telegram.InlineKeyboardButton(f'Codex Cushman', callback_data=f'model#code-cushman-001')
    keyboard = telegram.InlineKeyboardMarkup([[item1, item2], [item3, item4], [item6, item7], [item5]])
    return keyboard


if __name__ == "__main__":
    openai.api_key = os.getenv("OPENAI_API_KEY")
    completion = openai.Completion()
    try:
        red = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT')),
            password=os.getenv('REDIS_PASSWORD')
                          )
        red.ping()
    except Exception as e:
        red = None
        print(f'REDIS Error: {e}')
    token = os.getenv('BOT_TOKEN')
    dialog_bot = DialogBot(token)
    dialog_bot.start()
