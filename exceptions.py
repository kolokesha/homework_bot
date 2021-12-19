class MissingHomework(Exception):
    def __str__(self):
        return f'Отсутствует ключ homeworks в ответе'


class HomeworkNotList(Exception):
    def __str__(self):
        return f'Ключ Homeworks неверного типа, должен быть list'


class UnavailableServer(Exception):
    def __init__(self, code):
        self.code = code
        self.message = f'Сервис недоступен, код ответа:{code}'

    def __str__(self):
        return self.message


class EmptyEndpoint(Exception):
    def __str__(self):
        return f'Отсутствует ответ от сервиса'


class ApiConnectError(Exception):
    def __init__(self, error):
        self.error = error
        self.message = f'Ошибка при запросе к основному API:{error}'

    def __str__(self):
        return self.message


class MissingHomeworkName(Exception):
    def __str__(self):
        return f'Отсутствует ключ homework_name и status в ответе'


class MissingHomeworkStatusInDict(Exception):
    def __str__(self):
        return (f'Недокументированный статус домашней работы,'
                f' обнаруженный в ответе')


class FailedSendMessage(Exception):
    def __str__(self):
        return f'Неудачная отправка сообщения'
