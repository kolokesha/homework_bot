class CheckTokensError(Exception):
    def __str__(self):
        return f'Не хвататет одной или нескольких переменных'


class MissingHomework(Exception):
    def __str__(self):
        return f'Отсутствует ключ homeworks в ответе'


class HomeworkNotList(Exception):
    def __str__(self):
        return f'Ключ Homeworks неверного типа, должен быть list'


class UnavailableServer(Exception):
    def __str__(self):
        return f'Сервис недоступен'


class EmptyEndpoint(Exception):
    def __str__(self):
        return f'Отсутствует ответ от сервиса'


class ApiConnectError(Exception):
    def __str__(self):
        return f'Ошибка при запросе к основному API'


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
