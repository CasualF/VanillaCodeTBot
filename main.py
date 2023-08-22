from aiogram import Bot, Dispatcher, executor, types
from decouple import config
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import markups
import aiohttp
import asyncio
import requests
import tempfile
import os

storage = MemoryStorage()
bot = Bot(config('TOKEN'))
dp = Dispatcher(bot=bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Variables
CAT_WAVING_STICKER = 'CAACAgUAAxkBAAMTZODxSVrx-Au63rwBN1KalR7coR0AAuIFAAKncZlWsMfRBFaNBHQwBA'
SUBJECTS_PHOTO = 'https://img.freepik.com/free-vector/cute-shiba-inu-dog-reading-book-with-coffee-cartoon-vector-icon-illustration-animal-education-icon_138676-5547.jpg'
DEFAULT_COURSE_PHOTO = 'http://app.vanilla-code.pp.ua/images/course_previews/photo_2023-08-15_14-38-52.jpg'


# URLs
MAIN_API = 'http://app.vanilla-code.pp.ua/'
CHECK_NUMBER_API = 'http://app.vanilla-code.pp.ua/api/account/check_number/?number='
GET_COURSES_API = 'http://app.vanilla-code.pp.ua/api/courses/'


class UserState(StatesGroup):
    start = State()
    # course = State() Not needed
    logged = State()
    logged_lesson_back = State()
    logged_lesson_front = State()
    logged_lesson_design = State()
    exiting = State()


@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message:types.Message, state: FSMContext):
    await message.answer_sticker(CAT_WAVING_STICKER)
    await message.answer(f'Привет {message.from_user.first_name}, добро пожаловать в ✨Vanilla Code✨!\n'
                         f'Рассказываем о сложном простыми словами.'
                         f'Зацени наши курсы, там много интересного!', reply_markup=markups.start_markup)
    await UserState.start.set()


@dp.message_handler(lambda message: message.text == '📚 Предметы', state=[UserState.logged, '*'])
async def subjects(message: types.Message, state: FSMContext):
    states = (UserState.logged.state, UserState.start.state)
    current_state = str(await state.get_state())
    if current_state in states and current_state == UserState.logged.state:
        subjects_caption = ('В данный момент у нас доступны курсы по трём наиболее востребованным направлениям\n'
                            'Чтобы узнать о направлении выбери его нажатием по кнопке снизу 👇')
        await message.answer_photo(photo=SUBJECTS_PHOTO, caption=subjects_caption, reply_markup=markups.subject_list)
    else:
        await message.answer('Чтобы смотреть курсы мы должны вас распознать как нашего юзера\n '
                             'Нажми /send_contact чтобы поделиться номером')
        await state.finish()


