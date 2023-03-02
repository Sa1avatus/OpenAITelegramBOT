import os
from transformers import GPT2Tokenizer
import logging
import openai
from telegram.ext import filters
from telegram.ext import MessageHandler, CallbackQueryHandler
from telegram.ext import Application, CommandHandler
import telegram
import redis
import settings as s
import json
import ast
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    #filename='log_file.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)


class DialogBot(object):
    def __init__(self, token):
        '''
        This is the constructor for the DialogBot class.
        It takes in one argument, token, which is the token for the Telegram bot.
        It creates an instance of the Application class from the telegram.ext library and sets the token for the bot.
        It then creates five MessageHandler and CallbackQueryHandler objects, each with a different command or filter,
        and adds them to the application object.
        :param token: Telegram bot token
        '''
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
        '''
        This method starts the bot by running the run_polling() method on the application object.
        This causes the bot to start listening for updates from Telegram.
        '''
        self.application.run_polling()

    def check_user(self, chat_id, update):
        '''
        Checking existing user parameters in cache
        :param chat_id: user id
        :param update: Update object containing the check_user
        :return: None
        '''
        if not self.get_value(chat_id, 'tokens'):
            self.set_value(chat_id, 'tokens', os.getenv('USER_TOKENS'))
        if not self.get_value(chat_id, 'user'):
            self.set_value(chat_id, 'user', update.message.chat.username)
        if not self.get_value(chat_id, 'lang'):
            self.set_value(chat_id, 'lang', 'EN')

    async def lang_command(self, update, context):
        '''
        This method is used when the command '/lang' is received by the bot.
        It takes in two arguments: update and context.
        update is an object that contains information about the update received by the bot,
        and context is an object that contains information about the context in which the update was received.
        It first retrieves the chat_id of the user who sent the command.
        Then it creates two InlineKeyboardButton objects for the languages Russian and English,
        and creates an InlineKeyboardMarkup object using these buttons.
        It then checks if the user has previously selected a language and uses that language as the default,
        otherwise it defaults to English.
        It then sends a message to the user with the option to select a language and the reply markup.
        :param update: Update object containing the lang command
        :param context: Context object containing the context of the lang command
        '''
        chat_id = update.message.chat_id
        item1 = telegram.InlineKeyboardButton(f'🇷🇺 Русский', callback_data=f'lang#RU')
        item2 = telegram.InlineKeyboardButton(f'🇬🇧 English', callback_data=f'lang#EN')
        keyboard = telegram.InlineKeyboardMarkup([[item1, item2]])
        self.check_user(chat_id, update)
        lang = self.get_value(chat_id, 'lang')
        answer = s.LANG_MESSAGE.get(lang)
        await context.bot.sendMessage(chat_id=chat_id, text=answer, reply_markup=keyboard)

    async def start_command(self, update, context):
        '''
        This method is used when the command '/start' is received by the bot. It takes in two arguments:
        update and context. update is an object that contains information about the update received by the bot,
        and context is an object that contains information about the context in which the update was received.
        It first retrieves the chat_id of the user who sent the command.
        Then it checks if the user has previously selected a language and uses that language as the default,
        otherwise it defaults to English. It then sets the 'conversation' field to an empty string.
        If the user has not set a number of tokens yet,
        it sets that field to the number of tokens specified in the .env file,
        and also sets the 'user' field to the username of the chat.
        If the user has not set a language yet it calls the lang_command method,
        otherwise it retrieves the number of tokens the user has and sends a message
        to the user with the number of tokens they have and some options.
        :param update: Update object containing the start command
        :param context: Context object containing the context of the start command
        '''
        chat_id = update.message.chat_id
        self.check_user(chat_id, update)
        lang = self.get_value(chat_id, 'lang')
        self.set_value(chat_id, 'conversation', '')
        self.set_value(chat_id, 'messages', '')
        tokens = int(self.get_value(chat_id, 'tokens')) if int(self.get_value(chat_id, 'tokens')) > 0 else 0
        answer = s.START_MESSAGE[lang].replace('%tokens%', str(tokens))
        await context.bot.sendMessage(chat_id=chat_id, text=answer, reply_markup=get_markup(tokens))

    async def help_command(self, update, context):
        '''
        This method is used when the command '/help' is received by the bot.
        It takes in two arguments: update and context.
        update is an object that contains information about the update received by the bot,
        and context is an object that contains information about the context in which the update was received.
        It first retrieves the chat_id of the user who sent the command.
        Then it checks if the user has previously selected a language and uses that language as the default,
        otherwise it defaults to English.
        It then retrieves the help message for the selected language and sends it to the user as a message.
        :param update: Update object containing the help command
        :param context: Context object containing the context of the help command
        '''
        chat_id = update.message.chat_id
        self.check_user(chat_id, update)
        lang = self.get_value(chat_id, 'lang')
        text = s.HELP_MESSAGE.get(lang)
        answer = f'{text}'
        await context.bot.sendMessage(chat_id=chat_id, text=answer)

    def get_value(self, key, value):
        '''
        This function is used to retrieve a value stored in the chat_options dictionary for a specific chat,
        identified by its chat_id. It takes in two arguments:
        chat_id and key. It returns the value of the key from the dictionary.
        :param chat_id: Chat id for which the value is to be returned
        :param key: Key for which the value is to be returned
        :return: Value for the given key
        '''
        try:
            if red:
                str_value = red.hget(key, value).decode("utf-8")
            else:
                str_value = self.chat_options[key].get(value)
        except Exception as e:
            logging.error(e)
            str_value = None
        return str_value

    def set_value(self, key, value1, value2):
        '''
        This function is used to set a value in the chat_options dictionary for a specific chat,
        identified by its chat_id.
        It takes in three arguments: chat_id, key, and value.
        It assigns the value to the key in the dictionary.
        If the chat_id is not in the chat_options it creates an empty dictionary.
        :param chat_id: Chat id for which the value is to be set
        :param key: Key for which the value is to be set
        :param value: Value to be set
        '''
        try:
            if red:
                red.hset(key, value1, value2)
            else:
                if not self.chat_options.get(key):
                    self.chat_options[key] = {}
                self.chat_options[key].update({value1: value2})
        except Exception as e:
            logging.error(e)
        return None

    async def handle_message(self, update, context):
        '''
        This method handles incoming messages that are not commands. It takes in two arguments:
        update and context. update is an object that contains information about the update received by the bot,
        and context is an object that contains information about the context in which the update was received.
        It first retrieves the chat_id of the user who sent the message and checks if the user has previously
        selected a language and uses that language as the default, otherwise it defaults to English.
        It then retrieves the current conversation of the user, and append the received message to it.
        Then it checks if the user has enough tokens to use the selected model,
        if the user has enough tokens it calls the selected model to generate a response.
        If the user doesn't have enough tokens it sends a message telling the user that they don't have enough tokens.
        In case of any exception occurred, it calls the start_command method to start a new conversation.
        Finally, it sends the response generated by the selected model to the user.
        :param update: Update object containing the message
        :param context: Context object containing the context of the message
        '''
        chat_id = update.message.chat_id
        self.check_user(chat_id, update)
        lang = self.get_value(chat_id, 'lang')
        str_conv = self.get_value(chat_id, 'conversation')
        str_conv = f'{str_conv}\n{update.message.text}'
        self.set_value(chat_id, 'conversation', str_conv)
        try:
            model = self.get_value(chat_id, 'model')
            if int(self.get_value(chat_id, 'tokens')) > s.MINIMUM_TOKENS[model]:
                if model == 'dalle':
                    answer = self.dalle_model(chat_id, update.message.text)
                elif model == 'gpt-3.5-turbo':
                    answer = self.gpt3_chat_model(chat_id, update.message.text, model)
                else:
                    answer = self.gpt3_model(chat_id, update.message.text, model)
            else:
                answer = s.NO_TOKENS[lang]
            await context.bot.sendMessage(chat_id=chat_id, text=answer)
        except Exception as e:
            logging.error(e)
            await self.start_command(update, context)

    async def handle_callback(self, update, context):
        '''
        This method handles incoming callback queries,
        which are triggered by the user interacting with inline keyboard buttons.
        It takes in two arguments: update and context.
        update is an object that contains information about the update received by the bot,
        and context is an object that contains information about the context in which the update was received.
        It first retrieves the chat_id of the user who sent the callback query and checks
        if the user has previously selected a language and uses that language as the default,
        otherwise it defaults to English. Then it checks if the user has enough tokens to proceed.
        If the user doesn't have enough tokens it sends a message telling the user that they don't have enough tokens.
        If the user has enough tokens it checks the callback data to determine the action taken by the user.
        If the user selected a model, it sets the selected model for the user and sends
        a message asking for the user's input.
        If the user selected a language, it sets the selected language for the user and sends
        a message with the current token balance and a markup to select the model.
        :param update: Update object containing the callback query
        :param context: Context object containing the context of the callback query
        '''
        chat_id = update.callback_query.message.chat_id
        self.check_user(chat_id, update.callback_query)
        reply_markup = None
        lang = self.get_value(chat_id, 'lang')
        try:
            tokens = int(self.get_value(chat_id, 'tokens'))
            if (update.callback_query.data.split('#')[0] == 'model'):
                model = update.callback_query.data.split('#')[1]
                self.set_value(chat_id, 'model', model)
                if tokens < s.MINIMUM_TOKENS[model]:
                    answer = s.NO_TOKENS[lang]
                else:
                    answer = s.ASK_MODEL[lang]
            elif (update.callback_query.data.split('#')[0] == 'lang'):
                lang = update.callback_query.data.split('#')[1]
                self.set_value(chat_id, 'lang', lang)
                answer = s.START_MESSAGE[lang].replace('%tokens%', self.get_value(chat_id, 'tokens'))
                reply_markup = get_markup(tokens)
            else:
                answer = 'Else'
            await context.bot.sendMessage(chat_id=chat_id, text=answer, reply_markup=reply_markup)
        except Exception as e:
            logging.error(e)
            await self.start_command(update.callback_query, context)

    def dalle_model(self, chat_id, text):
        '''
        This method is used to generate an image from the DALL-E model.
        It takes in two arguments: chat_id and text.
        chat_id is the unique identifier of the user who sent the message and text is the text input provided by the user.
        It uses the openai.Image.create() method to generate an image
        based on the text input and with the parameters n=1 and size="1024x1024".
        It then retrieves the url of the generated image and saves it to the variable image_url.
        It then calls the function get_used_tokens(self, chat_id, 'DALL*E', 20000)
        to calculate the used token for DALL-E model and get_text_model_usage(self, chat_id, 'DALL*E', used_tokens)
        to get the usage message and returns a string containing the image url and usage message.
        :param chat_id: Telegram chat id
        :param text: Input text for the DALL-E model
        :return: String containing the url of the generated image and the information about the model and token usage
        '''
        response = openai.Image.create(
            prompt=text,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        used_tokens = self.get_used_tokens(chat_id, 'dalle', 1)
        str_text = self.get_text_model_usage(chat_id, 'DALL*E', used_tokens)
        return f'{image_url}\n\n{str_text}'

    def gpt3_model(self, chat_id, text, model):
        '''
        This method is used to generate text from the GPT-3 model. It takes in three arguments: chat_id, text, and model.
        It first retrieves the current conversation from the Redis store using the
        get_value(self, chat_id, 'conversation') method and concatenates it with the new text input.
        It then limits the length of the text to 1000 characters if the length is more than 1000.
        It uses the completion.create() method to generate text based on the input text, the selected model,
        temperature, max_tokens, top_p, frequency_penalty, presence_penalty and stop.
        It then calls the get_used_tokens(self, chat_id, model, response["usage"]["total_tokens"]) method
        to calculate the used tokens for the selected model and get_text_model_usage(self, chat_id, model, used_tokens)
        method to get the usage message.
        It then concatenates the generated text with the current conversation and saves it back to the Redis store.
        It returns a string containing the generated text and the usage message.
        :param chat_id: Telegram chat id
        :param text: Input text for the GPT-3 model
        :param model: GPT-3 model to use
        :return: String containing the generated text and the information about the model and token usage
        '''
        str_conv = self.get_value(chat_id, 'conversation')
        text = f'{str_conv}\n{text}' if len(f'{str_conv}\n{text}') < 1000 else f'{str_conv}\n{text}'[-1000:]
        max_tokens = s.MAX_MODEL_TOKENS[model] - get_tokens_number(text) - 100
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
        return f'{str_response}\n\n{str_text}'

    def gpt3_chat_model(self, chat_id, text, model):
        max_tokens = s.MAX_MODEL_TOKENS[model] - get_tokens_number(text) - 100
        messages = ast.literal_eval(str(self.get_value(chat_id, 'messages'))) if self.get_value(chat_id, 'messages') else []
        messages.append({'role': 'user', 'content': text})
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
        )
        used_tokens = self.get_used_tokens(chat_id, model, response["usage"]["total_tokens"])
        str_text = self.get_text_model_usage(chat_id, model, used_tokens)
        str_response = response['choices'][0]['message']['content']
        messages.append({'role': 'assistant', 'content': str_response})
        self.set_value(chat_id, 'messages', messages)
        return f'{str_response}\n\n{str_text}'

    def get_used_tokens(self, chat_id, model, used_tokens):
        '''
        It checks the model passed in and multiplies the used_tokens by a factor based on the cost per token
        for that model, the cost per token is hardcoded.
        It then retrieves the current number of tokens from the Redis store using the
        get_value(self, chat_id, 'tokens') method and subtracts the used tokens from it.
        It then saves the updated number of tokens back to the Redis store using the
        set_value(self, chat_id, 'tokens', tokens - used_tokens) method.
        It returns the number of tokens used.
        '''
        used_tokens = used_tokens * s.MODEL_PRICE[model]
        tokens = int(self.get_value(chat_id, 'tokens'))
        self.set_value(chat_id, 'tokens', tokens - used_tokens)
        return used_tokens

    def get_text_model_usage(self, chat_id, model, used_tokens):
        '''
        Returns a string containing the information about the model and token usage for the provided chat_id.
        :param chat_id: Telegram chat id
        :param model: GPT-3 model used
        :param used_tokens: Number of tokens used
        :return: String containing the information about the model and token usage
        '''
        lang = 'EN' if not self.get_value(chat_id, 'lang') else self.get_value(chat_id, 'lang')
        tokens = int(self.get_value(chat_id, 'tokens'))
        used_model = f'{s.USED_MODEL[lang]} {model}'
        used_tokens_str = f'{s.USED_TOKENS[lang]} {used_tokens}'
        remain_tokens_str = f'{s.REMAIN_TOKENS[lang]} {tokens if tokens > 0 else 0}'
        return f'{used_model}\n{used_tokens_str}\n{remain_tokens_str}'


