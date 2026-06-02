import requests
import telebot
import logging

from time import sleep
from environs import env
from dotenv import load_dotenv


def get_text_for_message(headers, bot, chat_id):
    url = 'https://dvmn.org/api/long_polling/'
    timestamp = {}
    while True:
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=5,
                params=timestamp
            )
            response.raise_for_status()
            response = response.json()
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(3)
            continue
        else:
            if response.get('timestamp_to_request'):
                timestamp['timestamp'] = response.get('timestamp_to_request')
            elif response.get('status') == 'found':
                timestamp['timestamp'] = response.get('last_attempt_timestamp')
                attempts = response.get("new_attempts")
                for attempt in attempts:
                    url = attempt.get("lesson_url")
                    title = attempt.get("lesson_title")
                    if attempt.get("is_negative"):
                        text_review = "К сожалению, в работе нашлись ошибки."
                    else:
                        text_review = "Преподавателю все понравилось, можно приступать к следующему уроку!"
                    text = f"У вас проверили работу <<{title}>>\n{text_review}\n{url}"
                    send_message(chat_id, text, bot)


def send_message(chat_id, text, bot):
    bot.send_message(chat_id=chat_id, text=text)


def main():
    load_dotenv()
    devman_token = env.str('DEVMAN_TOKEN')
    tg_bot_token = env.str('TELEGRAM_BOT_API_KEY')
    bot = telebot.TeleBot(tg_bot_token)
    chat_id = env.str("TELEGRAM_CHAT_ID")
    headers = {
        "Authorization": f"Token {devman_token}"
    }
    class MyLogsHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            bot.send_message(chat_id=chat_id, text=log_entry)
    logger = logging.getLogger('MyLogsHandler')
    logger.setLevel(logging.INFO)
    logger.addHandler(MyLogsHandler())
    try:
        get_text_for_message(headers, bot, chat_id)
    except Exception as err:
        logger.error('Бот упал с ошибкой:', exc_info=True)


if __name__ == "__main__":
    main()
