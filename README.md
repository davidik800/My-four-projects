🏠 МастерНаДом Бот

«🚀 Telegram-бот для быстрого приёма и управления заявками на бытовые услуги»

МастерНаДом Бот — это универсальный Telegram-бот для сервисов, которые принимают заявки клиентов на выездные бытовые услуги.

Бот позволяет клиенту оформить заявку всего за несколько шагов, указав необходимую услугу, описание проблемы, фотографию, адрес, номер телефона и удобное время.

Все заявки автоматически сохраняются в базе данных и передаются администратору для дальнейшей обработки. ⚡

---

✨ Возможности

👤 Для клиента

- 🏠 Главное меню
- 🛠️ Выбор услуги:
  - 🔧 Сантехник
  - ⚡ Электрик
  - 🧰 Ремонт
- 📝 Подробное описание проблемы
- 📸 Возможность прикрепить фотографию
- 📍 Указание адреса
- 📞 Указание номера телефона
- 🕐 Выбор удобного времени
- 📋 Просмотр своих заявок
- 📊 Просмотр текущего статуса заявки
- ❌ Отмена оформления заявки

👨‍💼 Для администратора

- 🔐 Защищённая административная панель
- 📋 Просмотр всех заявок
- 🔔 Автоматическое уведомление о новой заявке
- 👤 Информация о клиенте
- 📸 Получение фотографии заявки
- 📍 Адрес клиента
- 📞 Контактный телефон
- 🕐 Удобное время визита
- 🔄 Изменение статуса заявки

📊 Статусы заявок

Каждая заявка может находиться в одном из трёх состояний:

🆕 Новая
🔧 В работе
✅ Выполнена

---

🧩 Как работает бот

👤 Клиент
    │
    ▼
🚀 /start
    │
    ▼
🛠️ Выбор услуги
    │
    ▼
📝 Описание проблемы
    │
    ▼
📸 Фото
    │
    ▼
📍 Адрес
    │
    ▼
📞 Телефон
    │
    ▼
🕐 Удобное время
    │
    ▼
📋 Создание заявки
    │
    ├──────────────► 💾 SQLite
    │
    ▼
👨‍💼 Администратор
    │
    ▼
🔄 Управление статусом

---

🛠️ Технологии

- 🐍 Python
- 🤖 aiogram 3
- 🗄️ SQLite
- 🔄 FSM (Finite State Machine)
- 📡 Telegram Bot API
- 💾 SQLite database

---

📁 Структура проекта

Проект специально сделан максимально простым для запуска:

📦 master-na-dom-bot
│
├── 🐍 main.py
├── 🗄️ applications.db
├── 📁 uploads/
└── 📄 README.md

Основная логика бота находится в одном файле:

main.py

---

🚀 Установка

1. Клонировать репозиторий

git clone <YOUR_REPOSITORY_URL>
cd master-na-dom-bot

2. Установить зависимости

pip install aiogram

3. Настроить бота

Откройте:

main.py

и укажите:

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 123456789

4. Запустить

python main.py

После запуска бот начинает принимать заявки через Telegram. 🚀

---

🔐 Безопасность

Административные функции доступны только пользователю, чей Telegram ID указан в:

ADMIN_ID

Токен Telegram-бота является секретным значением и не должен публиковаться в открытом репозитории.

---

💾 База данных

Для хранения заявок используется SQLite.

Основная таблица:

applications

В ней хранятся:

- 🆔 ID заявки
- 👤 ID пользователя
- 🔹 Username
- 👤 Имя клиента
- 🛠️ Услуга
- 📝 Описание
- 📸 Фото
- 📍 Адрес
- 📞 Телефон
- 🕐 Удобное время
- 📊 Статус
- 📅 Дата создания

---

🎯 Назначение

Бот подходит для:

- 🔧 сервисов бытовых услуг;
- 🏠 выездных мастеров;
- ⚡ электриков;
- 🚰 сантехнических служб;
- 🧰 ремонтных компаний;
- 🛠️ небольших сервисных организаций;
- 📋 любых проектов, которым необходимо принимать заявки через Telegram.

---

⚡ Основная идея

