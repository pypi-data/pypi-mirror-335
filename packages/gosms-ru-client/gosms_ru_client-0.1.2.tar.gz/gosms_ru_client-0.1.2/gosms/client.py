from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import requests
from enum import Enum
import time

class GoSMSError(Exception):
    """Базовый класс для ошибок GoSMS API"""
    def __init__(self, code: int, message: str, hash: Optional[str] = None):
        self.code = code
        self.message = message
        self.hash = hash
        super().__init__(f"[{code}] {message}")

class MessageStatus(Enum):
    """Статусы сообщений"""
    PENDING = "Ждет обработки"
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

class GoSMSClient:
    """Клиент для работы с API GoSMS"""
    
    BASE_URL = "https://api.gosms.ru/v1"
    
    def __init__(self, token: str):
        """
        Инициализация клиента
        
        Args:
            token: JWT токен для аутентификации
        """
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Обработка ответа от API"""
        if response.status_code >= 400:
            error_data = response.json().get("errors", {})
            raise GoSMSError(
                code=error_data.get("code", 0),
                message=error_data.get("message", "Неизвестная ошибка"),
                hash=error_data.get("hash")
            )
        
        return response.json() if response.status_code != 204 else {}

    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Выполнение HTTP запроса"""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        response = self.session.request(
            method=method,
            url=url,
            json=data,
            params=params
        )
        
        return self._handle_response(response)

    def send_sms(self, phone_number: str, message: str) -> SMSMessage:
        """
        Отправка SMS сообщения
        
        Args:
            phone_number: Номер телефона получателя в формате 79XXXXXXXXX
            message: Текст сообщения
            
        Returns:
            SMSMessage: Информация об отправленном сообщении
        """
        data = {
            "phone_number": phone_number,
            "message": message
        }
        
        response = self._make_request(
            method="POST",
            endpoint="/sms/send",
            data=data
        )
        
        return SMSMessage(**response)

    def get_messages(
        self, 
        limit: Optional[int] = None, 
        offset: Optional[int] = None,
        search: Optional[str] = None
    ) -> List[SMSMessage]:
        """
        Получение списка сообщений с поддержкой пагинации и поиска
        
        Args:
            limit: Количество записей для возврата
            offset: Смещение относительно начала списка
            search: Строка для поиска
            
        Returns:
            List[SMSMessage]: Список сообщений
        """
        params = {
            "limit": limit,
            "offset": offset,
            "search": search
        }
        
        # Удаляем None значения
        params = {k: v for k, v in params.items() if v is not None}
        
        response = self._make_request(
            method="GET",
            endpoint="/sms",
            params=params
        )
        
        return [SMSMessage(**msg) for msg in response.get("messages", [])] 