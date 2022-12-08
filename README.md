# NewsPortal учебный проект по Django

## Установка


1. Если не установлен Python, [установите отсюда](https://www.python.org/downloads/)

2. Клонируйте репозиторий

3. Зайдите  в директорию проекта

   ```bash
   $ cd NewsPaper
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

6. Создайте копию файла окружения .env

   ```bash
   $ cp .env.example .env
   ```

7. Заполните необходимые данные в созданном файле `.env`

8. Запустите приложение

   ```bash
   $ python manage.py runserver 
   $ celery -A NewsPaper worker -l INFO -P solo
   $ celery -A NewsPaper beat -l INFO
   ```

Доступ к порталу будет по ссылке [http://localhost:8000](http://localhost:8000)!


