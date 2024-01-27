# Blackjack Telegram Bot

Простой телеграмм-бот для игры в блек-джек, реализованный на Python с использованием библиотеки Telebot.

## Начало работы

Чтобы начать, следуйте инструкциям ниже:

### Предварительные требования

Убедитесь, что у вас установлен Python на вашем компьютере. Вы можете загрузить его с [python.org](https://www.python.org/downloads/).

### Установка

1. Клонируйте репозиторий на свой локальный компьютер:

    ```
    git clone https://github.com/your_username/blackjack-telegram-bot.git
    ```
2. Перейдите в каталог проекта:

    ```
   cd blackjack-telegram-bot
   ```
3. Установите необходимые пакеты Python:

   ```
   pip install -r requirements.txt
   ```
### Использование

Создайте телеграмм-бота и получите токен от BotFather.

Создайте переменную TOKEN в файле .env, и замените значение на ваш актуальный токен бота.

Запустите бота:

```
python bot.py
```
Начните игру, набрав /game в чате Telegram.

### Возможности

Выбор между европейским блек-джеком.
Выбор количества колод для игры (1, 2, 4, 6).
Интерактивные команды игры с использованием пользовательской клавиатуры.
Поддержка взятия дополнительных карт или остановки во время хода игрока.
Автоматическое выполнение хода дилера.
Определение победителя и объявление результатов.
### Содействие

Не стесняйтесь вносить свой вклад в проект. Вы можете открывать проблемы для сообщений об ошибках или отправлять запросы на объединение для улучшений.

### Лицензия

Этот проект лицензирован по лицензии MIT - подробности см. в файле LICENSE.
