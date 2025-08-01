
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils import executor
import logging
import os
import re

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
ADMIN_ID = 1195423197
user_data = {}

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("Оформить ОСАГО"), KeyboardButton("Рассчитать стоимость"))

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("Здравствуйте, дорогой Клиент! Рады приветствовать вас в нашем Telegram-боте. Пожалуйста, выберите действие:", reply_markup=main_kb)

@dp.message_handler(lambda m: m.text == "Оформить ОСАГО")
async def start_survey(msg: types.Message):
    user_data[msg.from_user.id] = {"step": "name"}
    await msg.answer("Введите ваше ФИО:")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "name")
async def handle_name(msg: types.Message):
    user_data[msg.from_user.id]["name"] = msg.text
    user_data[msg.from_user.id]["step"] = "phone"
    await msg.answer("Введите номер телефона в формате +7XXXXXXXXXX:")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "phone")
async def handle_phone(msg: types.Message):
    phone = msg.text.strip()
    if re.fullmatch(r"\+7\d{10}", phone):
        user_data[msg.from_user.id]["phone"] = phone
        user_data[msg.from_user.id]["step"] = "gosnomer"
        await msg.answer("Введите госномер автомобиля (пример: А123ВС77 или A123BC799):")
    else:
        await msg.answer("❌ Неверный формат. Введите номер в формате +7XXXXXXXXXX.")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "gosnomer")
async def handle_gosnomer(msg: types.Message):
    gosnomer = msg.text.strip().upper()
    if re.fullmatch(r"^[А-ЯA-Z]{1}\d{3}[А-ЯA-Z]{2}\d{2,3}$", gosnomer):
        user_data[msg.from_user.id]["gosnomer"] = gosnomer
        user_data[msg.from_user.id]["step"] = "vin"
        await msg.answer("Введите VIN номер. Он указан в Свидетельстве о регистрации ТС. (:")
    else:
        await msg.answer("❌ Формат госномера неверный. Пример: А123ВС77 или A123BC799")

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
    data = user_data[msg.from_user.id]

    summary = (
        "📋 Новая заявка на ОСАГО:\n"
        f"👤 ФИО: {data.get('name')}\n"
        f"📞 Телефон: {data.get('phone')}\n"
        f"🚗 Госномер: {data.get('gosnomer')}\n"
        f"🔎 VIN: {data.get('vin')}\n"
        f"🚘 Марка: {data.get('brand')}\n"
        f"📆 Год выпуска: {data.get('year')}"
    )

    await msg.answer("Спасибо, уважаемый Клиент! Анкета заполнена! Свяжемся с вами в течении 1 часа.", reply_markup=main_kb)
    user_data[msg.from_user.id]["step"] = None

    try:
        await bot.send_message(ADMIN_ID, summary)
    except Exception as e:
        logging.error(f"Ошибка при отправке админу: {e}")

@dp.message_handler(lambda m: m.text == "Рассчитать стоимость")
async def ask_region(msg: types.Message):
    user_data[msg.from_user.id] = {"step": "calc_region"}
    await msg.answer("Введите ваш регион (например: Волгоград):")

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
        await msg.answer("Введите КБМ (например, 1,17 — если вы только получили права):")
    except ValueError:
        await msg.answer("Пожалуйста, введите возраст числом.")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "calc_kbm")
async def handle_kbm(msg: types.Message):
    try:
        kbm = float(msg.text.replace(",", "."))
        base = 8000
        result = base * kbm
        await msg.answer(f"Примерная стоимость ОСАГО. Для полного уточнения мы с вами свяжемся!: {int(result)} ₽", reply_markup=main_kb)
    except ValueError:
        await msg.answer("Введите корректное значение КБМ.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
