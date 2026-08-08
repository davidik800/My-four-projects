# main.py
# Блок 1/5 — импорт, настройки, БД, состояния и базовые утилиты

import asyncio
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple

from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    FSInputFile,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# =========================
# НАСТРОЙКИ
# =========================

TOKEN = "YOUR_TOKEN_HERE"
ADMIN_ID = YOUR_ADMIN_ID # <-- сюда свой Telegram ID

DB_PATH = "applications.db"
UPLOADS_DIR = Path("uploads")

# =========================
# ЛОГИРОВАНИЕ
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("master_na_dom_bot")

# =========================
# БАЗА ДАННЫХ
# =========================

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Создаёт таблицу applications, если её ещё нет."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            full_name TEXT,
            service TEXT NOT NULL,
            description TEXT NOT NULL,
            photo_file_id TEXT,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Новая',
            created_at TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def create_application(
    user_id: int,
    username: Optional[str],
    full_name: str,
    service: str,
    description: str,
    photo_file_id: Optional[str],
    address: str,
    phone: str,
    time_text: str,
) -> int:
    """Сохраняет заявку в БД и возвращает её ID."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO applications (
            user_id, username, full_name, service, description,
            photo_file_id, address, phone, time, status, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Новая', ?)
        """,
        (
            user_id,
            username,
            full_name,
            service,
            description,
            photo_file_id,
            address,
            phone,
            time_text,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    app_id = cur.lastrowid
    conn.commit()
    conn.close()
    return app_id


def get_applications_by_user(user_id: int) -> List[sqlite3.Row]:
    """Возвращает все заявки пользователя, от новых к старым."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT * FROM applications
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_all_applications() -> List[sqlite3.Row]:
    """Возвращает все заявки для админки."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT * FROM applications
        ORDER BY id DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_application_by_id(app_id: int) -> Optional[sqlite3.Row]:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
    row = cur.fetchone()
    conn.close()
    return row


def update_application_status(app_id: int, status: str) -> bool:
    """Обновляет статус заявки. True, если строка найдена."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE applications SET status = ? WHERE id = ?",
        (status, app_id),
    )

    updated = cur.rowcount > 0
    conn.commit()
    conn.close()
    return updated


# =========================
# СОЗДАНИЕ ПАПКИ ДЛЯ ФОТО
# =========================

UPLOADS_DIR.mkdir(exist_ok=True)

# =========================
# СОСТОЯНИЯ FSM
# =========================

class ApplicationForm(StatesGroup):
    service = State()
    description = State()
    photo = State()
    address = State()
    phone = State()
    time = State()


# =========================
# КОНСТАНТЫ
# =========================

SERVICE_LABELS = {
    "plumber": "Сантехник",
    "electrician": "Электрик",
    "repair": "Ремонт",
}

STATUS_LABELS = {
    "Новая": "Новая",
    "В работе": "В работе",
    "Выполнена": "Выполнена",
}

STATUS_ORDER = ["Новая", "В работе", "Выполнена"]

# =========================
# КЛАВИАТУРЫ
# =========================

def main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Оставить заявку")
    builder.button(text="Мои заявки")
    builder.button(text="Прайс")
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)


def services_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Сантехник", callback_data="service:plumber")
    builder.button(text="Электрик", callback_data="service:electrician")
    builder.button(text="Ремонт", callback_data="service:repair")
    builder.adjust(1)
    return builder.as_markup()


def yes_no_photo_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Отправлю фото", callback_data="photo:yes")
    builder.button(text="Пропустить", callback_data="photo:no")
    builder.adjust(1)
    return builder.as_markup()


def admin_status_kb(app_id: int, current_status: str) -> InlineKeyboardMarkup:
    """Кнопки смены статуса заявки в админке."""
    builder = InlineKeyboardBuilder()

    for status in STATUS_ORDER:
        if status != current_status:
            builder.button(
                text=f"Сделать: {status}",
                callback_data=f"admin_status:{app_id}:{status}",
            )

    builder.adjust(1)
    return builder.as_markup()


def my_app_status_kb(app_id: int, status: str) -> InlineKeyboardMarkup:
    """Кнопка-подсказка для заявки пользователя."""
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Статус: {status}", callback_data=f"noop:{app_id}")
    return builder.as_markup()


# =========================
# УТИЛИТЫ
# =========================

def normalize_phone(raw: str) -> str:
    """Очень мягкая нормализация телефона, без жёсткой валидации."""
    text = raw.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if text.startswith("8") and len(text) >= 11:
        return "+7" + text[1:] # мягкий вариант для RU-номеров
    return text


def build_application_text(row: sqlite3.Row) -> str:
    """Формирует красивый текст заявки."""
    photo_text = "Есть фото" if row["photo_file_id"] else "Без фото"
    return (
        f"<b>Заявка №{row['id']}</b>\n"
        f"<b>Услуга:</b> {row['service']}\n"
        f"<b>Описание:</b> {row['description']}\n"
        f"<b>Фото:</b> {photo_text}\n"
        f"<b>Адрес:</b> {row['address']}\n"
        f"<b>Телефон:</b> {row['phone']}\n"
        f"<b>Время:</b> {row['time']}\n"
        f"<b>Статус:</b> {row['status']}\n"
        f"<b>Создано:</b> {row['created_at']}"
    )


def build_admin_application_text(row: sqlite3.Row) -> str:
    username = f"@{row['username']}" if row["username"] else "нет username"
    return (
        f"<b>НОВАЯ ЗАЯВКА №{row['id']}</b>\n"
        f"<b>Пользователь:</b> {row['full_name']} ({username})\n"
        f"<b>User ID:</b> <code>{row['user_id']}</code>\n"
        f"<b>Услуга:</b> {row['service']}\n"
        f"<b>Описание:</b> {row['description']}\n"
        f"<b>Адрес:</b> {row['address']}\n"
        f"<b>Телефон:</b> {row['phone']}\n"
        f"<b>Время:</b> {row['time']}\n"
        f"<b>Статус:</b> {row['status']}\n"
        f"<b>Создано:</b> {row['created_at']}"
    )


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# =========================
# BOT / DISPATCHER
# =========================

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# =========================
# ДАЛЕЕ БУДУТ:
# 2/5 — /start, меню, начало заявки
# 3/5 — шаги заявки по FSM
# 4/5 — отправка в админку и "Мои заявки"
# 5/5 — /admin, смена статусов, запуск
# =========================
# Блок 2/5 — /start, главное меню и запуск оформления заявки

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Приветствие и главное меню."""
    text = (
        "Здравствуйте! Это <b>МастерНаДом Бот</b>.\n\n"
        "Здесь можно быстро оставить заявку на услуги:\n"
        "• сантехник\n"
        "• электрик\n"
        "• ремонт\n\n"
        "Выберите действие в меню ниже."
    )
    await message.answer(text, reply_markup=main_menu_kb())


@router.message(F.text == "Прайс")
async def show_price(message: Message) -> None:
    """Показывает примерный прайс."""
    text = (
        "<b>Прайс</b>\n\n"
        "Сантехник — от 500 ₽\n"
        "Электрик — от 500 ₽\n"
        "Ремонт — от 1000 ₽\n\n"
        "Точная стоимость зависит от объёма работ, адреса и срочности."
    )
    await message.answer(text, reply_markup=main_menu_kb())


@router.message(F.text == "Оставить заявку")
async def start_application(message: Message, state: FSMContext) -> None:
    """Запуск пошагового оформления заявки."""
    await state.clear()
    await state.set_state(ApplicationForm.service)

    text = (
        "Шаг 1 из 6.\n"
        "Выберите нужную услугу:"
    )
    await message.answer(text, reply_markup=services_kb())


@router.callback_query(F.data.startswith("service:"))
async def choose_service(callback: CallbackQuery, state: FSMContext) -> None:
    """Сохраняет выбранную услугу и переходит к описанию проблемы."""
    service_key = callback.data.split(":", 1)[1]
    service_name = SERVICE_LABELS.get(service_key)

    if not service_name:
        await callback.answer("Неизвестная услуга", show_alert=True)
        return

    await state.update_data(service=service_name)
    await state.set_state(ApplicationForm.description)

    await callback.message.edit_text(
        f"Вы выбрали: <b>{service_name}</b>\n\n"
        "Шаг 2 из 6.\n"
        "Опишите проблему как можно подробнее."
    )
    await callback.answer()


@router.message(F.text == "Мои заявки")
async def show_my_applications(message: Message) -> None:
    """Показывает список заявок пользователя."""
    rows = get_applications_by_user(message.from_user.id)

    if not rows:
        await message.answer(
            "У вас пока нет заявок.",
            reply_markup=main_menu_kb(),
        )
        return

    parts = ["<b>Ваши заявки:</b>\n"]
    for row in rows:
        parts.append(
            f"№{row['id']} — {row['service']} — <b>{row['status']}</b>\n"
            f"{row['created_at']}"
        )

    await message.answer("\n\n".join(parts), reply_markup=main_menu_kb())


@router.callback_query(F.data.startswith("noop:"))
async def noop_callback(callback: CallbackQuery) -> None:
    """Пустая кнопка-заглушка."""
    await callback.answer()


@router.message(Command("cancel"))
async def cancel_flow(message: Message, state: FSMContext) -> None:
    """Отмена текущего оформления заявки."""
    await state.clear()
    await message.answer("Оформление заявки отменено.", reply_markup=main_menu_kb())
# Блок 3/5 — пошаговое оформление заявки: описание, фото, адрес, телефон, время

@router.message(ApplicationForm.description)
async def process_description(message: Message, state: FSMContext) -> None:
    """Сохраняет описание проблемы и запрашивает фото."""
    text = message.text.strip() if message.text else ""
    if len(text) < 5:
        await message.answer("Описание слишком короткое. Напишите подробнее, что случилось.")
        return

    await state.update_data(description=text)
    await state.set_state(ApplicationForm.photo)

    await message.answer(
        "Шаг 3 из 6.\n"
        "Отправьте фото проблемы или нажмите «Пропустить».",
        reply_markup=yes_no_photo_kb(),
    )


@router.callback_query(F.data == "photo:yes")
async def ask_photo_from_button(callback: CallbackQuery) -> None:
    """Подсказка после нажатия кнопки отправки фото."""
    await callback.answer()
    await callback.message.answer("Пожалуйста, отправьте фото одним сообщением.")


@router.callback_query(F.data == "photo:no")
async def skip_photo(callback: CallbackQuery, state: FSMContext) -> None:
    """Пропускает фото и переходит к адресу."""
    await state.update_data(photo_file_id=None)
    await state.set_state(ApplicationForm.address)

    await callback.message.edit_text(
        "Фото пропущено.\n\n"
        "Шаг 4 из 6.\n"
        "Напишите адрес, где нужно выполнить работу."
    )
    await callback.answer()


@router.message(ApplicationForm.photo, F.photo)
async def process_photo(message: Message, state: FSMContext) -> None:
    """Сохраняет file_id фото и переходит к адресу."""
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo_file_id=photo_file_id)
    await state.set_state(ApplicationForm.address)

    await message.answer(
        "Фото получено.\n\n"
        "Шаг 4 из 6.\n"
        "Напишите адрес, где нужно выполнить работу."
    )


