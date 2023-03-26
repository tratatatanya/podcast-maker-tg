import os
import telegram
from dotenv import load_dotenv
from telegram.ext import Updater, MessageHandler, Filters
from telegram.error import TelegramError, TimedOut, BadRequest
from pytube import YouTube
from pytube.exceptions import RegexMatchError

load_dotenv()


def get_audio(update, context):
    url = update.message.text
    chat = update.effective_chat
    try:
        yt = YouTube(url)
    except RegexMatchError:
        context.bot.send_message(
            chat_id=chat.id,
            text='Вставьте валидную ссылку, с этой ничего не поделаешь :('
        )
        return
    context.bot.send_message(chat_id=chat.id, text='Получено, скачиваю!')
    audio = yt.streams.get_audio_only()
    filename = audio.default_filename
    audio.download()
    filepath = os.path.join(os.getcwd(), filename)
    filesize = os.path.getsize(filepath)
    if filesize <= 50 * 1024 * 1024:
        context.bot.send_message(chat_id=chat.id, text='Скачано, отправляю!')
        audiofile = open(filename, "rb")
        context.bot.send_audio(chat_id=chat.id, audio=audiofile)
        audiofile.close()
    else:
        context.bot.send_message(
            chat_id=chat.id,
            text='Упс, аудиофайл больше 50МБ, его нельзя отправить через бота!'
        )
    os.remove(filepath)


def main():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    bot = telegram.Bot(token=bot_token)
    updater = Updater(token=bot_token)
    chat_id = None
    try:
        updates = bot.get_updates()
        if updates:
            last_update = updates[-1]
            chat_id = last_update.message.chat_id
        updater.dispatcher.add_handler(MessageHandler(Filters.text, get_audio))
    except (TelegramError, TimedOut, BadRequest) as e:
        error_msg = f"Произошла ошибка: {e}"
        bot.send_message(chat_id=chat_id, text=error_msg)
        return
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

