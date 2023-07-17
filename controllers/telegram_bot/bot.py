""" Bot to talk to telegram and receive commands """

from telegram.ext import Updater
from telegram.ext import CommandHandler
import configparser
import requests
import logging
import time
from future import standard_library
standard_library.install_aliases()

time.sleep(20)

config = configparser.RawConfigParser()
config.read('config.cfg')

baseurl = "http://localhost:5000/"
updater = Updater(token=config.get('DEFAULT', 'token'))

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def volmute(bot, update):
    """ Mute volume """
    url = baseurl + "audio/volume/0"
    try:
        r = requests.get(url)
        bot.send_message(chat_id=update.message.chat_id, text=r.content)
    except Exception:
        print("Fail....")
        bot.send_message(chat_id=update.message.chat_id, text="Failed to Mute")


def volmax(bot, update):
    """ Set volume to max """
    url = baseurl + "audio/volume/1"
    try:
        r = requests.get(url)
        bot.send_message(chat_id=update.message.chat_id, text=r.content)
    except Exception:
        print("Fail....")
        bot.send_message(chat_id=update.message.chat_id, text="Failed to deafen")


def sounds(bot, update, args):
    """ Get a list of sounds """
    url = baseurl + "audio/"
    if len(args) == 0:
        url += "list"
    else:
        url += args[0]
    try:
        r = requests.get(url)
        bot.send_message(chat_id=update.message.chat_id, text=r.content)
    except Exception:
        print("Fail....")
        bot.send_message(chat_id=update.message.chat_id, text="Failed...")


def joystick(bot, update, args):
    """ List all joysticks """
    url = baseurl + "joystick/"
    if len(args) == 0:
        url += "list"
    else:
        url += args[0]
    try:
        r = requests.get(url)
        bot.send_message(chat_id=update.message.chat_id, text=r.content)
    except Exception:
        print("Fail....")
        bot.send_message(chat_id=update.message.chat_id, text="Failed...")


def status(bot, update):
    """ Get status of droid """
    url = baseurl + "status"
    try:
        r = requests.get(url)
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text=r.content)
    except Exception:
        print("Fail....")
        bot.send_message(chat_id=update.message.chat_id, text="Failed to get status")


def chatid(bot, update):
    """ Get chat ID """
    try:
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text=chat_id)
    except Exception:
        print("Fail....")
        bot.send_message(chat_id=update.message.chat_id, text="Failed to get chat_id")


start_handler = CommandHandler('status', status)
sounds_handler = CommandHandler('sounds', sounds, pass_args=True)
joystick_handler = CommandHandler('joystick', joystick, pass_args=True)
volmute_handler = CommandHandler('mute', volmute)
volmax_handler = CommandHandler('maxvol', volmax)
chatid_handler = CommandHandler('chatid', chatid)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(sounds_handler)
dispatcher.add_handler(joystick_handler)
dispatcher.add_handler(volmute_handler)
dispatcher.add_handler(volmax_handler)
dispatcher.add_handler(chatid_handler)

updater.start_polling()