Минимум действий со стороны клиента → максимум информации для исполнителя.

Клиенту не нужно звонить, искать менеджера или заполнять длинные формы.

Он просто открывает Telegram, отвечает на несколько вопросов — и заявка отправляется исполнителю. 🚀

---

🏠 MasterNaDom Bot

«🚀 A Telegram bot for fast service request submission and management»

MasterNaDom Bot is a universal Telegram bot for services that accept customer requests for on-site household services.

The bot allows customers to create a request in just a few steps by selecting a service, describing the problem, attaching a photo, providing an address, phone number, and preferred visit time.

All requests are automatically stored in the database and sent to the administrator for further processing. ⚡

---

✨ Features

👤 For customers

- 🏠 Main menu
- 🛠️ Service selection:
  - 🔧 Plumber
  - ⚡ Electrician
  - 🧰 Repair
- 📝 Detailed problem description
- 📸 Ability to attach a photo
- 📍 Address submission
- 📞 Phone number submission
- 🕐 Preferred visit time
- 📋 View personal requests
- 📊 View current request status
- ❌ Cancel request creation

👨‍💼 For administrators

- 🔐 Protected administrator panel
- 📋 View all requests
- 🔔 Automatic notification about new requests
- 👤 Customer information
- 📸 Request photo
- 📍 Customer address
- 📞 Contact phone number
- 🕐 Preferred visit time
- 🔄 Request status management

📊 Request statuses

Each request can have one of three statuses:

🆕 New
🔧 In Progress
✅ Completed

---

🧩 How the bot works

👤 Customer
    │
    ▼
🚀 /start
    │
    ▼
🛠️ Service selection
    │
    ▼
📝 Problem description
    │
    ▼
📸 Photo
    │
    ▼
📍 Address
    │
    ▼
📞 Phone
    │
    ▼
🕐 Preferred time
    │
    ▼
📋 Request creation
    │
    ├──────────────► 💾 SQLite
    │
    ▼
👨‍💼 Administrator
    │
    ▼
🔄 Status management

---

🛠️ Technologies

- 🐍 Python
- 🤖 aiogram 3
- 🗄️ SQLite
- 🔄 FSM (Finite State Machine)
- 📡 Telegram Bot API
- 💾 SQLite database

---

📁 Project structure

The project is intentionally kept simple to run:

📦 master-na-dom-bot
│
├── 🐍 main.py
├── 🗄️ applications.db
├── 📁 uploads/
└── 📄 README.md

The main bot logic is contained in a single file:

main.py

---

🚀 Installation

1. Clone the repository

git clone <YOUR_REPOSITORY_URL>
cd master-na-dom-bot

2. Install dependencies

pip install aiogram

3. Configure the bot

Open:

main.py

and specify:

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 123456789

4. Run

python main.py

After launching, the bot starts accepting requests through Telegram. 🚀

---

🔐 Security

Administrative functions are available only to the user whose Telegram ID is specified in:

ADMIN_ID

The Telegram bot token is a secret value and must not be published in a public repository.

---

💾 Database

The bot uses SQLite for request storage.

Main table:

applications

It stores:

- 🆔 Request ID
- 👤 User ID
- 🔹 Username
- 👤 Customer name
- 🛠️ Service
- 📝 Description
- 📸 Photo
- 📍 Address
- 📞 Phone number
- 🕐 Preferred time
- 📊 Status
- 📅 Creation date

---

🎯 Purpose

The bot is suitable for:

- 🔧 household service companies;
- 🏠 on-site technicians;
- ⚡ electricians;
- 🚰 plumbing services;
- 🧰 repair companies;
- 🛠️ small service businesses;
- 📋 any project that needs to accept customer requests through Telegram.

---

⚡ Core idea

Minimum actions for the customer → maximum information for the service provider.

The customer does not need to make a phone call, search for a manager, or fill out a long form.

They simply open Telegram, answer a few questions, and the request is sent to the service provider. 🚀

---

📜 License

This project can be used, modified, and adapted for personal or commercial projects.

⭐ If you find the project useful, consider giving the repository a star.

🚀 MasterNaDom Bot — from customer request to completed service
