import collections
import os

import openai
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
import telegram
from dotenv import load_dotenv
load_dotenv()


class DialogBot(object):
    def __init__(self, token, generator):
        self.updater = Updater(token=token)  # заводим апдейтера
        handler = MessageHandler(Filters.text | Filters.command, self.handle_message)
        self.updater.dispatcher.add_handler(handler)  # ставим обработчик всех текстовых сообщений
        self.handlers = collections.defaultdict(generator)  # заводим мапу "id чата -> генератор"
        self.model = None

    def start(self):
        self.updater.start_polling()

    def handle_message(self, update, context):
        print("Received", update.message)
        chat_id = update.message.chat_id
        if update.message.text == '/start':
            # если передана команда /start, начинаем всё с начала -- для
            # этого удаляем состояние текущего чатика, если оно есть
            self.handlers.pop(chat_id, None)
            answer = next(self.handlers[chat_id])
        elif update.message.text.split('#')[0] == 'model':
            print(f'model: {update.message.text}')
            model = update.message.text
            dialog_bot.model = model
            answer = f'Вы выбрали модель {dialog_bot.model}'
        else:
            try:
                print(f'try {self.model}')
                if self.model == 'model#dalle':
                    answer = self.dalle_model(update.message.text)
                elif self.model == 'model#codex':
                    answer = self.codex_model(update.message.text)
                else:
                    answer = self.gpt3_model(update.message.text)
            except StopIteration:
                print(f'StopIteration')
                # если при этом генератор закончился -- что делать, начинаем общение с начала
                del self.handlers[chat_id]
                # (повторно вызванный, этот метод будет думать, что пользователь с нами впервые)
                return self.handle_message(update, context)
        print("Answer: %r" % answer)
        context.bot.sendMessage(chat_id=chat_id, text=answer, reply_markup=get_markup())

    def dalle_model(self, text):
        response = openai.Image.create(
            prompt=text,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        print(f'Response: {response}')
        return image_url

    def codex_model(self, text):
        response = completion.create(
            prompt='"""\n{}\n"""'.format(text),
            model='code-davinci-002',
            temperature=0.9,
            max_tokens=3100,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:"])
        return f'```python\n{response["choices"][0]["text"]}\n```'

    def gpt3_model(self, text):
        print(f'TEXT: {text}')
        response = completion.create(
            prompt='"""\n{}\n"""'.format(text),
            model='text-davinci-003',
            temperature=0.9,
            max_tokens=3100,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:"])
        print(f'{response["choices"][0]["text"]}')
        return f'{response["choices"][0]["text"]}'


    def __str__(self):
        return self.handler


def dialog():
    answer = yield "Выберите модель взаимодействия с ИИ:"
    answer = yield "Напишите, что вы хотите от модели:"
    return answer

def get_markup():
    item1 = telegram.InlineKeyboardButton(f'GPT-3', callback_data=f'model#davinchi')
    item2 = telegram.InlineKeyboardButton(f'DALL·E', callback_data=f'model#dalle')
    item3 = telegram.InlineKeyboardButton(f'Codex', callback_data=f'model#codex')
    keys = [['model#davinchi','model#dalle','model#codex']]
    keyboard = telegram.ReplyKeyboardMarkup(keys)
    #keyboard.add(item1, item2, item3)
    return keyboard


if __name__ == "__main__":
    openai.api_key = os.getenv("OPENAI_API_KEY")
    completion = openai.Completion()
    token = os.getenv('BOT_TOKEN')
    dialog_bot = DialogBot(token, dialog)
    dialog_bot.start()