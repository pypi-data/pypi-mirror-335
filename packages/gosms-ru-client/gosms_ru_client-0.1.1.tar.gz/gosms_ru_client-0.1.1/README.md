# GoSMS Python Client

Python client for GoSMS API.

## Installation

```bash
pip install gosms-ru-client
```

## Authentication

Для работы с API необходим JWT токен. Получить его можно в панели управления GoSMS:

1. Войдите в панель управления по адресу https://cms.gosms.ru
2. Перейдите в раздел "API интеграция"
3. Нажмите "Создать токен"
4. Скопируйте полученный токен и используйте его при инициализации клиента

## Usage

```python
from gosms import GoSMSClient

# Initialize client
client = GoSMSClient(token="your_jwt_token")

try:
    # Send SMS
    message = client.send_sms(
        phone_number="79999999999",
        message="Test message"
    )
    print(f"Message sent: {message}")
    
    # Get message list
    messages = client.get_messages(limit=10)
    print(f"Recent messages: {messages}")
    
except GoSMSError as e:
    print(f"API Error: {e}")
```

## Features

- Send SMS messages
- Get message list with pagination and search
- API error handling
- Type hints

## Requirements

- Python 3.7+
- requests>=2.25.0

## License

MIT 