from typing import Optional, Union
from telegram import (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    ForceReply
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, ChatMemberHandler, CommandHandler, ConversationHandler, ContextTypes
import sqlite3 as sql
from .help import *


async def results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    query_db.execute(
        f"""SELECT * FROM Teachers WHERE ID = "{user_id}";""")
    res = query_db.fetchone()
    if res is None or len(res) == 0:
        await context.bot.sendMessage(text="Эта функция доступна только преподавателю (пососи чел)",
                                      chat_id=update.message.chat_id)
        return ConversationHandler.END
    await context.bot.sendMessage(text="Введите название группы, результаты которой вы хотите посмотреть.",
                                  chat_id=update.message.chat_id)
    return "input_group"


async def get_resuts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.text
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    query_db.execute(
        f"""SELECT * FROM Groups WHERE GROUP_ID = "{group_id}";""")
    res = query_db.fetchone()
    if res is None or len(res) == 0:
        await context.bot.sendMessage(
            text="Такой группы не существует, создайте ее, если хотите!", chat_id=update.message.chat_id)
    elif res[2] is None:
        await context.bot.sendMessage(
            text="Задачи из вашей группы пока никто не решал!", chat_id=update.message.chat_id)
    else:
        res_students = res[2].split()
        res_dict = dict()
        for i in range(len(res_students)):
            res_one = res_students[i].split('_')
            task = res_one[1]
            id_student = res_one[0]
            if id_student in res_dict:
                res_dict[id_student].add(task)
            else:
                res_dict[id_student] = set()
                res_dict[id_student].add(task)
        j = 0
        text = ""
        for student in res_dict.keys():
            res_student = list(res_dict[student])
            text += "@" + str(student) + ": "
            text += str(len(res_student)) + " уникальных задач\n"
        await context.bot.send_message(
            text=f"{text}",
            chat_id=update.message.chat_id)

    keyboard = [
        [
            InlineKeyboardButton("Выйти к списку команд", callback_data="Выйти к списку команд")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Что дальше?", reply_markup=reply_markup)
    return 'what_to_do'