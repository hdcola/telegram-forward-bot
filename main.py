#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import json
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
import telegram
import os
import logging
import threading
import getopt
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )

def save_data():
    global DATA_LOCK
    while DATA_LOCK:
        time.sleep(0.05)
    DATA_LOCK = True
    f = open(os.path.join(PATH,"data.json"), 'w')
    f.write(json.dumps(submission_list, ensure_ascii=False))
    f.close()
    DATA_LOCK = False


def save_config():
    f = open(os.path.join(PATH,"config.json"), 'w')
    f.write(json.dumps(CONFIG, indent=4))
    f.close()

def check_member(bot,chatid,userid):
    try:
        bot.get_chat_member(chatid,userid)
        return True
    except telegram.TelegramError as e:
        return False

def process_msg(update, context):
    bot = context.bot
    if update.channel_post != None:
        return
    if update.message.chat_id == CONFIG['Group_ID'] \
        and update.message.reply_to_message != None:
        if update.message.reply_to_message.from_user.id == CONFIG['ID'] \
            and (update.message.reply_to_message.forward_from != None
                 or update.message.reply_to_message.forward_from_chat
                 != None):
            msg = update.message.reply_to_message
            global submission_list
            if submission_list[str(CONFIG['Group_ID']) + ':'
                               + str(msg.message_id)]['posted'] == True:
                return
            if submission_list[str(CONFIG['Group_ID']) + ':'
                               + str(msg.message_id)]['type'] == 'real':
                post = real_name_post(bot, msg,
                        update.message.from_user)
            elif submission_list[str(CONFIG['Group_ID']) + ':'
                                 + str(msg.message_id)]['type'] \
                == 'anonymous':

                post = anonymous_post(bot, msg,
                        update.message.from_user)
            if update.message.text != None:
                for chat_id in CONFIG['Publish_Channel_ID']:
                    bot.send_message(chat_id=chat_id,
                                    text=update.message.text,
                                    reply_to_message_id=post.message_id)
            return
    if update.message.from_user.id == update.message.chat_id:
        member = False
        for chat_id in CONFIG['Publish_Channel_ID']:
            if check_member(bot,chat_id,update.message.from_user.id):
                member = True
        if member :
            send_anonymous_post(bot, update.message,update.message.from_user)
        else:
            markup = \
                telegram.InlineKeyboardMarkup([[telegram.InlineKeyboardButton("是"
                    , callback_data='submission_type:real'),
                    telegram.InlineKeyboardButton("否",
                    callback_data='submission_type:anonymous')],
                    [telegram.InlineKeyboardButton("取消投稿",
                    callback_data='cancel:submission')]])
            if update.message.forward_from != None \
                or update.message.forward_from_chat != None:
                if update.message.forward_from_chat != None:
                    markup = \
                        telegram.InlineKeyboardMarkup([[telegram.InlineKeyboardButton("是"
                            , callback_data='submission_type:real')],
                            [telegram.InlineKeyboardButton("取消投稿",
                            callback_data='cancel:submission')]])
                elif update.message.forward_from.id \
                    != update.message.from_user.id:
                    markup = \
                        telegram.InlineKeyboardMarkup([[telegram.InlineKeyboardButton("是"
                            , callback_data='submission_type:real')],
                            [telegram.InlineKeyboardButton("取消投稿",
                            callback_data='cancel:submission')]])
            bot.send_message(chat_id=update.message.chat_id,
                            text="即将完成投稿...\n⁠您是否想要保留消息来源(保留消息发送者用户名)",
                            reply_to_message_id=update.message.message_id,
                            reply_markup=markup)


def process_command(update, context):
    bot = context.bot
    if update.channel_post != None:
        return
    command = update.message.text[1:].replace(CONFIG['Username'], ''
            ).lower()
    if command == 'start':
        bot.send_message(chat_id=update.message.chat_id,
                         text="""可接收的投稿类型:
文字
图片
音频/语音
视频
文件""")
        return

    if update.message.from_user.id == CONFIG['Admin']:
        if command == 'setgroup':
            CONFIG['Group_ID'] = update.message.chat_id
            save_config()
            bot.send_message(chat_id=update.message.chat_id,
                             text="已设置本群为审稿群")
            return


