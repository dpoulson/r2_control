#!/usr/bin/python

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import requests
import logging

baseurl = "http://localhost:5000/"
updater = Updater(token='367756606:AAFr5YEN1w2A9VEHcDaxCvoGolrMgz4CPsA')

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def volmute(bot, update):
    url = baseurl + "/audio/volume/0"
    try:
        r = requests.get(url)
        bot.send_message(chat_id=update.message.chat_id, text=r.content)
    except:
        print "Fail...."
        bot.send_message(chat_id=update.message.chat_id, text="Failed to Mute")

def volmax(bot, update):
    url = baseurl + "/audio/volume/1"
    try:
        r = requests.get(url)
        bot.send_message(chat_id=update.message.chat_id, text=r.content)
    except:
        print "Fail...."
        bot.send_message(chat_id=update.message.chat_id, text="Failed to deafen")


def sounds(bot, update, args):
    url = baseurl + "audio/"
    try:
        r = requests.get(url)
        bot.send_message(chat_id=update.message.chat_id, text=r.content)
    except:
        print "Fail...."
        bot.send_message(chat_id=update.message.chat_id, text="Failed to deafen")


def status(bot, update):
    url = baseurl + "status"
    try:
        r = requests.get(url)
        bot.send_message(chat_id=update.message.chat_id, text=r.content)
    except:
        print "Fail...."
        bot.send_message(chat_id=update.message.chat_id, text="Failed to get status")

start_handler = CommandHandler('status', status)
sounds_handler = CommandHandler('sounds', sounds, pass_args=True)
volmute_handler = CommandHandler('mute', volmute)
volmax_handler = CommandHandler('maxvol', volmax)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(sounds_handler)
dispatcher.add_handler(volmute_handler)
dispatcher.add_handler(volmax_handler)


updater.start_polling()


