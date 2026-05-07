import requests
from time import sleep
from environs import env
from dotenv import load_dotenv
import telebot



def sending_message(headers, url, bot, chat_id):
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
                    bot.send_message(chat_id=chat_id, text=text)


def main():
	load_dotenv()
    devman_token = env.str('DEVMAN_TOKEN')
    tg_bot_token = env.str('TELEGRAM_BOT_API_KEY')
    bot = telebot.TeleBot(tg_bot_token)
    chat_id = env.str("TELEGRAM_CHAT_ID")
    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        "Authorization": f"Token {devman_token}"
    }
    sending_message(headers, url, bot, chat_id)


if __name__ == "__main__":
    main()
