# Дрими - Бот для толкования снов 🌙✨

[English version](README.en.md) | Русская версия

Telegram-бот, который помогает интерпретировать сны с помощью искусственного интеллекта. Пользователи могут отправлять описания своих снов текстом или голосовыми сообщениями и получать глубокие интерпретации на основе психологии и символизма.

## Основные возможности

- 🗣 Поддержка голосовых сообщений с автоматической транскрипцией
- ✍️ Текстовые сообщения с описанием снов
- 🤖 Интерпретация снов с помощью GPT-4
- 🎯 Понятные и глубокие толкования
- 💬 Уточняющие вопросы и диалог
- 📖 История снов с предпросмотром
- 📊 Статистика использования
- 🔄 Лимит 20 снов в месяц

## Технические требования

- Python 3.8 или выше
- Telegram Bot Token (получить у [@BotFather](https://t.me/botfather))
- OpenAI API ключ
- FastAPI для аналитической панели (опционально)

## Установка

1. Клонируйте репозиторий:
```bash
git clone git@github.com:gotemapak/dream_bot_project.git
cd dream_bot_project
```

2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` и добавьте необходимые переменные окружения:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
DASHBOARD_TOKEN=your_dashboard_token
```

## Запуск бота

1. Убедитесь, что виртуальное окружение активировано
2. Запустите бота:
```bash
python bot.py
```

## Использование

1. Начните чат с ботом в Telegram
2. Отправьте `/start` для получения приветственного сообщения
3. Отправьте свой сон одним из способов:
   - Текстовым сообщением
   - Голосовым сообщением
4. Дождитесь интерпретации
5. Используйте кнопки меню для:
   - Просмотра истории снов
   - Получения статистики
   - Задания уточняющих вопросов

## Аналитическая панель

Для запуска панели аналитики:
```bash
python dashboard.py
```
Панель будет доступна по адресу: `http://localhost:8000?token=your_dashboard_token`

## Обработка ошибок

Бот включает обработку:
- Проблем с обработкой голосовых сообщений
- Ошибок API
- Проблем с подключением
- Превышения месячного лимита

## Лицензия

Этот проект лицензирован под MIT License - подробности в файле [LICENSE](LICENSE). 