from ..common import *

class Welcome(StatesGroup):
    select_language = State()


@dispatcher.message_handler(commands="start")
async def start(message: types.Message):
    if await user_by_id(message.from_user.id) is None:
        await add_user(message.from_user.id)
        await select_language(message)
    else:
        await help(message)


@dispatcher.message_handler(commands="language")
async def select_language(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    languages = ("English", "Español", "Français")
    keyboard.add(*languages)
    languages = ("Português", "Русский", "简体中文")
    keyboard.add(*languages)

    await message.answer(locales["select-language"], reply_markup=keyboard)
    await Welcome.select_language.set()


@dispatcher.message_handler(Text(equals="English"), state=Welcome.select_language)
async def english_selected(message: types.Message, state: FSMContext):
    await language_selected("en", message, state)


@dispatcher.message_handler(Text(equals="Español"), state=Welcome.select_language)
async def spanish_selected(message: types.Message, state: FSMContext):
    await language_selected("es", message, state)


@dispatcher.message_handler(Text(equals="Français"), state=Welcome.select_language)
async def french_selected(message: types.Message, state: FSMContext):
    await language_selected("fr", message, state)


@dispatcher.message_handler(Text(equals="Português"), state=Welcome.select_language)
async def portuguese_selected(message: types.Message, state: FSMContext):
    await language_selected("pt", message, state)


@dispatcher.message_handler(Text(equals="Русский"), state=Welcome.select_language)
async def russian_selected(message: types.Message, state: FSMContext):
    await language_selected("ru", message, state)


@dispatcher.message_handler(Text(equals="简体中文"), state=Welcome.select_language)
async def chinese_selected(message: types.Message, state: FSMContext):
    await language_selected("zh", message, state)


async def language_selected(lang: str, message: types.Message, state: FSMContext):
    await set_lang(message.from_user.id, lang)
    await set_bot_commands(lang, message.from_user.id)
    await message.answer(locales["welcome"][lang], reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


async def set_bot_commands(lang: str, userId: int=None):
    commands = []

    for command, description in locales["commands"][lang].items():
        commands.append(types.BotCommand(command=command, description=description))
    
    #  If language_code is empty
    #  Commands will be applied to all users from the given scope
    if userId is not None:
        lang = ""
        scope = types.BotCommandScopeChat(userId)
    else:
        scope = types.BotCommandScopeDefault()
    
    await bot.set_my_commands(commands=commands, scope=scope, language_code=lang)


@dispatcher.message_handler(commands="help")
async def help(message: types.Message):
    await message.answer(await locale_string_by_id("welcome", message.from_user.id))


@dispatcher.errors_handler(exception=BotBlocked)
async def bot_blocked(update: types.Update, exception: BotBlocked) -> bool:
    return True
