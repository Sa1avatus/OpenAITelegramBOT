import collections
import os
import logging
import openai
import json
from telegram.ext import Filters
from telegram.ext import MessageHandler, CallbackQueryHandler, CommandHandler
from telegram.ext import Updater
import telegram
import redis
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
class DialogBot(object):
    def __init__(self, token, generator):
        self.updater = Updater(token=token)  # заводим апдейтера
        handler1 = MessageHandler(Filters.text & (~Filters.command), self.handle_message)
        handler2 = CallbackQueryHandler(self.handle_callback)
        handler3 = CommandHandler('start', self.start_command)
        self.updater.dispatcher.add_handler(handler1)
        self.updater.dispatcher.add_handler(handler2)  # ставим обработчик всех текстовых сообщений
        self.updater.dispatcher.add_handler(handler3)
        self.handlers = collections.defaultdict(generator)  # заводим мапу "id чата -> генератор"
        self.model = None

    def start(self):
        self.updater.start_polling()

    def start_command(self, update, context):
        chat_id = update.message.chat_id
        self.handlers.pop(chat_id, None)
        answer = next(self.handlers[chat_id])
        context.bot.sendMessage(chat_id=chat_id, text=answer, reply_markup=get_markup())

    def handle_message(self, update, context):
        chat_id = update.message.chat_id
        try:
            if red:
                model = red.get(update.message.chat_id).decode("utf-8")
            else:
                model = self.model

            if model == 'dalle':
                answer = self.dalle_model(update.message.text)
            else:
                answer = self.gpt3_model(update.message.text, model)
        except StopIteration:
            # если при этом генератор закончился -- что делать, начинаем общение с начала
            del self.handlers[chat_id]
            # (повторно вызванный, этот метод будет думать, что пользователь с нами впервые)
            return self.handle_message(update, context)
        context.bot.sendMessage(chat_id=chat_id, text=answer, reply_markup=get_markup())

    def handle_callback(self, update, context):
        chat_id = update.callback_query.message.chat_id
        if (update.callback_query.data.split('#')[0] == 'model'):
            model = update.callback_query.data.split('#')[1]
            dialog_bot.model = model
            if red:
                red.set(update.callback_query.message.chat_id, model)
            answer = f'Напишите, что вы хотите от модели:'
        else:
            del self.handlers[chat_id]
            # (повторно вызванный, этот метод будет думать, что пользователь с нами впервые)
            return self.handle_message(update, context)
        context.bot.sendMessage(chat_id=chat_id, text=answer)

    def dalle_model(self, text):
        response = openai.Image.create(
            prompt=text,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        return image_url

    def gpt3_model(self, text, model):
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
        used_tokens = f'Потрачено токенов: {response["usage"]["total_tokens"]}'
        used_model = f'Использовалась модель: {response.model}'
        return f'{response["choices"][0]["text"]}\n\n{used_model}\n{used_tokens}'


def dialog():
    answer = yield "Выберите модель взаимодействия с ИИ:"
    #answer = yield "Напишите, что вы хотите от модели:"
    return answer


def get_markup():
    item1 = telegram.InlineKeyboardButton(f'GPT-3 Davinchi', callback_data=f'model#text-davinci-003')
    item2 = telegram.InlineKeyboardButton(f'GPT-3 Curie', callback_data=f'model#text-curie-001')
    item3 = telegram.InlineKeyboardButton(f'GPT-3 Babbage', callback_data=f'model#text-babbage-001')
    item4 = telegram.InlineKeyboardButton(f'GPT-3 Ada', callback_data=f'model#text-ada-001')
    item5 = telegram.InlineKeyboardButton(f'DALL·E', callback_data=f'model#dalle')
    item6 = telegram.InlineKeyboardButton(f'Codex Davinchi', callback_data=f'model#code-davinci-002')
    item7 = telegram.InlineKeyboardButton(f'Codex Cushman', callback_data=f'model#code-cushman-001')
    keyboard = telegram.InlineKeyboardMarkup([[item1, item2, item3, item4], [item6, item7], [item5]])
    return keyboard


if __name__ == "__main__":
    start_sequence = "\nAI:"
    restart_sequence = "\nHuman: "
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
    dialog_bot = DialogBot(token, dialog)
    dialog_bot.start()