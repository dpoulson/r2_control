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

def status(bot, update):
    url = baseurl + "status"
    try:
        r = requests.get(url)
        bot.send_message(chat_id=update.message.chat_id, text=r.content)
    except:
        print "Fail...."
        bot.send_message(chat_id=update.message.chat_id, text="Failed to get status")

start_handler = CommandHandler('status', status)

dispatcher.add_handler(start_handler)


updater.start_polling()


