import os
import sys
sys.path.append("venv/lib/python3.13/site-packages")
import logging
import telebot
from dotenv import load_dotenv

# ✅ Логирование
logging.basicConfig(level=logging.INFO)

try:
    from .recognize_faces import recognize_and_return_names, write_names_to_sheet
except Exception as e:
    logging.error("Ошибка при импорте recognize_faces:", exc_info=True)
    raise

# ✅ Загрузка переменных окружения
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise Exception("❌ BOT_TOKEN не найден в .env файле")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохраняем фото временно
        photo_path = 'received_photo.jpg'
        with open(photo_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Распознаём
        recognized_names = recognize_and_return_names(photo_path)
        write_names_to_sheet(recognized_names)
        if recognized_names:
            response = "Распознаны: " + ", ".join(recognized_names)
        else:
            response = "Никого не распознали."

        bot.reply_to(message, response)

    except Exception as e:
        logging.error("Ошибка при обработке фото:", exc_info=True)
        bot.reply_to(message, "Произошла ошибка при распознавании.")

print("✅ Бот запущен. Ожидаю фото...")
bot.polling(none_stop=True)
