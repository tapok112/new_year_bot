import json

from aiogram import F, Bot
from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup
from aiogram.types import Message, FSInputFile

from bot.config_reader import conf
from bot.keyboards.cancel import cancel_button, cancel_cmd
from bot.keyboards.questions import question_keyboard, question_cmds
from bot.keyboards.start import start_keyboard, start_cmds

question_router = Router()

with open("bot/questions.json", "r", encoding="utf-8") as file:
    questions_data = json.load(file)

class QuizStates(StatesGroup):
    start = State()
    first = State()
    second = State()
    complete = State()


@question_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(QuizStates.start)
    if message.from_user.username == "Valeriabori":
        await message.answer(
            "☃️☃️☃️☃️☃️\n"
            "\n"
            f"Привет, {message.from_user.first_name}!\n"
            "Дима подготовил для тебя небольшой квест, когда ты ответишь на несколько вопросов, тебе будет открыт доступ к локации твоего новогоднего подарка!🎁\n"
            "Если готова, нажми на кнопку внизу!\n"
            "Если хочешь перезапустить бота, или начать блиц заново, напиши /start"
            "\n"
            "🍬🍬🍬🍬🍬",
            reply_markup=start_keyboard(start_cmds)
        )
    else:
        await message.answer(
            "☃️☃️☃️☃️☃️\n"
            "\n"
            f"Привет, {message.from_user.first_name}!\n"
            "Маша и Дима подготовили для тебя небольшой квест, когда ты ответишь на несколько вопросов, тебе будет открыт доступ к локации твоего новогоднего подарка!🎁\n"
            "Если готов(а), нажми на кнопку внизу!\n"
            "Если хочешь перезапустить бота, или начать блиц заново, напиши /start"
            "\n"
            "🍬🍬🍬🍬🍬",
            reply_markup=start_keyboard(start_cmds)
        )


@question_router.callback_query(F.data.casefold() == "подсказка")
async def cmd_hint(callback: types.CallbackQuery, state: FSMContext):
        current_state = await state.get_state()
        hint = questions_data[callback.from_user.username]["questions"][current_state.split(":")[1]]["help"]

        if hint is None:
            await callback.message.answer(f"✖️Подсказки для этого шага отсутствуют")
        else:
            await callback.message.answer(
                "✅ Подсказка: \n"
                f"{hint}")

