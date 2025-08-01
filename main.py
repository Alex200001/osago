
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils import executor
import logging
import os

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Токен бота из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Хранилище данных пользователя
user_data = {}

# Клавиатура
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("Оформить ОСАГО"), KeyboardButton("Рассчитать стоимость"))

# Команда /start
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("Здравствуйте! Выберите действие:", reply_markup=main_kb)

# Старт анкеты
@dp.message_handler(lambda m: m.text == "Оформить ОСАГО")
async def start_survey(msg: types.Message):
    user_data[msg.from_user.id] = {"step": "name"}
    await msg.answer("Введите ваше ФИО:")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "name")
async def handle_name(msg: types.Message):
    user_data[msg.from_user.id]["name"] = msg.text
    user_data[msg.from_user.id]["step"] = "phone"
    await msg.answer("Введите номер телефона:")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "phone")
async def handle_phone(msg: types.Message):
    user_data[msg.from_user.id]["phone"] = msg.text
    user_data[msg.from_user.id]["step"] = "gosnomer"
    await msg.answer("Введите госномер автомобиля:")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "gosnomer")
async def handle_gosnomer(msg: types.Message):
    user_data[msg.from_user.id]["gosnomer"] = msg.text
    user_data[msg.from_user.id]["step"] = "vin"
    await msg.answer("Введите VIN номер:")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "vin")
async def handle_vin(msg: types.Message):
    user_data[msg.from_user.id]["vin"] = msg.text
    user_data[msg.from_user.id]["step"] = "brand"
    await msg.answer("Марка и модель автомобиля:")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "brand")
async def handle_brand(msg: types.Message):
    user_data[msg.from_user.id]["brand"] = msg.text
    user_data[msg.from_user.id]["step"] = "year"
    await msg.answer("Год выпуска автомобиля:")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "year")
async def handle_year(msg: types.Message):
    user_data[msg.from_user.id]["year"] = msg.text
    user_data[msg.from_user.id]["step"] = "confirm"
    await msg.answer("Спасибо! Анкета заполнена. Мы скоро свяжемся с вами.", reply_markup=main_kb)

# Расчёт стоимости
@dp.message_handler(lambda m: m.text == "Рассчитать стоимость")
async def ask_region(msg: types.Message):
    user_data[msg.from_user.id] = {"step": "calc_region"}
    await msg.answer("Введите ваш регион (например: Москва):")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "calc_region")
async def handle_region(msg: types.Message):
    user_data[msg.from_user.id]["region"] = msg.text
    user_data[msg.from_user.id]["step"] = "calc_power"
    await msg.answer("Введите мощность автомобиля в л.с.:")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "calc_power")
async def handle_power(msg: types.Message):
    try:
        power = int(msg.text)
        user_data[msg.from_user.id]["power"] = power
        user_data[msg.from_user.id]["step"] = "calc_age"
        await msg.answer("Введите возраст водителя:")
    except ValueError:
        await msg.answer("Пожалуйста, введите число (мощность в л.с.)")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "calc_age")
async def handle_age(msg: types.Message):
    try:
        age = int(msg.text)
        user_data[msg.from_user.id]["age"] = age
        user_data[msg.from_user.id]["step"] = "calc_kbm"
        await msg.answer("Введите КБМ (например, 0.85 — если без аварий):")
    except ValueError:
        await msg.answer("Пожалуйста, введите возраст числом.")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "calc_kbm")
async def handle_kbm(msg: types.Message):
    try:
        kbm = float(msg.text.replace(",", "."))
        user_data[msg.from_user.id]["kbm"] = kbm
        base = 8000
        result = base * kbm
        await msg.answer(f"Примерная стоимость ОСАГО: {int(result)} ₽", reply_markup=main_kb)
    except ValueError:
        await msg.answer("Введите корректное значение КБМ.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
