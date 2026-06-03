import requests
import telebot
import logging

from time import sleep
from environs import env
from dotenv import load_dotenv

load_dotenv()
TG_BOT_TOKEN = env.str('TELEGRAM_BOT_API_KEY')
BOT = telebot.TeleBot(TG_BOT_TOKEN)
CHAT_ID = env.str("TELEGRAM_CHAT_ID")


def get_review_result(headers):
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
                    send_message(text)


def send_message(text):
    BOT.send_message(chat_id=CHAT_ID, text=text)


class MyLogsHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        BOT.send_message(chat_id=CHAT_ID, text=log_entry)   


def main():
    devman_token = env.str('DEVMAN_TOKEN')
    headers = {
        "Authorization": f"Token {devman_token}"
    }
    logger = logging.getLogger('MyLogsHandler')
    logger.setLevel(logging.INFO)
    logger.addHandler(MyLogsHandler())
    try:
        get_review_result(headers)
    except Exception as err:
        logger.error('Бот упал с ошибкой:')
        logger.exception(err)
        get_review_result(headers)


if __name__ == "__main__":
    main()
