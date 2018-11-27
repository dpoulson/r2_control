import requests
from r2utils import internet


def send(message):
    """ Sends a telegram message """
    if internet.check():
        try:
            send_message = "Test"
            #send_message = 'https://api.telegram.org/bot' + config.get('telegram', 'token')
            #send_message += '/sendMessage?chat_id=' + config.get('telegram', 'chat_id')
            #send_message += '&parse_mode=Markdown&text='
            #send_message += message
            requests.get(send_message)
        except:
            if __debug__:
                print("Thought we had an internet connection, but sending Telegram failed")
    else:
        if __debug__:
            print("Tried to send Telegram, but no internet connection")
