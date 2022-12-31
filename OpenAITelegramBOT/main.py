import collections
import os
import logging
import openai
from telegram.ext import filters
from telegram.ext import MessageHandler, CallbackQueryHandler
from telegram.ext import Application, CommandHandler
import telegram
import redis
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    filename='log_file.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class DialogBot(object):
    def __init__(self, token):
        self.application = Application.builder().token(token).build()  # заводим апдейтера
        handler1 = MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message)
        handler2 = CallbackQueryHandler(self.handle_callback)
        handler3 = CommandHandler('start', self.start_command)
        self.application.add_handler(handler1)
        self.application.add_handler(handler2)  # ставим обработчик всех текстовых сообщений
        self.application.add_handler(handler3)
        #self.handlers = collections.defaultdict(generator)  # заводим мапу "id чата -> генератор"
        #self.model = None
        self.chat_options = {}#int(os.getenv('USER_TOKENS')) # число токенов, доступных юзеру

    def start(self):
        self.application.run_polling()

    async def start_command(self, update, context):
        chat_id = update.message.chat_id
        #self.handlers.pop(chat_id, None)
        if not self.get_tokens(chat_id):
            if red:
                red.hset(chat_id, 'tokens', os.getenv('USER_TOKENS'))
                red.hset(chat_id, 'user', update.message.chat.username)
            else:
                self.chat_options[chat_id] = {'tokens': os.getenv('USER_TOKENS')}
        tokens = int(self.get_tokens(chat_id))
        answer = f'вам доступно {tokens} токенов.\nВыберите модель взаимодействия с ИИ:'#next(self.handlers[chat_id])
        await context.bot.sendMessage(chat_id=chat_id, text=answer, reply_markup=get_markup())

    def get_model(self, chat_id):
        if red:
            model = red.hget(chat_id, 'model').decode("utf-8")
        else:
            model = self.chat_options[chat_id]['model']
        return model

    def get_tokens(self, chat_id):
        try:
            if red:
                tokens = red.hget(chat_id, 'tokens').decode("utf-8")
            else:
                tokens = self.chat_options[chat_id]['tokens']
        except Exception as e:
            tokens = None
        return tokens

    def get_redis_value(self, key, value):
        try:
            str_value = red.hget(key, value).decode("utf-8")
            return str_value
        except Exception as e:
            return None

    def set_redis_value(self, key, value1, value2):
        try:
            red.hset(key, value1, value2)
        except Exception as e:
            return None

    async def handle_message(self, update, context):
        chat_id = update.message.chat_id
        try:
            if int(self.get_tokens(chat_id)) > 0:
                model = self.get_model(chat_id)
                if model == 'dalle':
                    answer = self.dalle_model(chat_id, update.message.text)
                else:
                    answer = self.gpt3_model(chat_id, update.message.text, model)
            else:
                answer = 'У вас закончились токены!'
        except Exception as e:
            print(e.__str__())
            return self.start_command(update, context)
        if red:
            red.hset(chat_id, 'last_answer', answer)
            red.hset(update.update_id, 'quote', answer)
        await context.bot.sendMessage(chat_id=chat_id, text=answer)

    async def handle_callback(self, update, context):
        chat_id = update.callback_query.message.chat_id
        if int(self.get_tokens(chat_id)) <= 0:
            answer = 'У вас закончились токены!'
        else:
            if (update.callback_query.data.split('#')[0] == 'model'):
                model = update.callback_query.data.split('#')[1]
                if red:
                    red.hset(chat_id, "model", model)
                else:
                    if not self.chat_options.get(chat_id):
                        self.chat_options[chat_id] = {'tokens': os.getenv('USER_TOKENS')}
                    self.chat_options[chat_id].update({'model': model})
                answer = f'Напишите, что вы хотите от модели:'
            else:
                return self.start_command(update, context)
            if red:
                red.hset(chat_id, 'last_quote', answer)
                red.hset(update.update_id, 'answer', answer)
        await context.bot.sendMessage(chat_id=chat_id, text=answer)

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
        return f'{response["choices"][0]["text"]}\n\n{str_text}'

    def get_used_tokens(self, chat_id, model, used_tokens):
        if model == 'text-davinci-003':
            used_tokens = used_tokens * 20 #цена 1к токена в Давинчи 2 цента
        elif model == 'text-curie-001':
            used_tokens = used_tokens * 2 #цена 1к токена в Curie 0.2 цента
        elif model == 'text-babbage-001':
            used_tokens = int(used_tokens / 2) #цена 1к токена в Babbage 0.05 цента
        elif model == 'text-ada-001':
            used_tokens = int(used_tokens / 2.5) #цена 1к токена в Babbage 0.04 цента
        elif model == 'DALL*E':
            used_tokens = 20000   #цена 1 картинки в ДАЛЛИ 2 цента
        else:
            used_tokens = used_tokens
        tokens = int(self.get_tokens(chat_id))
        if red:
            self.set_redis_value(chat_id, 'tokens', tokens - used_tokens)
        else:
            self.chat_options[chat_id]['tokens'] = int(self.chat_options[chat_id]['tokens']) - int(used_tokens)
        return used_tokens

    def get_text_model_usage(self, chat_id, model, used_tokens):
        tokens = int(self.get_tokens(chat_id))
        used_model = f'Использовалась модель: {model}'
        used_tokens_str = f'Потрачено токенов: {used_tokens}'
        remain_tokens_str = f'Остаток токенов: {tokens - used_tokens if tokens - used_tokens > 0 else 0}'
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
    dialog_bot = DialogBot(token)
    dialog_bot.start()