@router.message(ApplicationForm.photo)
async def invalid_photo_step(message: Message) -> None:
    """Если в шаге фото пришёл не снимок и не кнопка."""
    await message.answer(
        "На этом шаге нужно отправить фото или нажать «Пропустить»."
    )


@router.message(ApplicationForm.address)
async def process_address(message: Message, state: FSMContext) -> None:
    """Сохраняет адрес и запрашивает телефон."""
    text = message.text.strip() if message.text else ""
    if len(text) < 5:
        await message.answer("Адрес слишком короткий. Напишите полный адрес.")
        return

    await state.update_data(address=text)
    await state.set_state(ApplicationForm.phone)

    await message.answer(
        "Шаг 5 из 6.\n"
        "Отправьте номер телефона для связи."
    )


@router.message(ApplicationForm.phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    """Сохраняет телефон и запрашивает удобное время."""
    text = message.text.strip() if message.text else ""
    phone = normalize_phone(text)

    if len(phone) < 8:
        await message.answer("Телефон выглядит некорректно. Введите номер ещё раз.")
        return

    await state.update_data(phone=phone)
    await state.set_state(ApplicationForm.time)

    await message.answer(
        "Шаг 6 из 6.\n"
        "Напишите удобное время для визита мастера.\n"
        "Например: сегодня после 18:00 или завтра в 10:30."
    )


@router.message(ApplicationForm.time)
async def process_time(message: Message, state: FSMContext) -> None:
    """Завершает сбор данных и создаёт заявку."""
    text = message.text.strip() if message.text else ""
    if len(text) < 3:
        await message.answer("Укажите удобное время более понятно.")
        return

    await state.update_data(time=text)

    data = await state.get_data()

    service = data.get("service", "")
    description = data.get("description", "")
    photo_file_id = data.get("photo_file_id")
    address = data.get("address", "")
    phone = data.get("phone", "")
    time_text = data.get("time", "")

    app_id = create_application(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        service=service,
        description=description,
        photo_file_id=photo_file_id,
        address=address,
        phone=phone,
        time_text=time_text,
    )

    await state.clear()

    await message.answer(
        f"Спасибо! Ваша заявка <b>№{app_id}</b> принята.\n"
        f"Статус: <b>Новая</b>",
        reply_markup=main_menu_kb(),
    )
# Блок 4/5 — админ-уведомления, /admin, список заявок и смена статусов

async def notify_admin_new_application(app_id: int) -> None:
    """
    Отправляет администратору уведомление о новой заявке.
    Вызывается автоматически после создания заявки.
    """
    row = get_application_by_id(app_id)
    if not row:
        return

    text = build_admin_application_text(row)

    # Если есть фото — отправим его отдельным сообщением, чтобы не терять наглядность.
    if row["photo_file_id"]:
        try:
            await bot.send_photo(
                chat_id=ADMIN_ID,
                photo=row["photo_file_id"],
                caption=(
                    f"<b>НОВАЯ ЗАЯВКА №{row['id']}</b>\n"
                    f"<b>Фото:</b> прикреплено к сообщению ниже"
                ),
            )
        except Exception as e:
            logger.warning("Не удалось отправить фото админу: %s", e)

    await bot.send_message(
        chat_id=ADMIN_ID,
        text=text,
        reply_markup=admin_status_kb(row["id"], row["status"]),
    )


# ВАЖНО:
# Эта функция переопределяет предыдущую create_application из блока 1.
# Благодаря этому блок 3 автоматически начнёт вызывать версию с уведомлением админу.
def create_application(
    user_id: int,
    username: Optional[str],
    full_name: str,
    service: str,
    description: str,
    photo_file_id: Optional[str],
    address: str,
    phone: str,
    time_text: str,
) -> int:
    """Сохраняет заявку в БД, а затем уведомляет администратора."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO applications (
            user_id, username, full_name, service, description,
            photo_file_id, address, phone, time, status, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Новая', ?)
        """,
        (
            user_id,
            username,
            full_name,
            service,
            description,
            photo_file_id,
            address,
            phone,
            time_text,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    app_id = cur.lastrowid
    conn.commit()
    conn.close()

    # Асинхронное уведомление админу, не блокируя пользователя.
    try:
        asyncio.create_task(notify_admin_new_application(app_id))
    except RuntimeError:
        # На случай, если задача создаётся вне работающего event loop.
        logger.warning("Не удалось создать задачу уведомления админу для заявки №%s", app_id)

    return app_id


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    """Админ-панель: показывает все заявки."""
    if not is_admin(message.from_user.id):
        await message.answer("Доступ запрещён.")
        return

    rows = get_all_applications()

    if not rows:
        await message.answer("Заявок пока нет.")
        return

    await message.answer(f"<b>Админ-панель</b>\nВсего заявок: {len(rows)}")

    for row in rows:
        text = build_admin_application_text(row)
        await message.answer(
            text,
            reply_markup=admin_status_kb(row["id"], row["status"]),
        )


@router.callback_query(F.data.startswith("admin_status:"))
async def admin_change_status(callback: CallbackQuery) -> None:
    """Меняет статус заявки из админки."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён", show_alert=True)
        return

    try:
        _, app_id_str, new_status = callback.data.split(":", 2)
        app_id = int(app_id_str)
    except Exception:
        await callback.answer("Некорректные данные", show_alert=True)
        return

    if new_status not in STATUS_ORDER:
        await callback.answer("Недопустимый статус", show_alert=True)
        return

    updated = update_application_status(app_id, new_status)
    if not updated:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    row = get_application_by_id(app_id)
    if not row:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    try:
        await callback.message.edit_text(
            build_admin_application_text(row),
            reply_markup=admin_status_kb(row["id"], row["status"]),
        )
    except Exception:
        # Если сообщение уже нельзя редактировать — просто отвечаем без ошибки.
        pass

    await callback.answer(f"Статус изменён на: {new_status}")


@router.message(Command("help"))
async def help_cmd(message: Message) -> None:
    """Короткая справка по командам."""
    text = (
        "<b>Доступные команды</b>\n"
        "/start — главное меню\n"
        "/admin — админ-панель (только для администратора)\n"
        "/cancel — отменить оформление заявки"
    )
    await message.answer(text, reply_markup=main_menu_kb())
# Блок 5/5 — запуск бота, инициализация БД и точка входа

@router.message()
async def fallback_handler(message: Message) -> None:
    """
    Универсальный обработчик на случай неизвестного текста.
    Не мешает шагам FSM, потому что обработчики состояний стоят выше.
    """
    await message.answer(
        "Я не понял команду.\n"
        "Используйте меню ниже или /start.",
        reply_markup=main_menu_kb(),
    )


async def on_startup() -> None:
    """Действия при запуске."""
    init_db()
    logger.info("База данных инициализирована.")
    logger.info("Бот запущен как: МастерНаДом Бот")


async def main() -> None:
    """Главная функция запуска."""
    await on_startup()

    # Убираем старый webhook, если он был, чтобы polling работал стабильно.
    await bot.delete_webhook(drop_pending_updates=True)

    # Запуск long polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен вручную.")
