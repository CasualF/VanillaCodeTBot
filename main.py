from aiogram import Bot, Dispatcher, executor, types
from decouple import config
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import markups
import aiohttp
import asyncio
import requests

storage = MemoryStorage()
bot = Bot(config('TOKEN'))
dp = Dispatcher(bot=bot, storage=storage)
# dp.middleware.setup(LoggingMiddleware())

# Variables
cat_waving_sticker = 'CAACAgUAAxkBAAMTZODxSVrx-Au63rwBN1KalR7coR0AAuIFAAKncZlWsMfRBFaNBHQwBA'
subjects_photo = 'https://img.freepik.com/free-vector/cute-shiba-inu-dog-reading-book-with-coffee-cartoon-vector-icon-illustration-animal-education-icon_138676-5547.jpg'


# URLs
CHECK_NUMBER_API = 'http://app.vanilla-code.pp.ua/api/account/check_number/?number='


class UserState(StatesGroup):
    start = State()
    logged = State()
    exiting = State()


@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message:types.Message, state: FSMContext):
    await message.answer_sticker(cat_waving_sticker)
    await message.answer(f'Привет {message.from_user.first_name}, добро пожаловать в ✨Vanilla Code✨!\n'
                         f'Рассказываем о сложном простыми словами.'
                         f'Зацени наши курсы, там много интересного!', reply_markup=markups.start_markup)
    await UserState.start.set()


@dp.message_handler(lambda message: message.text == '📚 Предметы', state='*')
async def subjects(message: types.Message, state: FSMContext):
    subjects_caption = ('В данный момент у нас доступны курсы по трём наиболее востребованным направлениям\n'
                        'Чтобы выбрать направление выбери его нажатием по кнопке снизу ')
    await message.answer_photo(photo=subjects_photo, caption=subjects_caption, reply_markup=markups.subject_list)
    await state.finish()


@dp.message_handler(lambda message: message.text == '🐍 Backend', state='*')
async def contacts(message: types.Message, state: FSMContext):
    await message.answer('Контакты:\n'
                         'Email -> dastan12151@gmail.com\n'
                         'Наш сайт -> https://vanillacode-61871.web.app\n'
                         'Есть вопросы? Пиши сюда -> @dastanasanov')
    await state.finish()


@dp.message_handler(lambda message: message.text == '💩 Frontend', state='*')
async def contacts(message: types.Message, state: FSMContext):
    await message.answer()
    await state.finish()


@dp.message_handler(lambda message: message.text == '🪄 UX/UI Design', state='*')
async def contacts(message: types.Message, state: FSMContext):
    await message.answer('Контакты:\n'
                         'Email -> dastan12151@gmail.com\n'
                         'Наш сайт -> https://vanillacode-61871.web.app\n'
                         'Есть вопросы? Пиши сюда -> @dastanasanov')
    await state.finish()


@dp.message_handler(lambda message: message.text == '📞 Контакты', state='*')
async def contacts(message: types.Message, state: FSMContext):
    await message.answer('Контакты:\n'
                         'Email -> dastan12151@gmail.com\n'
                         'Наш сайт -> https://vanillacode-61871.web.app\n'
                         'Есть вопросы? Пиши сюда -> @dastanasanov')
    await state.finish()


@dp.message_handler(lambda message: message.text == '❌ Выйти из бота', state='*')
async def quit_bot(message: types.Message, state: FSMContext):
    await message.answer('Пока! Чтобы включить бота -> /start', reply_markup=types.ReplyKeyboardRemove())
    await bot.close()
    await state.finish()


@dp.message_handler(lambda message: message.text == '⬅️ Назад', state='*')
async def back_to_main_menu(message: types.Message, state: FSMContext):
    # Отправляем в старт меню
    await cmd_start(message, state)


@dp.message_handler(commands=['send_contact'])
async def send_contact(message: types.Message):
    await message.answer('Поделитесь номером чтобы мы смогли найти вас в базе данных сайта',
                         reply_markup=markups.share_contact)

    @dp.message_handler(content_types=types.ContentType.CONTACT)
    async def handle_contact(message: types.Message):
        contact = message.contact
        number = contact.phone_number
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(CHECK_NUMBER_API+number) as response:
                    if response.status == 200:
                        await message.answer('Нашли!')
                        await UserState.logged.set()
                    elif response.status == 404:
                        await message.answer('Юзера с таким номером телефона не существует!')
            except:
                await message.answer("Что то пошло не так...")

    # await message.answer('Контакт: ')


@dp.message_handler()
async def answer(message: types.Message):
    await message.reply('Такой команды нет, введи существующую!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