def get_markup(tokens):
    '''
    Returns the markup for the given number of tokens
    :param tokens: Number of tokens
    :return: InlineKeyboardMarkup object
    '''
    items = []
    item1 = telegram.InlineKeyboardButton(f'GPT-3 Davinchi', callback_data=f'model#text-davinci-003')
    item2 = telegram.InlineKeyboardButton(f'GPT-3 Curie', callback_data=f'model#text-curie-001')
    item3 = telegram.InlineKeyboardButton(f'GPT-3 Babbage', callback_data=f'model#text-babbage-001')
    item4 = telegram.InlineKeyboardButton(f'GPT-3 Ada', callback_data=f'model#text-ada-001')
    item5 = telegram.InlineKeyboardButton(f'DALL·E', callback_data=f'model#dalle')
    item6 = telegram.InlineKeyboardButton(f'Codex Davinchi', callback_data=f'model#code-davinci-002')
    item7 = telegram.InlineKeyboardButton(f'Codex Cushman', callback_data=f'model#code-cushman-001')
    item8 = telegram.InlineKeyboardButton(f'GPT-3.5', callback_data=f'model#gpt-3.5-turbo')
    if tokens > 0:
        items.append([item8])
        items.append([item1, item2])
        items.append([item3, item4])
    items.append([item6, item7])
    if tokens > 20000:
        items.append([item5])
    keyboard = telegram.InlineKeyboardMarkup(items)
    return keyboard


def get_tokens_number(text):
    '''
    This function takes a string as input 'text' and returns the number of tokens in it.
    It uses the 'gpt2' tokenizer from the transformers library to tokenize the input text.
    In case of any exception, it returns the length of the input text.
    :param text: input text
    :return tokens_len: number of tokens in it
    '''
    try:
        tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        tokenized_sentence = tokenizer.tokenize(text)
        tokens_len = len(tokenized_sentence)
    except Exception as e:
        logging.warning(e)
        tokens_len = len(text)
    return tokens_len


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
        #red.flushdb()  # TEST!!!
    except redis.exceptions.RedisError as e:
        logging.warning(e)
        red = None
    token = os.getenv('BOT_TOKEN')
    dialog_bot = DialogBot(token)
    dialog_bot.start()