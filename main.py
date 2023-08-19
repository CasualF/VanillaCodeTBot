from aiogram import Bot, Dispatcher, executor, types
from decouple import config


bot = Bot(config('TOKEN'))
db = Dispatcher(bot=bot)


@db.message_handler(commands=['start'])
async def cmd_start(message:types.Message):
    await message.answer('Добро пожаловать в Vanilla Code!\nO сложном простыми словами')


@db.message_handler()
async def answer(message: types.Message):
    await message.reply('Такой команды нет, введи существующую!')


if __name__ == '__main__':
    executor.start_polling(db)