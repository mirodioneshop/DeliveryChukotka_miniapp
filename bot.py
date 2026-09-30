import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8875398364:AAHF1LudhGumAycjkNk3CW9BTAiltFr74TU"
ADMIN_CHAT_ID = 6464412618
MANAGER_USERNAME = "mirodione"

# 🌐 Ссылка на ваше Mini App на GitHub Pages:
WEB_APP_URL = "https://mirodioneshop.github.io/DeliveryChukotka_miniapp/"
# =============================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)


# Состояния анкеты
class CargoForm(StatesGroup):
    destination = State()      # Населенный пункт
    shipping_service = State() # Выбор ТК / Маркетплейса
    item_count = State()       # Количество товаров
    sender_contact = State()   # Контакт отправителя
    recipient_info = State()   # ФИО и номер получателя
    confirm = State()          # Подтверждение заявки


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Перезапустить бота / Главное меню"),
    ]
    await bot.set_my_commands(commands)


# Главное меню бота
def get_main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📦 Оформить в чате"),
                KeyboardButton(text="📱 Онлайн форма", web_app=WebAppInfo(url=WEB_APP_URL)),
            ],
            [
                KeyboardButton(text="📍 Адреса ПВЗ"),
                KeyboardButton(text="❓ Частые вопросы (FAQ)"),
            ],
            [
                KeyboardButton(text="💰 Примерный прайс-лист"),
                KeyboardButton(text="🚫 Запрещённые грузы"),
            ],
            [
                KeyboardButton(text="👨‍💻 Написать в личку"),
                KeyboardButton(text="📲 Поделиться ботом"),
            ],
        ],
        resize_keyboard=True,
    )


def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отменить оформление")]],
        resize_keyboard=True,
    )


def get_confirm_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Всё верно, отправить")],
            [KeyboardButton(text="✏️ Заполнить заново"), KeyboardButton(text="❌ Отменить оформление")],
        ],
        resize_keyboard=True,
    )


def get_shipping_service_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="АВИТО\n(любой населенный пункт)"),
                KeyboardButton(text="ВБ\n(только до Анадыря)"),
            ],
            [
                KeyboardButton(text="ОЗОН\n(Анадырь, Угольные Копи, Певек)"),
                KeyboardButton(text="ПОЧТА РОССИИ\n(любой населенный пункт)"),
            ],
            [KeyboardButton(text="Другое")],
            [KeyboardButton(text="❌ Отменить оформление")],
        ],
        resize_keyboard=True,
    )


def get_phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить мой номер телефона", request_contact=True)],
            [KeyboardButton(text="❌ Отменить оформление")],
        ],
        resize_keyboard=True,
    )


def get_manager_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Написать в личку", url=f"https://t.me/{MANAGER_USERNAME}")]
        ]
    )


def get_share_inline_keyboard():
    share_text = "Быстрая доставка товаров и посылок из Санкт-Петербурга на Чукотку 🏔️📦"
    share_url = f"https://t.me/share/url?url=https://t.me/DeliveryChukotka_bot&text={share_text}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📲 Отправить другу в Telegram", url=share_url)]
        ]
    )


@router.message(F.text == "❌ Отменить оформление")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
    await message.answer(
        "Оформление заявки отменено.",
        reply_markup=get_main_menu_keyboard(),
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Здравствуйте! Я бот для приёма заявок на доставку товаров из Санкт-Петербурга на Чукотку.\n\n"
        "Выберите нужное действие в меню ниже 👇",
        reply_markup=get_main_menu_keyboard(),
    )


@router.message(F.text == "📍 Адреса ПВЗ")
async def show_pvz_addresses(message: Message):
    text = (
        "📍 **Адреса пунктов выдачи заказов (ПВЗ) для оформления доставки:**\n\n"
        "🟣 **Wildberries:** Мурино, Проспект Авиаторов Балтики 15 \n"
        "🔵 **Ozon:** Мурино, пр-кт Авиаторов Балтики, 13 \n"
        "🟢 **СДЭК:** Мурино, Петровский бульвар 7 \n"
        "🟡 **Яндекс Маркет:** Мурино, Петровский бульвар 2, корпус 2 \n"
        "🔴 **Lamoda:** Мурино, Петровский бульвар 6, корпус 2 \n\n"
        "📌 *Заказы и посылки можно оформлять или направлять на любой из указанных пунктов.*"
    )
    await message.answer(text, parse_mode="Markdown")


