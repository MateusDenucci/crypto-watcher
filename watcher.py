import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from dotenv import load_dotenv
import os


load_dotenv()

TOKENS_TO_WATCH = {
    'bit-hotel': 0.24,
    'star-atlas': 0.13,
    'ertha': 0.60,
    'cryptowolf-finance': 6.0,
}


def get_tokens_price(tokens):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

    parameters = {
      'slug': tokens
    }

    headers = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': os.getenv('CMC_API_KEY'),
    }

    session = requests.session()
    session.headers.update(headers)

    try:
        result = {}
        response = session.get(url, params=parameters)
        response_data = json.loads(response.text)

        if response_data['status']['error_code'] == 0:
            for token_id in response_data['data']:
                result[response_data['data'][token_id]['slug']] = response_data['data'][token_id]['quote']['USD']['price']
        
        return result
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


def send_telegram_message(message, telegram_chat_id):
    if telegram_chat_id:
        payload = {
            'chat_id': telegram_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        return requests.post("https://api.telegram.org/bot{token}/sendMessage".format(token=os.getenv('TELEGRAM_TOKEN')),
                             data=payload).content
    else:
        return False


def check_prices(only_price_achieved):
    tokens = [key for key in TOKENS_TO_WATCH.keys()]

    token_prices = get_tokens_price(','.join(tokens))

    message = ''
    if only_price_achieved:
        for token in token_prices:
            if token_prices[token] >= TOKENS_TO_WATCH[token]:
                message += f'TIME TO SELL! The current price of the token {token} is ${round(token_prices[token], 2)} USD and the price you are looking for is ${TOKENS_TO_WATCH[token]} \n\n'                
    
    else:
        for token in token_prices:
            message += f'The current price of the token {token} is ${round(token_prices[token], 2)} USD and the price you are looking for is ${TOKENS_TO_WATCH[token]} \n\n'
    send_telegram_message(message, os.getenv('PERSONAL_TELEGRAM_ID'))
