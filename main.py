import requests
import json
from time import sleep
from environs import env
from dotenv import load_dotenv
import telebot
load_dotenv()


def main():
    devman_token = env.str('DEVMAN_TOKEN')
    tg_bot_token = env.str('TELEGRAM_BOT_API_KEY')
    bot = telebot.TeleBot(tg_bot_token)
    chat_id = env.str("TELEGRAM_CHAT_ID")
    url = 'https://dvmn.org/api/long_polling/'
    headers = {
	"Authorization": f"Token {devman_token}"
    }
    timestamp = {}   
    while True:
        try:
            response = requests.get(url, headers=headers, timeout=5, params=timestamp)
            response = response.json()            
            timestamp.clear()
            if response.get('timestamp_to_request'):
                timestamp['timestamp'] = response.get('timestamp_to_request')
                print(response)
            elif response.get('status') == 'found':
            	text = 'Преподаватель проверил работу!'
                bot.send_message(chat_id=chat_id, text=text)
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            continue    	
        sleep(3)


if __name__ == "__main__":
    main()