# Кнопка: ❓ Частые вопросы (FAQ)
@router.message(F.text == "❓ Частые вопросы (FAQ)")
async def show_faq(message: Message):
    text = (
        "❓ **ЧАСТЫЕ ВОПРОСЫ И ОТВЕТЫ (FAQ):**\n\n"
        "⏱️ **Каковы сроки доставки в ваш населенный пункт?**\n"
        "Точно сказать нельзя сколько будет идти посылка/посылки, всё зависит от нагрузки сортировочных центров.\n\n"
        "💳 **Как происходит оплата?**\n"
        "После того как посылка будет собрана Вам пришлю реквизиты для оплаты, работа только по предоплате.\n\n"
        "📦 **Что делать если посылка крупногабаритная?**\n"
        "Крупногабаритные посылки и совсем маленькие посылки обсуждаются отдельно.\n\n"
        "📏 **Какие ограничения действуют по весу и габаритам?**\n"
        "• **Ozon:** до 35 кг, Максимальный размер: 200 см по большей стороне.\n"
        "• **Авито:** До 18 кг, максимальная длина одной стороны — до 120 см (при сумме трех сторон не более 2,5 м).\n"
        "• **Wildberries:** До 14 кг, 45 × 65 × 20 см.\n"
        "• **Почта России:** до 20 кг, сумма Д/Ш/В ≤ 220 см."
    )
    await message.answer(text, parse_mode="Markdown")


# Кнопка: 📲 Поделиться ботом
@router.message(F.text == "📲 Поделиться ботом")
async def share_bot_handler(message: Message):
    await message.answer(
        "Нажмите кнопку ниже, чтобы переслать ссылку на нашего бота своим друзьям и близким на Чукотке 👇",
        reply_markup=get_share_inline_keyboard(),
    )


@router.message(F.text == "👨‍💻 Написать в личку")
async def contact_manager(message: Message):
    await message.answer(
        "Если у вас возникли вопросы или требуется личная консультация, нажмите кнопку ниже для связи со мной:",
        reply_markup=get_manager_inline_keyboard(),
    )


