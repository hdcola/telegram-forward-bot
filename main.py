#!/usr/bin/python
# -*- coding: utf-8 -*-

import config
from  feedback import feedback
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
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
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )

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

        if update.message.from_user.id == CONFIG['Admin']:
            helptext +="""

Bot管理员指令
/update 从Github上升级到最新的代码
/restart 重启Bot Service
/getconfig 得到现有的Bot配置
/setfeedback <str> 设置反馈按钮，每个按钮的文字用逗号分开
/setanswer <str> 设置反馈按钮按下后的提示信息，应该和铵钮数量相同，用逗号分开
            """
        
        bot.send_message(chat_id=update.message.chat_id,
                         text=helptext)
        return

    if update.message.from_user.id == CONFIG['Admin'] or check_admin(bot,CONFIG['Publish_Group_ID'][0],update.message.from_user.id):
        if command == 'feedbackoff':
            CONFIG['Feedback']=False
            config.save_config()
            bot.send_message(chat_id=update.message.chat_id,
                             text="Feedback已经关闭")
        elif command == 'feedbackon':
            CONFIG['Feedback']=True
            config.save_config()
            bot.send_message(chat_id=update.message.chat_id,
                             text="Feedback已经打开")

    if update.message.from_user.id == CONFIG['Admin'] :
        if command == 'update':
            shell=CONFIG['Update_shell'] + ' > /tmp/gitpull.txt'
            os.system(shell)
            output = open("/tmp/gitpull.txt").read()
            update.message.reply_text("Update命令\n%s\n执行完毕。输出内容：\n%s" % (shell,output))
        elif command == "restart":
            shell=CONFIG['Restart_shell'] + ' > /tmp/restart.txt'
            os.system(shell)
            output = open("/tmp/restart.txt").read()
            update.message.reply_text("Update命令\n%s\n执行完毕。输出内容：\n%s" % (shell,output))
        elif command == "getconfig":
            update.message.reply_text(config.get_json())
    return

def set_answer(update,context):
    if update.message.from_user.id == CONFIG['Admin'] :
        try:
            CONFIG['Feedback_answer'] = context.args[0]
            config.save_config()
            update.message.reply_text('反馈消息已经更新为:%s' % CONFIG['Feedback_answer'])
            return
        except (IndexError, ValueError):
            update.message.reply_text('使用说明: /setanswer 赞了一把,踩了一脚,吐了一地\n请使用逗号将每个按钮的反馈消息分开')

def set_feedback(update,context):
    if update.message.from_user.id == CONFIG['Admin'] :
        try:
            CONFIG['Feedback_text'] = context.args[0]
            config.save_config()
            update.message.reply_text('反馈按钮已经更新为:%s' % CONFIG['Feedback_text'] )
            return
        except (IndexError, ValueError):
            update.message.reply_text('使用说明: /setfeedback 👍,👎,🤮\n请使用逗号将按钮分开')

def send_anonymous_post(bot, msg, editor):
    if CONFIG['Feedback']:
        replay_markup = feedback.init_replay_markup_str(CONFIG['Feedback_text'],CONFIG['Feedback_answer'])
    else:
        replay_markup = InlineKeyboardMarkup([[]])

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
                            voice=msg.voice, caption=msg.caption)
        elif msg.video != None:
            r = bot.send_video(chat_id=chatid,
                            video=msg.video, caption=msg.caption,
                            reply_markup=replay_markup)
        elif msg.photo:
            r = bot.send_photo(chat_id=chatid,
                            photo=msg.photo[0], caption=msg.caption,
                            reply_markup=replay_markup)
        else:
            types = []
            for i in msg.entities:
                types.append(i.type)

            # print(msg,"\n",types)
            if 'url' in types or 'text_link' in types:
                r = bot.send_message(chat_id=chatid,
                                    text=msg.text_markdown,
                                    parse_mode=telegram.ParseMode.MARKDOWN,
                                    reply_markup=replay_markup)
            else:
                r = bot.send_message(chat_id=chatid,
                                    text=msg.text_markdown,
                                    parse_mode=telegram.ParseMode.MARKDOWN)


def process_callback(update, context):
    if update.channel_post != None:
        return
    query = update.callback_query
    replay_markup = feedback.get_update_replay_markupr(query)
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

    config.config_file = os.path.join(PATH,"config.json")
    CONFIG = config.load_config()

    updater = Updater(CONFIG['Token'], use_context=True)
    dispatcher = updater.dispatcher

    me = updater.bot.get_me()
    CONFIG['ID'] = me.id
    CONFIG['Username'] = '@' + me.username
    config.setdefault()
    print('Starting... (ID: ' + str(CONFIG['ID']) + ', Username: ' + CONFIG['Username'] + ')')

    if CONFIG['Feedback']:
        replay_markup = feedback.init_replay_markup_str(CONFIG['Feedback_text'],CONFIG['Feedback_answer'])

    dispatcher.add_handler(CommandHandler("setfeedback", set_feedback,
                                  pass_args=True))
    dispatcher.add_handler(CommandHandler("setanswer", set_answer,
                                  pass_args=True))
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

    updater.idle()
    print('Stopping...')
    print('Stopped.')
