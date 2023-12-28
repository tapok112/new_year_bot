import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from bot.config_reader import conf
from bot.handlers.fsm.question_fcm import question_router


async def main():
    bot = Bot(token=conf.bot.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(question_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())