import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from sqlalchemy import select

# Импортируем наши настройки базы
from models import async_db_setup, async_session, User, Course, Mark
from kb import main_kb

TOKEN = '1560768289:AAHpEGqBi4Bmk_Iijk1GgDDTk3MwctYljsE'
bot = Bot(token=TOKEN)
dp = Dispatcher()


# Хендлер команды /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    async with async_session() as session:
        # Проверка регистрации
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))

        if not user:
            new_user = User(
                tg_id=message.from_user.id,
                name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                type_id=1  # По умолчанию "Студент"
            )
            session.add(new_user)
            await session.commit()
            await message.answer("Добро пожаловать! Вы зарегистрированы.", reply_markup=main_kb)
        else:
            await message.answer(f"С возвращением, {user.name}!", reply_markup=main_kb)


# Просмотр профиля
@dp.message(F.text == "Мой профиль")
async def profile(message: types.Message):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
        await message.answer(f"👤 Профиль\nИмя: {user.name}\nID: {user.tg_id}")


# Просмотр оценок
@dp.message(F.text == "Мои оценки")
async def marks(message: types.Message):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
        result = await session.scalars(select(Mark).where(Mark.user_id == user.user_id))
        marks_list = result.all()

        if not marks_list:
            await message.answer("У вас пока нет оценок.")
        else:
            text = "📊 Ваши оценки:\n" + "\n".join([f"Задание {m.task_id}: {m.value}" for m in marks_list])
            await message.answer(text)


async def main():
    # Создаем таблицы при запуске
    await async_db_setup()
    # Запуск логгирования
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
