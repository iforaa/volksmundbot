#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import states
import logging
import constants
from time import sleep

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

AW_COMMAND, AW_POLL_QUESTION, AW_POLL_ANSWER, AW_CHOOSING_RATE, AW_RATE_NEXT_OR_BACK, AW_RANKING = range(6)

RP_COMMAND_CREATE = "Create Poll"
RP_COMMAND_RATE = "Rate"
RP_COMMAND_RANKING = "Ranking"
RP_COMMANT_BACK = "Back"
RP_COMMAND_NEXT_WORD = "Next Word"


reply_keyboard = [[RP_COMMAND_CREATE, RP_COMMAND_RATE], [RP_COMMAND_RANKING],
                  ["Done"]]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
rate_reply_keyboard = [["1", "2", "3"],["4", "5"],['Done']]
rate_markup = ReplyKeyboardMarkup(rate_reply_keyboard, one_time_keyboard=True)



def keys(bot, update):
    update.message.reply_text(states.allKeys())


def keys(bot, update):
    update.message.reply_text(states.showAnswers())


def clear(bot, update):
    states.clearRedis()


def start(bot, update):
    update.message.reply_text(
        u"Welcome! I'm Volksmund Bot. Let's be creative and find new german words"
        u"for anglicisms. What do you want to do?",
        reply_markup=markup)
    states.set_state(update.message.chat_id, AW_COMMAND)


def receiver(bot, update):
    chat_id = update.message.chat_id
    text = update.message.text
    chat_state = int(states.get_state(chat_id))

    if chat_state == AW_COMMAND:
        if text == RP_COMMAND_CREATE:
            update.message.reply_text(
                u"Let's start a new open case. Send me word you want to change")
            states.set_state(chat_id, AW_POLL_QUESTION)

        elif text == RP_COMMAND_RATE:
            states.set_state(chat_id, AW_CHOOSING_RATE)
            question = states.get_random_question(chat_id)

            if question is False:
                update.message.reply_text("No words",
                    reply_markup=markup)
                states.set_state(update.message.chat_id, AW_COMMAND)
            else:
                update.message.reply_text(u"Bad word: " + question,
        reply_markup=rate_markup)
                sleep(1)
                update.message.reply_text("Variant: " + states.get_random_answer(chat_id))

        elif text == RP_COMMAND_RANKING:
            states.set_state(chat_id, AW_RANKING)
            ranking_keyboard = [[RP_COMMANT_BACK]]
            ranking_markup = ReplyKeyboardMarkup(ranking_keyboard, one_time_keyboard=True)
            update.message.reply_text(states.prepare_ranking(),
                              reply_markup=ranking_markup)


    elif chat_state == AW_POLL_QUESTION:
        update.message.reply_text(
            u"Please send me the print answer option")
        states.set_question(chat_id, text)
        states.set_state(chat_id, AW_POLL_ANSWER)
    elif chat_state == AW_POLL_ANSWER:
        states.add_answ_var(chat_id, text)

        if states.get_answ_len(chat_id) < 4:
            update.message.reply_text(
                u"Please send me the print answer option")
        else:
            update.message.reply_text(u"Thank you!",
                reply_markup=markup)
            states.set_state(chat_id, AW_COMMAND)
    elif chat_state == AW_CHOOSING_RATE:
        if text.isdigit():
            states.add_rate(chat_id, text)
            answer = states.get_random_answer(chat_id)
            if answer is None:
                states.add_rated_question(chat_id)
                states.set_state(chat_id, AW_RATE_NEXT_OR_BACK)
                next_or_back_keyboard = [[RP_COMMANT_BACK, RP_COMMAND_NEXT_WORD]]
                next_or_back_markup = ReplyKeyboardMarkup(next_or_back_keyboard, one_time_keyboard=True)
                update.message.reply_text("?",
                                          reply_markup=next_or_back_markup)
            else:
                update.message.reply_text("Variant: " + answer,
                                          reply_markup=rate_markup)
        else:
            update.message.reply_text("Try again",
                                      reply_markup=rate_markup)

    elif chat_state == AW_RATE_NEXT_OR_BACK:
        if text == RP_COMMANT_BACK:
            states.set_state(chat_id, AW_COMMAND)
            update.message.reply_text(
                u"Welcome! I'm Volksmund Bot. Let's be creative and find new german words"
                u"for anglicisms. What do you want to do?",
                reply_markup=markup)
        elif text == RP_COMMAND_NEXT_WORD:
            states.set_state(chat_id, AW_CHOOSING_RATE)
            question = states.get_random_question(chat_id)

            if question is False:
                update.message.reply_text("No words",
                                          reply_markup=markup)
                states.set_state(update.message.chat_id, AW_COMMAND)
            else:
                update.message.reply_text(u"Bad word: " + question,
                                          reply_markup=rate_markup)
                sleep(1)
                update.message.reply_text("Variant: " + states.get_random_answer(chat_id))

    elif chat_state == AW_RANKING:
        if text == RP_COMMANT_BACK:
            states.set_state(chat_id, AW_COMMAND)
            update.message.reply_text(
                u"Welcome! I'm Volksmund Bot. Let's be creative and find new german words"
                u"for anglicisms. What do you want to do?",
                reply_markup=markup)








def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(constants.TELEGRAM_KEY)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("keys", keys))
    dp.add_handler(CommandHandler("clear", clear))
    dp.add_handler(MessageHandler(Filters.text, receiver))



    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()