def send_anonymous_post(bot, msg, editor):
    for chatid in CONFIG['Publish_Channel_ID']:
        if msg.audio != None:
            r = bot.send_audio(chat_id=chatid,
                            audio=msg.audio, caption=msg.caption)
        elif msg.document != None:
            r = bot.send_document(chat_id=chatid,
                                document=msg.document,
                                caption=msg.caption)
        elif msg.voice != None:
            r = bot.send_voice(chat_id=chatid,
                            voice=msg.voice, caption=msg.caption)
        elif msg.video != None:
            r = bot.send_video(chat_id=chatid,
                            video=msg.video, caption=msg.caption)
        elif msg.photo:
            r = bot.send_photo(chat_id=chatid,
                            photo=msg.photo[0], caption=msg.caption)
        else:
            r = bot.send_message(chat_id=chatid,
                                text=msg.text_markdown,
                                parse_mode=telegram.ParseMode.MARKDOWN)


def anonymous_post(bot, msg, editor):
    for chatid in CONFIG['Publish_Channel_ID']:
        if msg.audio != None:
            r = bot.send_audio(chat_id=chatid,
                            audio=msg.audio, caption=msg.caption)
        elif msg.document != None:
            r = bot.send_document(chat_id=chatid,
                                document=msg.document,
                                caption=msg.caption)
        elif msg.voice != None:
            r = bot.send_voice(chat_id=chatid,
                            voice=msg.voice, caption=msg.caption)
        elif msg.video != None:
            r = bot.send_video(chat_id=chatid,
                            video=msg.video, caption=msg.caption)
        elif msg.photo:
            r = bot.send_photo(chat_id=chatid,
                            photo=msg.photo[0], caption=msg.caption)
        else:
            r = bot.send_message(chat_id=chatid,
                                text=msg.text_markdown,
                                parse_mode=telegram.ParseMode.MARKDOWN)

    submission_list[str(CONFIG['Group_ID']) + ':'
                    + str(msg.message_id)]['posted'] = True
    bot.edit_message_text(text="新投稿\n投稿人: ["
                          + submission_list[str(CONFIG['Group_ID'])
                          + ':' + str(msg.message_id)]['Sender_Name']
                          + '](tg://user?id='
                          + str(submission_list[str(CONFIG['Group_ID'])
                          + ':' + str(msg.message_id)]['Sender_ID'])
                          + """)
来源: 保留
审稿人: [""" + editor.name
                          + '](tg://user?id=' + str(editor.id)
                          + ")\n已采用", chat_id=CONFIG['Group_ID'],
                          parse_mode=telegram.ParseMode.MARKDOWN,
                          message_id=submission_list[str(CONFIG['Group_ID'
                          ]) + ':' + str(msg.message_id)]['Markup_ID'])
    bot.send_message(chat_id=submission_list[str(CONFIG['Group_ID'])
                     + ':' + str(msg.message_id)]['Sender_ID'],
                     text="您的稿件已过审，感谢您对我们的支持",
                     reply_to_message_id=submission_list[str(CONFIG['Group_ID'
                     ]) + ':' + str(msg.message_id)]['Original_MsgID'])
    threading.Thread(target=save_data).start()
    return r


def real_name_post(bot, msg, editor):
    global submission_list
    for chatid in CONFIG['Publish_Channel_ID']:
        r = bot.forward_message(chat_id=chatid,
                                from_chat_id=CONFIG['Group_ID'],
                                message_id=msg.message_id)

    submission_list[str(CONFIG['Group_ID']) + ':'
                    + str(msg.message_id)]['posted'] = True
    bot.edit_message_text(text="新投稿\n投稿人: ["
                          + submission_list[str(CONFIG['Group_ID'])
                          + ':' + str(msg.message_id)]['Sender_Name']
                          + '](tg://user?id='
                          + str(submission_list[str(CONFIG['Group_ID'])
                          + ':' + str(msg.message_id)]['Sender_ID'])
                          + """)
来源: 保留
审稿人: [""" + editor.name
                          + '](tg://user?id=' + str(editor.id)
                          + ")\n已采用", chat_id=CONFIG['Group_ID'],
                          parse_mode=telegram.ParseMode.MARKDOWN,
                          message_id=submission_list[str(CONFIG['Group_ID'
                          ]) + ':' + str(msg.message_id)]['Markup_ID'])
    bot.send_message(chat_id=submission_list[str(CONFIG['Group_ID'])
                     + ':' + str(msg.message_id)]['Sender_ID'],
                     text="您的稿件已过审，感谢您对我们的支持",
                     reply_to_message_id=submission_list[str(CONFIG['Group_ID'
                     ]) + ':' + str(msg.message_id)]['Original_MsgID'])
    threading.Thread(target=save_data).start()
    return r


