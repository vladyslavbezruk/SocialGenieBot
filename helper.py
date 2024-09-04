from aiogram import Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup



async def answer_delete(bot: Bot, callback_query: CallbackQuery, message_text: str):
    await bot.send_message(callback_query.from_user.id, message_text)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)


def create_keyboard(buttons: list):
    """

    :param buttons: A list of tuples where each tuple contains the button text and callback data.
    :return: InlineKeyboardMarkup object.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=callback_data)]
            for text, callback_data in buttons
        ]
    )
    return keyboard