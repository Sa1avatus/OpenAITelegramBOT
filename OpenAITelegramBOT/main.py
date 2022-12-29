import collections
import os
import logging
import openai
from telegram.ext import Filters
from telegram.ext import MessageHandler, CallbackQueryHandler, CommandHandler
from telegram.ext import Updater
import telegram
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
        #print("Received async def commands", update)
        chat_id = update.message.chat_id
        self.handlers.pop(chat_id, None)
        answer = next(self.handlers[chat_id])
        context.bot.sendMessage(chat_id=chat_id, text=answer, reply_markup=get_markup())

    def handle_message(self, update, context):
        #print("Received", update.message)
        chat_id = update.message.chat_id
        try:
            #print(f'try {self.model}')
            if self.model == 'dalle':
                answer = self.dalle_model(update.message.text)
            else:
                answer = self.gpt3_model(update.message.text, self.model)
        except StopIteration:
            #print(f'StopIteration')
            # если при этом генератор закончился -- что делать, начинаем общение с начала
            del self.handlers[chat_id]
            # (повторно вызванный, этот метод будет думать, что пользователь с нами впервые)
            return self.handle_message(update, context)
        #print("Answer: %r" % answer)
        context.bot.sendMessage(chat_id=chat_id, text=answer, reply_markup=get_markup())

    def handle_callback(self, update, context):
        #print("Received", update.callback_query)
        chat_id = update.callback_query.message.chat_id
        if (update.callback_query.data.split('#')[0] == 'model'):
            #print(f'model: {update.callback_query.data}')
            model = update.callback_query.data.split('#')[1]
            dialog_bot.model = model
            answer = f'Напишите, что вы хотите от модели:'
        else:
            del self.handlers[chat_id]
            # (повторно вызванный, этот метод будет думать, что пользователь с нами впервые)
            return self.handle_message(update, context)
        #print("Answer: %r" % answer)
        context.bot.sendMessage(chat_id=chat_id, text=answer)
        #context.bot.sendMessage(chat_id=chat_id, text=answer, reply_markup=get_markup())


    def dalle_model(self, text):
        response = openai.Image.create(
            prompt=text,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        #print(f'Response: {response}')
        return image_url


    def gpt3_model(self, text, model):
        #print(f'TEXT: {text}')
        #print(f'model: {model}')
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
        #print(f'{response["choices"][0]["text"]}')
        return f'{response["choices"][0]["text"]}\n\nИспользовалась модель: {response.model}'


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
    token = os.getenv('BOT_TOKEN')
    dialog_bot = DialogBot(token, dialog)
    dialog_bot.start()