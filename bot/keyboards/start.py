from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_keyboard(items: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for item in items:
        builder.button(text=item, callback_data=str(item))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


start_cmds = ["Готов", "Ну нахер"]