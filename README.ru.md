# OpenAITelegramBOT

## Установка


1. Если не установлен Python, [установите отсюда](https://www.python.org/downloads/)

2. Клонируйте репозиторий

3. Зайдите  в директорию проекта

   ```bash
   $ cd OpenAITelegramBOT
   ```

4. Создайте виртуальное окружение

   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

5. Установите зависимости

   ```bash
   $ pip install -r requirements.txt
   ```
   
   Если не установился модуль python-telegram-bot, то установите его вручную:
   ```bash
   pip install python-telegram-bot -U --pre
   ```

6. Создайте копию файла окружения .env

   ```bash
   $ cp .env.example .env
   ```

7. Перейдите по ссылке [BotFather](https://telegram.me/BotFather)  (у вас должно быть установлено приложение Telegram) и создайте нового бота, отправив команду /newbot. Следуйте инструкциям, пока не получите имя пользователя и токен для вашего бота.

8. Перейдите по ссылке [OpenAI](https://beta.openai.com/account/api-keys) (вы должны быть зарегистрированы и авторизованы) и создайте ключ API

9. Заполните необходимые данные в созданном файле `.env`

10. Запустите приложение

   ```bash
   $ python main.py 

   ```