def process_callback(update, context):
    bot = context.bot
    if update.channel_post != None:
        return
    global submission_list
    query = update.callback_query
    if query.message.chat_id == CONFIG['Group_ID'] and query.data \
        == 'receive:real':
        real_name_post(bot, query.message.reply_to_message,
                       query.from_user)
        return
    if query.message.chat_id == CONFIG['Group_ID'] and query.data \
        == 'receive:anonymous':
        anonymous_post(bot, query.message.reply_to_message,
                       query.from_user)
        return
    if query.data == 'cancel:submission':
        bot.edit_message_text(text="已取消投稿",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return
    msg = "新投稿\n投稿人: [" + query.message.reply_to_message.from_user.name \
        + '](tg://user?id=' \
        + str(query.message.reply_to_message.from_user.id) + ")\n来源: "
    fwd_msg = bot.forward_message(chat_id=CONFIG['Group_ID'],
                                  from_chat_id=query.message.chat_id,
                                  message_id=query.message.reply_to_message.message_id)

    submission_list[str(CONFIG['Group_ID']) + ':'
                    + str(fwd_msg.message_id)] = {}

    submission_list[str(CONFIG['Group_ID']) + ':'
                    + str(fwd_msg.message_id)]['posted'] = False

    submission_list[str(CONFIG['Group_ID']) + ':'
                    + str(fwd_msg.message_id)]['Sender_Name'] = \
        query.message.reply_to_message.from_user.name

    submission_list[str(CONFIG['Group_ID']) + ':'
                    + str(fwd_msg.message_id)]['Sender_ID'] = \
        query.message.reply_to_message.from_user.id

    submission_list[str(CONFIG['Group_ID']) + ':'
                    + str(fwd_msg.message_id)]['Original_MsgID'] = \
        query.message.reply_to_message.message_id

    if query.data == 'submission_type:real':
        msg += "保留"

        submission_list[str(CONFIG['Group_ID']) + ':'
                        + str(fwd_msg.message_id)]['type'] = 'real'
        markup = \
            telegram.InlineKeyboardMarkup([[telegram.InlineKeyboardButton("采用"
                , callback_data='receive:real')]])
        markup_msg = bot.send_message(chat_id=CONFIG['Group_ID'],
                text=msg, reply_to_message_id=fwd_msg.message_id,
                reply_markup=markup,
                parse_mode=telegram.ParseMode.MARKDOWN)

        submission_list[str(CONFIG['Group_ID']) + ':'
                        + str(fwd_msg.message_id)]['Markup_ID'] = \
            markup_msg.message_id
    elif query.data == 'submission_type:anonymous':
        msg += "匿名"

        submission_list[str(CONFIG['Group_ID']) + ':'
                        + str(fwd_msg.message_id)]['type'] = 'anonymous'
        markup = \
            telegram.InlineKeyboardMarkup([[telegram.InlineKeyboardButton("采用"
                , callback_data='receive:anonymous')]])
        markup_msg = bot.send_message(chat_id=CONFIG['Group_ID'],
                text=msg, reply_to_message_id=fwd_msg.message_id,
                reply_markup=markup,
                parse_mode=telegram.ParseMode.MARKDOWN)

        submission_list[str(CONFIG['Group_ID']) + ':'
                        + str(fwd_msg.message_id)]['Markup_ID'] = \
            markup_msg.message_id
    bot.edit_message_text(text="感谢您的投稿", chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    threading.Thread(target=save_data).start()


def help():
    return "'main.py -c <configpath>'"

if __name__ == '__main__':

    PATH = os.path.dirname(os.path.expanduser("~/.forwardbot/"))

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hc:",["config="])
    except getopt.GetoptError:
        print(help())
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help())
            sys.exit()
        elif opt in ("-c","--config"):
            PATH = arg

    CONFIG = json.loads(open(os.path.join(PATH,"config.json"), 'r').read())

    DATA_LOCK = False

    submission_list = json.loads(open(os.path.join(PATH,"data.json"), 'r').read())

    updater = Updater(CONFIG['Token'], use_context=True)
    dispatcher = updater.dispatcher

    me = updater.bot.get_me()
    CONFIG['ID'] = me.id
    CONFIG['Username'] = '@' + me.username

    print('Starting... (ID: ' + str(CONFIG['ID']) + ', Username: ' + CONFIG['Username'] + ')')

    dispatcher.add_handler(CallbackQueryHandler(process_callback))
    dispatcher.add_handler(MessageHandler(Filters.command,process_command))
    dispatcher.add_handler(MessageHandler( Filters.text
                        | Filters.audio
                        | Filters.photo
                        | Filters.video
                        | Filters.voice
                        | Filters.document , process_msg))

    updater.start_polling()
    print('Started')
    updater.idle()
    print('Stopping...')
    save_data()
    print('Data saved.')
    print('Stopped.')
