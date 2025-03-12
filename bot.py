import os
import asyncio
import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import API_TOKEN
from db_con import init_db, save_to_db
from parse import get_average_price


bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()



keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Отправить файл", callback_data="send_file")],
        [InlineKeyboardButton(text="💵 Узнать среднюю сумму товаров", callback_data="send_avg_price")]
    ])


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("Привет! Выберите действие:", reply_markup=keyboard)




@dp.callback_query()
async def handle_button_click(callback_query: types.CallbackQuery):
    if callback_query.data == "send_file":
        await callback_query.message.answer("Пожалуйста, отправьте Excel файл с данными для парсинга.")
    elif callback_query.data == "send_avg_price":
        try:
            text = get_average_price()
        except:
            text = "Ошибка. База пуста"
        await callback_query.message.answer(text, reply_markup=keyboard)



# Обработчик документов
@dp.message()
async def handle_docs(message: types.Message):
    if message.document and message.document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        downloaded_file = await bot.download_file(file_path)
        with open("temp.xlsx", "wb") as new_file:
            new_file.write(downloaded_file.getvalue())
        df = pd.read_excel("temp.xlsx")
        text = df.to_string(index=False)
        # Удаляем первую строку
        text = "\n".join(text.split("\n")[1:])
        await message.reply(f"Содержимое файла:\n{text}")
        # Сохраняем данные в бд
        conn, cursor = init_db()
        for index, row in df.iterrows():
            save_to_db(cursor, row['title'], row['url'], row['xpath'])
        conn.close()
        # Удаляем временный файл
        os.remove("temp.xlsx")
        await message.reply("Данные успешно сохранены в базу данных!", reply_markup=keyboard)
    else:
        await message.reply("Пожалуйста, отправьте файл в формате Excel (.xlsx).", reply_markup=keyboard)


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())