@question_router.callback_query(F.data.casefold() == "готов(а)")
async def process_start(callback: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await callback.message.edit_reply_markup()
    await state.set_state(QuizStates.first)
    await bot.send_message(chat_id=conf.bot.admin,
                           text=f"{callback.from_user.first_name} перешел на первый шаг")
    answer = await callback.message.answer(
        questions_data[callback.from_user.username]["questions"]["first"]["question"],
        reply_markup=question_keyboard(question_cmds)
    )
    await state.update_data(answer=answer)


@question_router.message(Command("cancel"))
@question_router.callback_query(F.data.casefold() == "ну нахер")
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await callback.message.edit_reply_markup()
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await bot.send_message(chat_id=conf.bot.admin,
                           text=f"{callback.from_user.first_name} прервал блиц с {current_state}")
    await callback.message.answer(
        "👾 Возвращаяйся! Ты можешь начать заново в любое время 👾"
    )


@question_router.message(QuizStates.first)
async def process_question1(message: Message, state: FSMContext, bot: Bot) -> None:
    user_data = await state.get_data()
    await user_data['answer'].edit_reply_markup()

    answers = questions_data[message.from_user.username]["questions"]["first"]["answer"]

    if not message.text.lower() in answers:
        await bot.send_message(chat_id=conf.bot.admin,
                               text=f"{message.from_user.first_name} ответил неверно на первом шаге")
        answer = await message.reply(
            "❌ Неправильно!\n"
            "Попробуй еще раз или нажми кнопку 'Подсказка'.",
            reply_markup=question_keyboard(question_cmds)
        )
        await state.update_data(answer=answer)
        return

    await state.set_state(QuizStates.second)
    await bot.send_message(chat_id=conf.bot.admin,
                           text=f"{message.from_user.first_name} перешел на второй шаг")
    answer = await message.answer(
        questions_data[message.from_user.username]["questions"]["second"]["question"],
        reply_markup=question_keyboard(question_cmds)
    )
    await state.update_data(answer=answer)


@question_router.message(QuizStates.second)
async def process_question2(message: Message, state: FSMContext, bot: Bot) -> None:
    user_data = await state.get_data()
    await user_data['answer'].edit_reply_markup()

    answers = questions_data[message.from_user.username]["questions"]["second"]["answer"]
    if message.text.lower() in answers:
        await state.set_state(QuizStates.complete)
        await bot.send_message(chat_id=conf.bot.admin,
                               text=f"{message.from_user.first_name} ответил верно на все вопросы")
        latitude = questions_data[message.from_user.username]["complete"]["latitude"]
        longitude = questions_data[message.from_user.username]["complete"]["longitude"]
        location = types.Location(latitude=latitude, longitude=longitude)

        try:
            code = questions_data[message.from_user.username]["complete"]["code"]
        except KeyError:
            code = None

        try:
            image = FSInputFile(questions_data[message.from_user.username]["complete"]["photo"])
        except KeyError:
            image = None

        if image:
            await message.answer(
                "🥳🥳🥳🥳🥳\n"
                "Успех, все вопросы пройдены. Ниже прикреплена локация, где лежит подарок."
            )
            await message.answer_location(location.latitude, location.longitude)
            await message.answer_photo(
                image,
                caption=f"Это QR-код для получения новогоднего подарка!"
            )
        else:
            await message.answer(
                "🥳🥳🥳🥳🥳\n"
                "Успех, все вопросы пройдены. Ниже прикреплена локация, где лежит подарок.\n"
                f"Твой код: {code}\n"
                "Тебя будет ждать дед мороз в красной футболке, поздоровайся с ним и скажи 'I need my present'\n"
                "P.S Дед мороз может напутать!\n"
                "Когда получишь пакетик, убедись, что на нем написан твой код."
            )
            await message.answer_location(location.latitude, location.longitude)


        answer = await message.answer(
            "📷📷📷📷📷\n"
            "Пришли свое довольное фото с подарком!",
            reply_markup=cancel_button(cancel_cmd)
        )
        await state.update_data(answer=answer)
    else:
        await bot.send_message(chat_id=conf.bot.admin,
                               text=f"{message.from_user.first_name} ответил неверно на втором шаге")
        answer = await message.reply(
            "❌ Неправильно!\n"
            "Попробуй еще раз или нажми кнопку 'Подсказка'.",
            reply_markup=question_keyboard(question_cmds)
        )
        await state.update_data(answer=answer)


@question_router.message(QuizStates.complete)
async def take_a_photo(message: Message, bot: Bot, state: FSMContext) -> None:
    user_data = await state.get_data()
    await user_data['answer'].edit_reply_markup()

    photo = message.photo[-1].file_id
    if message.photo:
        await bot.send_photo(chat_id=conf.bot.admin,photo=photo)

        if message.from_user.username == "Valeriabori":
            await message.answer(
                "💜💜💜💜💜\n"
                "Поздравляю с наступающим новым годом, пусть мечты сбываются, а все поставленные цели осуществляются!\n"
                "Успехов на играх будущего!!!\n"
                "❄️❄️❄️❄️❄️"
            )
        else:
            await message.answer(
                "💜💜💜💜💜\n"
                "Поздравляем с новым годом, пусть мечты сбываются, а все поставленные цели осуществляются!\n"
                "Увидимся в новом году!!!\n"
                "❄️❄️❄️❄️❄️"
            )

    else:
        await message.reply(
            "На этом шаге надо прислать фото.\n"
            "Попробуйте еще раз или нажмите кнопку 'Ну нахер'.",
            reply_markup=cancel_button(cancel_cmd)
        )


