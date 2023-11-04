from Tiktok_uploader import uploadVideo
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
from config import bot_api
import time
import os

bot = Bot(token=bot_api)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())


class UserState(StatesGroup):
    sessionid = State()
    name = State()
    tags_1 = State()
    tags_2 = State()
    tags_3 = State()
    tags_4 = State()
    tags_5 = State()
    tags_6 = State()
    video = State()


profile = InlineKeyboardButton("Профиль", callback_data='profile')
code = InlineKeyboardButton("Использовать код", callback_data='use_code')
pour = InlineKeyboardButton("Начать пролив", callback_data='start_pour')
start_markup = InlineKeyboardMarkup().add(profile, code, pour)


@dp.message_handler(Command('start'))
async def on_start(message: types.Message):
    await message.answer("Введите код запуска")


secret_code = 'test_use'


@dp.message_handler(lambda message: message.text == secret_code)
async def tracks(message: types.Message):
    await message.answer("Тестовый пролив активирован")
    await message.answer("AutoProlivBot", reply_markup=start_markup)


@dp.callback_query_handler(lambda c: c.data == 'start_pour')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Введите sessionid")
    await UserState.sessionid.set()


@dp.message_handler(state=UserState.sessionid)
async def process_sessionid_step(message: types.Message, state: FSMContext):
    await state.update_data(sessionid=message.text)
    await message.answer("Введите название видео")
    await UserState.name.set()


@dp.message_handler(state=UserState.name)
async def process_name_step(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите теги для 1 видео через запятую")
    await UserState.tags_1.set()


@dp.message_handler(state=UserState.tags_1)
async def process_tags_step(message: types.Message, state: FSMContext):
    await state.update_data(tags_1=message.text.split(','))
    await message.answer("Введите теги для 2 видео через запятую")
    await UserState.tags_2.set()


@dp.message_handler(state=UserState.tags_2)
async def process_tags_step(message: types.Message, state: FSMContext):
    await state.update_data(tags_2=message.text.split(','))
    await message.answer("Введите теги для 3 видео через запятую")
    await UserState.tags_3.set()


@dp.message_handler(state=UserState.tags_3)
async def process_tags_step(message: types.Message, state: FSMContext):
    await state.update_data(tags_3=message.text.split(','))
    await message.answer("Введите теги для 4 видео через запятую")
    await UserState.tags_4.set()


@dp.message_handler(state=UserState.tags_4)
async def process_tags_step(message: types.Message, state: FSMContext):
    await state.update_data(tags_4=message.text.split(','))
    await message.answer("Введите теги для 5 видео через запятую")
    await UserState.tags_5.set()


@dp.message_handler(state=UserState.tags_5)
async def process_tags_step(message: types.Message, state: FSMContext):
    await state.update_data(tags_5=message.text.split(','))
    await message.answer("Введите теги для 6 видео через запятую")
    await UserState.tags_6.set()


@dp.message_handler(state=UserState.tags_6)
async def process_tags_step(message: types.Message, state: FSMContext):
    await state.update_data(tags_6=message.text.split(','))
    await message.answer("Отправьте видео")
    await UserState.video.set()


@dp.message_handler(state=UserState.video, content_types=types.ContentType.VIDEO)
async def upload_video_step(message: types.Message, state: FSMContext):
    status_message = await message.answer("Видео загружается")
    video = message.video
    video_file_id = video.file_id
    video_file_name = video.file_name  # Название файла (опционально)

    # Задайте путь и имя файла, куда сохранить видео
    save_path = 'videos/'  # Укажите путь к папке, где будет сохранено видео
    save_file_name = video_file_name if video_file_name else 'video.mp4'
    file = await bot.download_file_by_id(file_id=video_file_id)
    with open(save_path + save_file_name, 'wb') as video_file:
        video_file.write(file.read())
    video_path = save_path + save_file_name

    try:
        user_data = await state.get_data()
        session_id = user_data['sessionid']
        video_name = user_data['name']

        # Список тегов
        tags = [user_data['tags_1'], user_data['tags_2'], user_data['tags_3'],
                user_data['tags_4'], user_data['tags_5'], user_data['tags_6']]

        uploaded_count = 0  # Счетчик загруженных видео

        for tag in tags:
            uploadVideo(session_id, video_path, video_name, tag, verbose=True)
            uploaded_count += 1
            await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Видео {uploaded_count} из 6 загружено")
            time.sleep(20)

        if os.path.exists(video_path):
            os.remove(video_path)

        await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Все видео успешно залиты")

        await message.answer("AutoProlivBot", reply_markup=start_markup)
        await state.finish()
    except Exception as e:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Ошибка залива видео: {e}")
        return



# session_id = "a1a4dbc461f9f302b23c6a1502900004"
# file = 'my_video.mp4'
# title = "мама"
# tags = ['bitcoin', "Joke", "fyp"]
#
#
# # Publish the video
# uploadVideo(session_id, file, title, tags, verbose=True)
if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
