#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import json
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
import telegram
import os
import logging
import getopt
import sys
try:
    import systemd.daemon
    from systemd import journal
    systemd_enable=True
except ImportError:
    systemd_enable=False

from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )

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

def check_admin(bot,chatid,userid):
    try:
        member = bot.get_chat_member(chatid,userid)
        if member.status in [ 'administrator' , 'creator']:
            return True
        return False
    except telegram.TelegramError as e:
        return False


def process_msg(update, context):
    bot = context.bot
    if update.channel_post != None:
        return

    if update.message.from_user.id == update.message.chat_id:
        member = False
        for chat_id in CONFIG['Publish_Group_ID']:
            if check_member(bot,chat_id,update.message.from_user.id):
                member = True
        if member :
            send_anonymous_post(bot, update.message,update.message.from_user)
        else:
            update.message.reply_text('您不是我们匿名了天群的用户，所以我什么都做不了。寂寞总让人伤感，找个朋友去聊天吧~')


def process_command(update, context):
    bot = context.bot
    if update.channel_post != None:
        return
    command = update.message.text[1:].replace(CONFIG['Username'], ''
            ).lower()
    if command == 'start' or command == 'help':
        helptext = "将文字、图片、音频/语音、视频、文件发送给我，我将直接把对它们匿名转发到你所在的群"
        if update.message.from_user.id == CONFIG['Admin'] or check_admin(bot,CONFIG['Publish_Group_ID'][0],update.message.from_user.id):
            helptext += """

管理员指令：
/feedbackoff 关闭所有匿名发送的反馈
/feedbackon 打开所有匿名发送的反馈
            """
        
        bot.send_message(chat_id=update.message.chat_id,
                         text=helptext)
        return

    if update.message.from_user.id == CONFIG['Admin'] or check_admin(bot,CONFIG[Publish_Group_ID][0],update.message.from_user.id):
        if command == 'feedbackoff':
            CONFIG['Feedback']=False
            save_config()
            bot.send_message(chat_id=update.message.chat_id,
                             text="Feedback已经关闭")
        elif command == 'feedbackon':
            CONFIG['Feedback']=True
            save_config()
            bot.send_message(chat_id=update.message.chat_id,
                             text="Feedback已经打开")
    if update.message.from_user.id == CONFIG['Admin'] :
        if command == 'update':
            gitpull_shell=CONFIG['Update_shell'] + ' > /tmp/gitpull.txt'
            os.system(gitpull_shell)
            output = open("/tmp/gitpull.txt").read()
            update.message.reply_text("Update命令执行完毕。输出内容：\n%s" % output)
    return



def send_anonymous_post(bot, msg, editor):
    if CONFIG['Feedback']:
        keyboard = [[InlineKeyboardButton("👍",callback_data="d:0"),
                    InlineKeyboardButton("👎",callback_data="c:0")]]
    else:
        keyboard = [[]]
    replay_markup = InlineKeyboardMarkup(keyboard)

    for chatid in CONFIG['Publish_Group_ID']:
        if msg.audio != None:
            r = bot.send_audio(chat_id=chatid,
                            audio=msg.audio, caption=msg.caption,
                            reply_markup=replay_markup)
        elif msg.document != None:
            r = bot.send_document(chat_id=chatid,
                                document=msg.document,
                                caption=msg.caption,
                                reply_markup=replay_markup)
        elif msg.voice != None:
            r = bot.send_voice(chat_id=chatid,
                            voice=msg.voice, caption=msg.caption,
                            reply_markup=replay_markup)
        elif msg.video != None:
            r = bot.send_video(chat_id=chatid,
                            video=msg.video, caption=msg.caption,
                            reply_markup=replay_markup)
        elif msg.photo:
            r = bot.send_photo(chat_id=chatid,
                            photo=msg.photo[0], caption=msg.caption,
                            reply_markup=replay_markup)
        else:
            r = bot.send_message(chat_id=chatid,
                                text=msg.text_markdown,
                                parse_mode=telegram.ParseMode.MARKDOWN,
                                reply_markup=replay_markup)


def process_callback(update, context):
    if update.channel_post != None:
        return
    query = update.callback_query

    print(query)
    button,count = query.data.split(":")
    count = int(count) + 1

    if button == "d":
        query.answer("你觉得这个适合群风")
    else:
        query.answer("你觉得不应该发送这样的匿名消息")

    buttons = query.message.reply_markup.inline_keyboard[0]
    update_buttons = []

    for b in buttons:
        if b.callback_data == query.data:
            update_buttons.append(InlineKeyboardButton("%s%s"%(b.text[0:1],count),callback_data="%s:%s"%(button,count) ) )
        else:
            update_buttons.append(InlineKeyboardButton(b.text,callback_data=b.callback_data ) )

    replay_markup = InlineKeyboardMarkup([update_buttons])
    
    query.edit_message_reply_markup(replay_markup)

def help():
    return "'main.py -c <configpath>'"

if __name__ == '__main__':

    PATH = os.path.dirname(os.path.expanduser("~/.config/forwardbot/"))

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
    if systemd_enable:
        systemd.daemon.notify('READY=1')
        journal.send('Starting... (ID: ' + str(CONFIG['ID']) + ', Username: ' + CONFIG['Username'] + ')')

    updater.idle()
    print('Stopping...')
    print('Stopped.')
