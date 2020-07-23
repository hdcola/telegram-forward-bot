#!/usr/bin/python
# -*- coding: utf-8 -*-

from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
import telegram
from datetime import date


class Feedback:
    feedbacks = {}
    show_answer = True
    show_alert = False

    def __init__(self):
        pass

    def init_buttons(self):
        buttons = []
        for key in self.feedbacks:
            buttons.append(InlineKeyboardButton(key, callback_data="%s:0"%key ) )
        return buttons

    def init_replay_markup_str(self,feedback_text,feedback_answer): 
        self.feedbacks = dict( zip( feedback_text.split(","),feedback_answer.split(",")) )
        return self.init_replay_markup()

    def init_replay_markup(self):
        return InlineKeyboardMarkup([self.init_buttons()])

    def get_update_replay_markupr(self,query):
        replay_markup = InlineKeyboardMarkup([self.get_updatebuttons(query)])
        return replay_markup

    def get_updatebuttons(self,query):
        button,count = query.data.split(":")
        count = int(count) + 1
    
        buttons = query.message.reply_markup.inline_keyboard[0]
        update_buttons = []

        if self.show_answer:
            query.answer(self.feedbacks[button],show_alert=self.show_alert)

        for b in buttons:
            if b.callback_data == query.data:
                update_buttons.append(InlineKeyboardButton("%s%s"%(b.text[0:1],count),callback_data="%s:%s"%(button,count) ) )
            else:
                update_buttons.append(InlineKeyboardButton(b.text,callback_data=b.callback_data ) )
        return update_buttons

feedback = Feedback()


def __show_buttons__(buttons):
    for  k in buttons:
        print("%s: %s"%(k.text,k.callback_data))

if __name__ == '__main__':
    # feedbacks = {"👍":"赞了一把",
    #             "👎":"踩了一脚",
    #             "🤮":"吐了一地"}

    feedback_text=["👍","👎","🤮"]
    feedback_answer=["赞了一把","踩了一脚","吐了一地"]

    feedback.feedbacks = dict(zip(feedback_text,feedback_answer))

    # 为了测试，关闭反馈和反馈提示 
    feedback.show_alert = False
    feedback.show_answer = False

    # 用feedbacks初始化buttons
    bs = feedback.init_buttons()
    print("初始化buttons:")
    __show_buttons__(bs)

    # 
    now = date.today()
    chat = telegram.Chat(1,'group')
    
    replay_markup = InlineKeyboardMarkup([bs])
    msg = telegram.Message(1,1,now,chat,reply_markup=replay_markup)
    callback = telegram.CallbackQuery(1,1,1,message=msg,data="👎:0")
    bs = feedback.get_updatebuttons(callback)
    print("callback一次")
    __show_buttons__(bs)


    replay_markup = InlineKeyboardMarkup([bs])
    msg = telegram.Message(1,1,now,chat,reply_markup=replay_markup)
    callback = telegram.CallbackQuery(1,1,1,message=msg,data="👎:1")
    bs = feedback.get_updatebuttons(callback)
    print("callback两次")
    __show_buttons__(bs)