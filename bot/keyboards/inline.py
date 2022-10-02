from aiogram import types
from ..database.classes.customer import Customer
from ..misc.utils.cities import get_cities
from bot.misc.bot import bot

async def account_markup(user_id: int) -> types.InlineKeyboardMarkup | None:
    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
            [
                types.InlineKeyboardButton(text = "Редагування", callback_data = "edit_account"),
                types.InlineKeyboardButton(text = "Видалити акаунт", callback_data = "delete_account")
            ]
        ]
    )
    customer = await Customer.get(user_id)
    if customer:
        # if customer['activated']:
        keyboard_markup.inline_keyboard[0].append(types.InlineKeyboardButton(text = "Тривога", callback_data = "alarm"))
        # else:
        #     keyboard_markup.inline_keyboard[0].append(types.InlineKeyboardButton(text = "Отримати доступ до Охорони", callback_data = "get_guard_acces"))
    return keyboard_markup


def get_cities_markup():
    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
        [types.InlineKeyboardButton(text = city, callback_data = city) for city in get_cities()]
    ])
    return keyboard_markup


async def close_alarm(user_id: int):
    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = [
        [
            types.InlineKeyboardButton(text = f"Залишити відгук", callback_data = "leave_respond"),
        ]
    ])
    await bot.send_message(chat_id = user_id, text = 'Тепер ви можете залишити відгук:', reply_markup = keyboard_markup)