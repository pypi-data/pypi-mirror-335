# GoSMS Python Client

Python клиент для работы с API сервиса отправки SMS сообщений GoSMS.

## Установка

```bash
pip install gosms-ru-client
```

## Аутентификация

Для работы с API необходим JWT токен. Получить его можно в панели управления GoSMS:

1. Войдите в панель управления по адресу https://cms.gosms.ru
2. Перейдите в раздел "API интеграция"
3. Нажмите "Создать токен"
4. Скопируйте полученный токен и используйте его при инициализации клиента

## Использование

```python
from gosms import GoSMSClient

# Инициализация клиента
client = GoSMSClient(token="your_jwt_token")

try:
    # Отправка SMS
    message = client.send_sms(
        phone_number="79999999999",
        message="Тестовое сообщение"
    )
    print(f"Сообщение отправлено: {message}")
    
    # Получение списка сообщений
    messages = client.get_messages(limit=10)
    print(f"Последние сообщения: {messages}")
    
except GoSMSError as e:
    print(f"Ошибка API: {e}")
```

## Возможности

- Отправка SMS сообщений
- Получение списка сообщений с пагинацией и поиском
- Обработка ошибок API
- Поддержка типизации (type hints)

## Требования

- Python 3.7 или выше
- requests>=2.25.0

## Документация

Полная документация доступна на сайте: https://docs.gosms.ru

## Лицензия

MIT 