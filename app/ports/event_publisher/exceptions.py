from fastapi import HTTPException


class EventPublisherNotConnectedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=501, detail="Подключение к сервису очередей недоступно!"
        )
