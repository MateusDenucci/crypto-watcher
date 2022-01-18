import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from dotenv import load_dotenv
import os


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


def check_prices(tokens_to_watch):
    tokens = [key for key in tokens_to_watch.keys()]

    token_prices = get_tokens_price(','.join(tokens))

    for token in token_prices:
        if token_prices[token] >= tokens_to_watch[token]:
            message = f'The current price of the token {token} is {token_prices[token]} USD and the price you were looking for was {tokens_to_watch[token]} USD'
            send_telegram_message(message, os.getenv('PERSONAL_TELEGRAM_ID'))


if __name__ == '__main__':
    load_dotenv()

    tokens_to_watch = {
        'bit-hotel': 0.24,
        'star-atlas': 0.013,
        'ertha': 0.60,
    }

    check_prices(tokens_to_watch)
