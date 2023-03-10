START_MESSAGE = {'RU': f'Вам доступно %tokens% токенов.\nВыберите модель взаимодействия с ИИ (для помощи, наберите /help):',
                 'EN': f'You have %tokens% tokens.\nChoose an AI Interaction Model (write /help for help):'
}
HELP_MESSAGE = {'RU': f'''
GPT-3.5: Набор моделей, которые улучшают GPT-3 и могут понимать и генерировать естественный язык или код.\n
GPT-3 Davinchi: Самая мощная модель GPT-3.
Может выполнять любую задачу, которую могут выполнять другие модели, часто с более высоким качеством.\n
GPT-3 Curie: Очень мощный, но быстрее и дешевле, чем Davinci.\n
GPT-3 Babbage: Способен выполнять простые задачи, очень быстро и недорого.\n
GPT-3 Ada: Способен выполнять очень простые задачи, обычно это самая быстрая модель в серии GPT-3 и самая низкая стоимость.\n
Codex Davinchi: Самая мощная модель Кодекса. Особенно хорош в переводе естественного языка в код.\n
Codex Cushman: Почти так же эффективен, как Davinci Codex, но немного быстрее.\n
DALL·E: Генерация изображений.

Для очистки беседы с чат-ботом, наберите /start
''',
'EN': f'''
GPT-3.5: A set of models that improve on GPT-3 and can understand as well as generate natural language or code\n
GPT-3 Davinchi: Most capable GPT-3 model. Can do any task the other models can do, often with higher quality,
longer output and better instruction-following.\n
GPT-3 Curie: Very capable, but faster and lower cost than Davinci.\n
GPT-3 Babbage: Capable of straightforward tasks, very fast, and lower cost.\n
GPT-3 Ada: Capable of very simple tasks, usually the fastest model in the GPT-3 series, and lowest cost.\n
Codex Davinchi: Most capable Codex model. Particularly good at translating natural language to code.\n
Codex Cushman: Almost as capable as Davinci Codex, but slightly faster.\n
DALL·E: Image generation

For clear conversation with chat-bot, write /start
'''
}
LANG_MESSAGE = {'RU': f'Выберите язык:',
                'EN': f'Choose language:'}
NO_TOKENS = {'RU': f'У вас недостаточно токенов для использования этой модели!',
             'EN': f'You do not have enough tokens to use this model!'}
ASK_MODEL = {'RU': f'Напишите, что вы хотите от модели:',
             'EN': f'Write what are want from model:'}
USED_MODEL = {'RU': f'Использовалась модель:',
             'EN': f'Used model:'}
USED_TOKENS = {'RU': f'Потрачено токенов:',
             'EN': f'Used tokens:'}
REMAIN_TOKENS = {'RU': f'Остаток токенов:',
             'EN': f'Remain tokens:'}
MODEL_PRICE = {'text-davinci-003': 20,
               'text-curie-001': 2,
               'text-babbage-001': 0.5,
               'text-ada-001': 0.4,
               'dalle': 20000,
               'code-davinci-002': 0,
               'code-cushman-001': 0,
               'gpt-3.5-turbo': 2,}
MINIMUM_TOKENS = {'text-davinci-003': 100,
               'text-curie-001': 100,
               'text-babbage-001': 100,
               'text-ada-001': 100,
               'dalle': 20000,
               'code-davinci-002': 0,
               'code-cushman-001': 0,
               'gpt-3.5-turbo': 100,   }
MAX_MODEL_TOKENS = {'text-davinci-003': 4000,
               'text-curie-001': 2048,
               'text-babbage-001': 2048,
               'text-ada-001': 2048,
               'code-davinci-002': 4000,
               'code-cushman-001': 2048,
               'gpt-3.5-turbo': 4000, }
MESSAGE_LENGTH = 4000