@dp.message_handler(lambda message: message.text == '🐍 Backend', state=UserState.logged)
async def contacts(message: types.Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(GET_COURSES_API) as response:
                if response.status == 200:
                    data = await response.json()
                    for course in data:
                        if course['title'] == 'Профессия Backend-разработчик':
                            backend_course = course
                    course_title = backend_course['title']
                    course_price = backend_course['price']
                    relative_preview = backend_course.get('preview', '')
                    avg_rating = backend_course.get('rating', {}).get('rating__avg', 'Рейтинг отсутствует')
                    full_preview = MAIN_API + relative_preview if relative_preview else DEFAULT_COURSE_PHOTO

                    async with session.get(full_preview) as image_response:
                        image_data = await image_response.read()
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
                            temp_image.write(image_data)
                            temp_image_path = temp_image.name

                    course_info = (
                        f"📚 Курс: {course_title}\n"
                        f"💰 Цена: {course_price}\n"
                        f"⭐ Рейтинг: {avg_rating}"
                    )
                    with open(temp_image_path, 'rb') as photo_file:
                        await message.answer_photo(photo=types.InputFile(photo_file),
                                                   caption=course_info,
                                                   reply_markup=markups.course_options)

                    os.remove(temp_image_path)

                    await UserState.logged_lesson_back.set()
                else:
                    await message.answer("Произошла ошибка при получении данных о курсах.")
        except Exception as e:
            await message.answer("Произошла ошибка при получении данных о курсах.")


@dp.message_handler(lambda message: message.text == '💩 Frontend', state=UserState.logged)
async def contacts(message: types.Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(GET_COURSES_API) as response:
                if response.status == 200:
                    data = await response.json()
                    for course in data:
                        if course['title'] == 'Профессия Frontend-разработчик':
                            frontend_course = course
                    course_title = frontend_course['title']
                    course_price = frontend_course['price']
                    relative_preview = frontend_course.get('preview', '')
                    avg_rating = frontend_course.get('rating', {}).get('rating__avg', 'Рейтинг отсутствует')
                    full_preview = MAIN_API + relative_preview if relative_preview else DEFAULT_COURSE_PHOTO

                    async with session.get(full_preview) as image_response:
                        image_data = await image_response.read()
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
                            temp_image.write(image_data)
                            temp_image_path = temp_image.name

                    course_info = (
                        f"📚 Курс: {course_title}\n"
                        f"💰 Цена: {course_price}\n"
                        f"⭐ Рейтинг: {avg_rating}"
                    )
                    with open(temp_image_path, 'rb') as photo_file:
                        await message.answer_photo(photo=types.InputFile(photo_file),
                                                   caption=course_info,
                                                   reply_markup=markups.course_options)

                    os.remove(temp_image_path)
                    await UserState.logged_lesson_front.set()
                else:
                    await message.answer("Произошла ошибка при получении данных о курсах.")
        except Exception as e:
            await message.answer("Произошла ошибка при получении данных о курсах.")


@dp.message_handler(lambda message: message.text == '🪄 UX/UI Design', state=UserState.logged)
async def contacts(message: types.Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(GET_COURSES_API) as response:
                if response.status == 200:
                    data = await response.json()
                    for course in data:
                        if course['title'] == 'Профессия UX/UI‑дизайнер':
                            design_course = course
                    course_title = design_course['title']
                    course_price = design_course['price']
                    relative_preview = design_course.get('preview', '')
                    avg_rating = design_course.get('rating', {}).get('rating__avg', 'Рейтинг отсутствует')
                    full_preview = MAIN_API + relative_preview if relative_preview else DEFAULT_COURSE_PHOTO

                    async with session.get(full_preview) as image_response:
                        image_data = await image_response.read()
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
                            temp_image.write(image_data)
                            temp_image_path = temp_image.name

                    course_info = (
                        f"📚 Курс: {course_title}\n"
                        f"💰 Цена: {course_price}\n"
                        f"⭐ Рейтинг: {avg_rating}"
                    )
                    with open(temp_image_path, 'rb') as photo_file:
                        await message.answer_photo(photo=types.InputFile(photo_file),
                                                   caption=course_info,
                                                   reply_markup=markups.course_options)

                    os.remove(temp_image_path)
                    await UserState.logged_lesson_design.set()
                else:
                    await message.answer("Произошла ошибка при получении данных о курсах.")
        except Exception as e:
            await message.answer("Произошла ошибка при получении данных о курсах.")


@dp.message_handler(lambda message: message.text == '📖  Уроки',
                    state=[UserState.logged_lesson_design, UserState.logged_lesson_front, UserState.logged_lesson_back])
async def lessons(message: types.Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        current_state = await state.get_state()
        if current_state == UserState.logged_lesson_back.state:
            course_id = 10
        elif current_state == UserState.logged_lesson_front.state:
            course_id = 1
        elif current_state == UserState.logged_lesson_design.state:
            course_id = 9
        try:
            lessons_url = f'http://16.171.231.50/api/lessons/?course_id={course_id}'
            async with session.get(lessons_url) as response:
                if response.status == 200:
                    lesson_data = await response.json()
                    results = lesson_data.get("results")[0]
                    next_link = lesson_data.get("next")
                    previous_link = lesson_data.get("previous")
                    youtube_link = results.get("youtube_link", "У данного урока нет видеоролика")
                    relative_preview = results.get("preview", "")
                    question = results.get("question", "У данного урока нет вопроса к нему")
                    if question != 'У данного урока нет вопроса к нему':
                        right_answer = results.get('right_answer')
                        wrong_answers = results.get('wrong_answers')
                        answers = (right_answer + ', ' + wrong_answers) if wrong_answers else right_answer
                    else:
                        answers = 'Нет вопроса, нет ответов'
                    like_count = results.get("like_count", 0)
                    dislike_count = results.get("dislike_count", 0)

                    full_preview_url = MAIN_API + relative_preview if relative_preview else DEFAULT_COURSE_PHOTO

                    async with session.get(full_preview_url) as image_response:
                        image_data = await image_response.read()
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
                            temp_image.write(image_data)
                            temp_image_path = temp_image.name

                    lesson_info = (
                        f"🖥️ Ссылка на ютуб ролик: {youtube_link}\n"
                        f"❓ Вопрос к уроку: {question}\n"
                        f"📝 Ответы: {answers}\n"
                        f"👍 Лайков: {like_count},👎 Дизлайков: {dislike_count}"
                    )

                    await state.update_data(next_link=next_link)
                    await state.update_data(previous_link=previous_link)
                    with open(temp_image_path, 'rb') as photo_file:
                        await bot.send_photo(message.chat.id, photo=photo_file, caption=lesson_info)

                    os.remove(temp_image_path)

                    keyboard = InlineKeyboardMarkup(row_width=2)
                    if lesson_data.get("previous"):
                        keyboard.add(InlineKeyboardButton("Предыдущий", callback_data="previous_lesson"))
                    if lesson_data.get("next"):
                        keyboard.add(InlineKeyboardButton("Следующий", callback_data="next_lesson"))

                    await bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)

                else:
                    await message.answer("Произошла ошибка при получении данных об уроках.")
        except Exception as e:
            await message.answer("Произошла ошибка при получении данных об уроках.")


@dp.callback_query_handler(lambda query: query.data == "next_lesson",
                           state='*')
async def next_page_hotels_callback(callback_query: types.CallbackQuery, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        try:
            data = await state.get_data()
            next_link = data.get("next_link")

            async with session.get(next_link) as response:
                if response.status == 200:
                    lesson_data = await response.json()
                    results = lesson_data.get("results")[0]
                    next_link = lesson_data.get("next")
                    previous_link = lesson_data.get("previous")

                    youtube_link = results.get("youtube_link", "У данного урока нет видеоролика")
                    relative_preview = results.get("preview", "")
                    question = results.get("question", "У данного урока нет вопроса к нему")
                    if question != 'У данного урока нет вопроса к нему':
                        right_answer = results.get('right_answer')
                        wrong_answers = results.get('wrong_answers')
                        answers = (right_answer + ', ' + wrong_answers) if wrong_answers else right_answer
                    like_count = results.get("like_count", 0)
                    dislike_count = results.get("dislike_count", 0)

                    full_preview_url = MAIN_API + relative_preview if relative_preview else DEFAULT_COURSE_PHOTO

                    async with session.get(full_preview_url) as image_response:
                        image_data = await image_response.read()
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
                            temp_image.write(image_data)
                            temp_image_path = temp_image.name

                    lesson_info = (
                        f"🖥️ Ссылка на ютуб ролик: {youtube_link}\n"
                        f"❓ Вопрос к уроку: {question}\n"
                        f"📝 Ответы: {answers}\n"
                        f"👍 Лайков: {like_count},👎 Дизлайков: {dislike_count}"
                    )

                    await state.update_data(next_link=next_link)
                    await state.update_data(previous_link=previous_link)
                    with open(temp_image_path, 'rb') as photo_file:
                        await bot.send_photo(callback_query.message.chat.id, photo=photo_file, caption=lesson_info)

                    os.remove(temp_image_path)

                    keyboard = InlineKeyboardMarkup(row_width=2)
                    if lesson_data.get("previous"):
                        keyboard.add(InlineKeyboardButton("Предыдущий", callback_data="previous_lesson"))
                    if lesson_data.get("next"):
                        keyboard.add(InlineKeyboardButton("Следующий", callback_data="next_lesson"))

                    await bot.send_message(callback_query.message.chat.id, "Выберите действие:", reply_markup=keyboard)

                else:
                    await callback_query.message.answer("Произошла ошибка при получении данных об уроках.")
        except Exception as e:
            await callback_query.message.answer("Произошла ошибка при получении данных об уроках.")


@dp.callback_query_handler(lambda query: query.data == "previous_lesson",
                           state='*')
async def next_page_hotels_callback(callback_query: types.CallbackQuery, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        try:
            data = await state.get_data()
            previous_link = data.get("previous_link")

            async with session.get(previous_link) as response:
                if response.status == 200:
                    lesson_data = await response.json()
                    results = lesson_data.get("results")[0]
                    next_link = lesson_data.get("next")
                    previous_link = lesson_data.get("previous")

                    youtube_link = results.get("youtube_link", "У данного урока нет видеоролика")
                    relative_preview = results.get("preview", "")
                    question = results.get("question", "У данного урока нет вопроса к нему")
                    if question != 'У данного урока нет вопроса к нему':
                        right_answer = results.get('right_answer')
                        wrong_answers = results.get('wrong_answers')
                        answers = (right_answer + ', ' + wrong_answers) if wrong_answers else right_answer
                    like_count = results.get("like_count", 0)
                    dislike_count = results.get("dislike_count", 0)

                    full_preview_url = MAIN_API + relative_preview if relative_preview else DEFAULT_COURSE_PHOTO

                    async with session.get(full_preview_url) as image_response:
                        image_data = await image_response.read()
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
                            temp_image.write(image_data)
                            temp_image_path = temp_image.name

                    lesson_info = (
                        f"🖥️ Ссылка на ютуб ролик: {youtube_link}\n"
                        f"❓ Вопрос к уроку: {question}\n"
                        f"📝 Ответы: {answers}\n"
                        f"👍 Лайков: {like_count},👎 Дизлайков: {dislike_count}"
                    )

                    await state.update_data(next_link=next_link)
                    await state.update_data(previous_link=previous_link)
                    with open(temp_image_path, 'rb') as photo_file:
                        await bot.send_photo(callback_query.message.chat.id, photo=photo_file, caption=lesson_info)

                    os.remove(temp_image_path)

                    keyboard = InlineKeyboardMarkup(row_width=2)
                    if lesson_data.get("previous"):
                        keyboard.add(InlineKeyboardButton("Предыдущий", callback_data="previous_lesson"))
                    if lesson_data.get("next"):
                        keyboard.add(InlineKeyboardButton("Следующий", callback_data="next_lesson"))

                    await bot.send_message(callback_query.message.chat.id, "Выберите действие:", reply_markup=keyboard)

                else:
                    await callback_query.message.answer("Произошла ошибка при получении данных об уроках.")
        except Exception as e:
            await callback_query.message.answer("Произошла ошибка при получении данных об уроках.")


@dp.message_handler(lambda message: message.text == '📞 Контакты', state='*')
async def contacts(message: types.Message, state: FSMContext):
    await message.answer('Контакты:\n'
                         'Email -> dastan12151@gmail.com\n'
                         'Наш сайт -> https://vanillacode-61871.web.app\n'
                         'Есть вопросы? Пиши сюда -> @dastanasanov')


@dp.message_handler(lambda message: message.text == '❌ Выйти из бота', state='*')
async def quit_bot(message: types.Message, state: FSMContext):
    await message.answer('Пока! Чтобы включить бота -> /start', reply_markup=types.ReplyKeyboardRemove())
    await bot.close()
    await state.finish()


@dp.message_handler(lambda message: message.text == '⬅️ Назад', state='*')
async def back_to_main_menu(message: types.Message, state: FSMContext):
    states = [UserState.logged_lesson_design.state,
              UserState.logged_lesson_front.state,
              UserState.logged_lesson_back.state]
    current_state = await state.get_state()
    if current_state in states:
        await UserState.logged.set()
        await subjects(message, state)
    else:
        await cmd_start(message, state)


@dp.message_handler(commands=['send_contact'], state='*')
async def send_contact(message: types.Message):
    await message.answer('Поделитесь номером чтобы мы смогли найти вас в базе данных сайта',
                         reply_markup=markups.share_contact)

    @dp.message_handler(content_types=types.ContentType.CONTACT, state='*')
    async def handle_contact(message: types.Message):
        contact = message.contact
        number = contact.phone_number
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(CHECK_NUMBER_API+number) as response:
                    if response.status == 200:
                        await message.answer('Нашли!', reply_markup=markups.start_markup)
                        await UserState.logged.set()
                    elif response.status == 404:
                        await message.answer(f'Юзера с таким номером телефона не существует!\n'
                                             f'Зарегистрируйтесь и вернитесь после {MAIN_API}',
                                             reply_markup=types.ReplyKeyboardRemove())
            except:
                await message.answer("Что то пошло не так...")


@dp.message_handler()
async def answer(message: types.Message):
    await message.reply('Такой команды нет, введи существующую!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
