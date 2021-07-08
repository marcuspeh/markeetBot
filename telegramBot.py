import sys
import os
import math
import string
import logging
import os
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from random import random

token = os.environ["token"]
PORT = int(os.environ.get('PORT', 5000))

class telegramBot:
    def __init__(self, token, port):
        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        self.logger = logging.getLogger(__name__)
        self.command = {}
        self.cache = {}
        self.token = token
        self.port = PORT

    def start(self, update, context):
        """Send a message when the command /start is issued."""
        print(update)
        self.command[update.message.from_user.id] = "/start"
        self.cache[update.message.from_user.id] = None
        update.message.reply_text('Hi there!')

    def help(self, update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Help!\n\n/checkstock - Check if an item is in stock at a particular store')
        self.command[update.message.from_user.id] = "/help"
        self.cache[update.message.from_user.id] = None

    def checkStock(self, update, context):
        """Check stock in shop"""
        self.command[update.message.from_user.id] = "/checkstock"
        self.cache[update.message.from_user.id] = None
        update.message.reply_text('Enter the shop name (case sensitive)')

    def checkStock_StoreName(self, update, text):
        self.cache[update.message.from_user.id] = text
        update.message.reply_text('Enter the item to find (case sensitive)')

    def checkStock_ItemName(self, update, text):
        url = "https://markeet.herokuapp.com/api/telegram/checkstock"
        json = {"shopName": self.cache[update.message.from_user.id], "productName": text}
        res = requests.get(url, json = json)
        result = res.json()
        update.message.reply_text(result["message"])
        self.command[update.message.from_user.id] = None
        self.cache[update.message.from_user.id] = None

    def listInventory(self, update, text):
        self.command[update.message.from_user.id] = "/list"
        self.cache[update.message.from_user.id] = None
        update.message.reply_text('Enter the shop name (case sensitive)')
    
    def listInventory_ItemName(self, update, text):
        url = "https://markeet.herokuapp.com/api/telegram/listinventory"
        json = {"shopName": text}
        res = requests.get(url, json = json)
        result = res.json()
        if "inventory" in result:
            result = result["inventory"]
            result = [(x["title"]) for x in result]
            result.sort()
            temp = "\n".join(result)

            update.message.reply_text("All products at {}:\n{}".format(text, temp))
        else:
            update.message.reply_text(result["message"])
        self.command[update.message.from_user.id] = None
        self.cache[update.message.from_user.id] = None

    def unknown(self, update, context):
        if self.command[update.message.from_user.id] == "/checkstock":
            if not self.cache[update.message.from_user.id]:
                return self.checkStock_StoreName(update, update.message.text)
            else:
                return self.checkStock_ItemName(update, update.message.text)
        elif self.command[update.message.from_user.id] == "/list":
            return self.listInventory_ItemName(update, update.message.text)
        else:
            self.command[update.message.from_user.id] = None
            self.cache[update.message.from_user.id] = None
            return self.help(update, context)
                
    def run(self):
        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        updater = Updater(self.token, use_context=True)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # on different commands - answer in Telegram
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CommandHandler("help", self.help))
        dispatcher.add_handler(CommandHandler("checkstock", self.checkStock))
        dispatcher.add_handler(CommandHandler("list", self.listInventory))

        # on non command i.e message - echo the message on Telegram
        dispatcher.add_handler(MessageHandler(Filters.text, self.unknown))

        # Start the Bot
        updater.start_webhook(listen="0.0.0.0",
                port=int(self.port),
                url_path=self.token)
        updater.bot.setWebhook('https://markeet-bot.herokuapp.com/' + self.token)

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()



if __name__ == "__main__":
    bot = telegramBot(token, PORT)
    bot.run()



