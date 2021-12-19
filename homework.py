import json
import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram as telegram
from dotenv import load_dotenv

from exceptions import (ApiConnectError, HomeworkNotList, MissingHomework,
                        MissingHomeworkName, MissingHomeworkStatusInDict,
                        UnavailableServer)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 300
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
MESSAGES = []

logging.basicConfig(
    level=logging.INFO,
)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


def send_message(bot, message):
    """Отправка сообщения ботом."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        logger.info('Удачная отправка сообщения')
    except telegram.TelegramError as error:
        logger.error(f'Не удалось отпрвить сообщение по причине: {error}')


def get_api_answer(current_timestamp):
    """Получение ответа."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except requests.exceptions.RequestException as error:
        logging.error(f'{ApiConnectError()} {error}')
    if homework_statuses.status_code != HTTPStatus.OK:
        raise UnavailableServer()
    try:
        homework_statuses = homework_statuses.json()
    except json.JSONDecodeError as error:
        raise json.JSONDecodeError(f'Не удалось распарсить json:{error}',
                                   error.doc, error.pos)
    else:
        return homework_statuses


def check_response(response):
    """Проверка ответа."""
    if not isinstance(response, dict):
        raise TypeError('Ответ должен быть dict!')
    if 'homeworks' in response:
        if not isinstance(response['homeworks'], list):
            raise HomeworkNotList()
    else:
        raise MissingHomework()
    homework = response['homeworks']
    return homework


def parse_status(homework):
    """Получение названия и статуса работы и проверка на его изменение."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if not homework_name and not homework_status:
        raise MissingHomeworkName()

    if homework_status not in HOMEWORK_STATUSES:
        raise MissingHomeworkStatusInDict()

    verdict = HOMEWORK_STATUSES[homework_status]
    message = f'Изменился статус проверки работы "{homework_name}". {verdict}'
    return message


def check_tokens():
    """Проверка на наличие обязательных переменных в env."""
    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    missing_tokens = []
    for key, value in tokens.items():
        if not value:
            missing_tokens.append(key)
    if missing_tokens:
        logger.critical(f'Не хвататет одной или нескольких переменных'
                        f' {*missing_tokens,}')
        return False
    return True


def check_message(message, prev_message):
    """Проверка на повторную отправку ошибок."""
    return message != prev_message


def main():
    """Основная логика работы бота."""
    prev_message = ''
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            if 'current_timestamp' in response:
                current_timestamp = response['current_timestamp']
            homework = check_response(response)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if check_message(message, prev_message):
                prev_message = message
                logger.error(error)
                send_message(bot, message)
        else:
            if homework:
                message = parse_status(homework[0])
                send_message(bot, message)
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
