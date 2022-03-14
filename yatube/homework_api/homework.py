import logging

...

PRACTICUM_TOKEN = ...
TELEGRAM_TOKEN = ...
CHAT_ID = ...

...

RETRY_TIME = 300
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
	@@ -19,36 +17,51 @@


def send_message(bot, message):
    ...


def get_api_answer(url, current_timestamp):
    ...


def parse_status(homework):
    verdict = ...
    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_response(response):
    homeworks = response.get('homeworks')
    ...


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    ...
    while True:
        try:
            ...
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
            continue
