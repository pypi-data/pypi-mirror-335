from dataclasses import dataclass
from enum import Enum
from typing import Optional

class MessageStatus(Enum):
    """Статусы сообщений"""
    PENDING = "Ждет обработки"
    SENT = "Отправлено"
    DELIVERED = "Доставлено"
    FAILED = "Ошибка"
    # Другие статусы можно добавить по мере их документирования

@dataclass
class SMSMessage:
    """Структура SMS сообщения"""
    id: str
    message: str
    status: int
    callback_id: str
    device_id: str
    phone_number: str
    message_status: str
    time_create: int

@dataclass
class Device:
    """Структура устройства"""
    id: str
    name: str
    status: str
    last_seen: Optional[int] = None
    # Другие поля можно добавить по мере их документирования 