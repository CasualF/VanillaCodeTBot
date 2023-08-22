from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton


start_markup = ReplyKeyboardMarkup(resize_keyboard=True)
start_markup.add('📚 Предметы').add('📞 Контакты').add('❌ Выйти из бота')


subject_list = ReplyKeyboardMarkup(resize_keyboard=True)
subject_list.add('🐍 Backend', '💩 Frontend', '🪄 UX/UI Design', '⬅️ Назад')


course_options = ReplyKeyboardMarkup(resize_keyboard=True)
course_options.add('📖  Уроки', '📞 Контакты', '⬅️ Назад')


share_contact = ReplyKeyboardMarkup()
button = KeyboardButton('Поделиться контактом', request_contact=True)
share_contact.add(button, '⬅️ Назад')
