#!/usr/bin/python
# -*- coding: utf-8 -*-
"""使用说明

import admincmd

admincmd.add_dispatcher(dispatcher)

然后自己来改下cmds，设置命令名和按钮名。这样就支持  /admin 和所有的按钮回调了。注意，cmds的callback名一定要admin:开头。
"""

from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import CommandHandler,Dispatcher,CallbackQueryHandler,CallbackContext
import config
from json import dumps
import os

cmds = {
    "admin:config":"配置",
    "admin:update":"更新",
    "admin:restart":"重启",
    "admin:status":"状态",
    "admin:help":"帮助"
    }

def admin_cmd_callback(update : Update, context : CallbackContext):
    if update.callback_query.from_user.id == config.CONFIG['Admin'] :
        msg=""
        query = update.callback_query
        if query.data == "admin:config":
            cfg = config.CONFIG.copy()
            cfg['Token'] = "***"
            query.answer("获取配置")
            msg = dumps(cfg,indent=4,ensure_ascii=False)
        elif query.data == "admin:status":
            shell=config.CONFIG['Status_shell'] + ' > /tmp/status.txt'
            os.system(shell)
            msg = "反回信息:\n" + open("/tmp/status.txt").read()
            query.answer("获取状态")
        elif query.data == "admin:restart":
            shell=config.CONFIG['Restart_shell'] + ' > /tmp/restart.txt'
            os.system(shell)
            msg = "反回信息:\n" + open("/tmp/restart.txt").read()
            query.answer("重启服务")
        elif query.data == "admin:help":
            msg = help()
            query.answer()
        elif query.data == "admin:update":
            shell=config.CONFIG['Update_shell'] + ' > /tmp/gitpull.txt'
            os.system(shell)
            msg = "反回信息:\n" + open("/tmp/gitpull.txt").read()
            query.answer("更新代码")
        query.edit_message_text(text=msg,reply_markup=init_replay_markup())

def init_buttons():
        buttons = []
        for key in cmds:
            buttons.append(InlineKeyboardButton(cmds[key], callback_data=key ) )
        return buttons

def init_replay_markup():
    return InlineKeyboardMarkup([init_buttons()])

def help():
    msg = """
都按按钮吧
"""
    return msg

def admin_cmd(update : Update, context : CallbackContext):
    if update.message.from_user.id == config.CONFIG['Admin'] :
        msg = help()
        update.message.reply_text(msg,reply_markup=init_replay_markup()) 

def add_dispatcher(dp: Dispatcher):
    dp.add_handler(CommandHandler(["admin"], admin_cmd))
    dp.add_handler(CallbackQueryHandler(admin_cmd_callback,pattern="^admin:[A-Za-z0-9_]*"))