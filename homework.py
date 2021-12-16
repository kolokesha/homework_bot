import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram as telegram
from dotenv import load_dotenv

from exceptions import (ApiConnectError, CheckTokensError, EmptyEndpoint,
                        FailedSendMessage, HomeworkNotList, MissingHomework,
                        MissingHomeworkName, MissingHomeworkStatusInDict,
                        UnavailableServer)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
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
    except FailedSendMessage:
        logger.error(FailedSendMessage())
        raise FailedSendMessage()


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
    except ApiConnectError:
        logger.error(ApiConnectError())
        raise ApiConnectError()
    if homework_statuses.status_code != HTTPStatus.OK:
        logger.error(UnavailableServer())
        raise UnavailableServer()
    if homework_statuses:
        return homework_statuses.json()
    logger.error(EmptyEndpoint())
    raise EmptyEndpoint()


def check_response(response):
    """Проверка ответа."""
    try:
        if 'homeworks' in response:
            if not isinstance(response['homeworks'], list):
                logger.error(HomeworkNotList())
                raise HomeworkNotList()
    except MissingHomework:
        logger.error(MissingHomework())
        raise MissingHomework()
    homework = response['homeworks']
    return homework


def parse_status(homework):
    """Получение названия и статуса работы и проверка на его изменение."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if not homework_name and not homework_status:
        logger.error(MissingHomeworkName())
        raise MissingHomeworkName()

    if homework_status not in HOMEWORK_STATUSES:
        logger.error(MissingHomeworkStatusInDict())
        raise (MissingHomeworkStatusInDict())

    verdict = HOMEWORK_STATUSES[homework_status]
    message = f'Изменился статус проверки работы "{homework_name}". {verdict}'
    return message


def check_tokens():
    """Проверка на наличие обязательных переменных в env."""
    if not (PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID):
        logger.critical('Не хвататет одной или нескольких переменных')
        return False
    return True


def check_message(message):
    """Проверка на повторную отправку ошибок."""
    if not MESSAGES or message != MESSAGES[-1]:
        MESSAGES.append(message)
        return True
    return False


def main():
    """Основная логика работы бота."""
    if check_tokens():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        current_timestamp = int(time.time())
    else:
        raise CheckTokensError()
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            current_timestamp += RETRY_TIME
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if check_message(message):
                send_message(bot, message)
                time.sleep(RETRY_TIME)
        else:
            message = ''
            if homework:
                message = parse_status(homework[0])
            if message:
                send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