@router.message(F.text == "💰 Примерный прайс-лист")
async def show_price_list(message: Message):
    text = (
        "💰 **Примерный прайс-лист на услуги:**\n\n"
        "• **Стоимость услуги:** 3 000 руб.\n\n"
        "📌 *Обратите внимание: маленькие товары, а также крупногабаритные товары оцениваются отдельно.*"
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(F.text == "🚫 Запрещённые грузы")
async def show_forbidden_cargo(message: Message):
    text = (
        "🚫 **Список грузов, запрещённых к перевозке:**\n\n"
        "❌ Взрывоопасные и легковоспламеняющиеся вещества (газовые баллоны, бензин, пиротехника)\n"
        "❌ Оружие, боеприпасы и спецсредства\n"
        "❌ Скоропортящиеся продукты питания\n"
        "❌ Ядовитые, едкие и радиоактивные вещества, кислоты\n"
        "❌ Наркотические и психотропные средства\n"
        "❌ Наличные деньги, драгоценности\n\n"
        "⚠️ *Если у вас есть сомнения, уточните возможность отправки у менеджера.*"
    )
    await message.answer(text, parse_mode="Markdown")


# --- ПОШАГОВЫЙ ОПРОС В ЧАТЕ ---

@router.message(F.text == "📦 Оформить в чате")
async def start_booking(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "✍️ **Шаг 1 из 5:** Укажите **населённый пункт** назначения (напишите текстом):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(CargoForm.destination)


@router.message(CargoForm.destination)
async def process_destination(message: Message, state: FSMContext):
    await state.update_data(destination=message.text)
    
    info_text = (
        "📦 **Шаг 2 из 5:** Через какую службу/маркетплейс отправляется посылка?\n\n"
        "ℹ️ **География доставки служб:**\n"
        "•  **Авито** и **Почта России** — отправка в *любой* населённый пункт Чукотки\n"
        "•  **Озон** — доставка до *Анадырь, Угольные Копи, Певек*\n"
        "•  **ВБ (Wildberries)** — доставка только в *Анадырь*"
    )
    
    await message.answer(
        info_text,
        reply_markup=get_shipping_service_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(CargoForm.shipping_service)


@router.message(CargoForm.shipping_service)
async def process_shipping_service(message: Message, state: FSMContext):
    clean_service = message.text.replace("\n", " ")
    await state.update_data(shipping_service=clean_service)
    
    await message.answer(
        "🔢 **Шаг 3 из 5:** Укажите **количество товаров / посылок** (например: *1 шт.*, *3 коробки*):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(CargoForm.item_count)


@router.message(CargoForm.item_count)
async def process_item_count(message: Message, state: FSMContext):
    await state.update_data(item_count=message.text)
    await message.answer(
        "📞 **Шаг 4 из 5:** Укажите ваши контактные данные (отправителя).\n"
        "Нажмите кнопку ниже, чтобы поделиться контактом, или впишите номер телефона вручную:",
        reply_markup=get_phone_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(CargoForm.sender_contact)


@router.message(CargoForm.sender_contact)
async def process_sender_contact(message: Message, state: FSMContext):
    if message.contact:
        sender_info = f"{message.contact.first_name} ({message.contact.phone_number})"
    else:
        sender_info = message.text

    await state.update_data(sender_contact=sender_info)
    
    await message.answer(
        "👤 **Шаг 5 из 5:** Укажите **ФИО и номер телефона ПОЛУЧАТЕЛЯ**:\n"
        "*(Например: Иванов Иван Иванович, +7 999 123-45-67)*",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(CargoForm.recipient_info)


@router.message(CargoForm.recipient_info)
async def process_recipient_info(message: Message, state: FSMContext):
    await state.update_data(recipient_info=message.text)
    user_data = await state.get_data()

    summary = (
        "📋 **ПРОВЕРЬТЕ ДАННЫЕ ЗАЯВКИ:**\n\n"
        f"📍 **Пункт назначения:** {user_data['destination']}\n"
        f"🚚 **Служба / Маркетплейс:** {user_data['shipping_service']}\n"
        f"🔢 **Количество товаров:** {user_data['item_count']}\n"
        f"📞 **Контакт отправителя:** {user_data['sender_contact']}\n"
        f"🎯 **Получатель:** {user_data['recipient_info']}\n\n"
        "Если всё указано верно, нажмите **«✅ Всё верно, отправить»**."
    )

    await message.answer(
        summary,
        reply_markup=get_confirm_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(CargoForm.confirm)


@router.message(CargoForm.confirm, F.text == "✅ Всё верно, отправить")
async def process_confirm_send(message: Message, state: FSMContext):
    user_data = await state.get_data()

    summary = (
        "📦 **НОВАЯ ЗАЯВКА НА ДОСТАВКУ (ИЗ ЧАТА)**\n\n"
        f"📍 **Пункт назначения:** {user_data['destination']}\n"
        f"🚚 **Служба / Маркетплейс:** {user_data['shipping_service']}\n"
        f"🔢 **Количество товаров:** {user_data['item_count']}\n"
        f"👤 **Заявитель (Отправитель):** @{message.from_user.username if message.from_user.username else 'без_username'}\n"
        f"📞 **Контакт отправителя:** {user_data['sender_contact']}\n"
        f"🎯 **Получатель:** {user_data['recipient_info']}"
    )

    try:
        await bot.send_message(ADMIN_CHAT_ID, summary, parse_mode="Markdown")
        await message.answer(
            "Спасибо! Заявка принята. Мы рассчитаем параметры доставки и свяжемся с вами в ближайшее время.",
            reply_markup=get_main_menu_keyboard(),
        )
    except Exception as e:
        logging.error(f"Ошибка отправки: {e}")
        await message.answer(
            "Спасибо! Заявка принята. Мы свяжемся с вами в ближайшее время.",
            reply_markup=get_main_menu_keyboard(),
        )

    await state.clear()


@router.message(CargoForm.confirm, F.text == "✏️ Заполнить заново")
async def process_confirm_restart(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Давайте заполним заявку заново.\n\n"
        "✍️ **Шаг 1 из 5:** Укажите **населённый пункт** назначения (напишите текстом):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(CargoForm.destination)


@router.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        data = json.loads(message.web_app_data.data)

        summary = (
            "📦 **НОВАЯ ЗАЯВКА (ИЗ МИНИ-ПРИЛОЖЕНИЯ)**\n\n"
            f"📍 **Пункт назначения:** {data.get('destination', 'Не указано')}\n"
            f"🚚 **Служба / Маркетплейс:** {data.get('service', 'Не указано')}\n"
            f"🔢 **Количество товаров:** {data.get('itemCount', 'Не указано')}\n"
            f"🔗 **Трек-номер / Ссылка:** {data.get('trackInfo', 'Не указано')}\n"
            f"👤 **Заявитель (Telegram):** @{message.from_user.username if message.from_user.username else 'без_username'}\n"
            f"📞 **Телефон отправителя:** {data.get('senderContact', 'Не указано')}\n"
            f"🎯 **Получатель:** {data.get('recipientInfo', 'Не указано')}"
        )

        await bot.send_message(ADMIN_CHAT_ID, summary, parse_mode="Markdown")

        await message.answer(
            "Спасибо! Заявка успешно принята. Мы рассчитаем параметры доставки и свяжемся с вами в ближайшее время.",
            reply_markup=get_main_menu_keyboard(),
        )
    except Exception as e:
        logging.error(f"Ошибка обработки Web App данных: {e}")
        await message.answer(
            "Произошла ошибка при отправке формы. Попробуйте ещё раз или свяжитесь с менеджером.",
            reply_markup=get_main_menu_keyboard(),
        )


@router.message()
async def echo_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(
            "Выберите нужное действие в меню ниже 👇",
            reply_markup=get_main_menu_keyboard(),
        )


async def main():
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())