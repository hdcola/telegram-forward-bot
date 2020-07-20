# telegram-forward-bot
将你的发言匿名转发到群聊的机器人

这个机器人的作用就是让群里的人通过机器人说话，目标是：

* 完全匿名了发言者的信息
* 规避公共群的个人信息被存档的问题
* 防止群中有他人的帐号出现问题，泄漏你的个人信息

注意，一个帐户注册后，你的`userid`是永远不变的，所以telegram并不真正安全。

## 安装

建议使用venv环境，本项目必须使用Python3，本人不打算再在Python2中做任何测试

```
python3 -m venv py3
source py3/bin/activate
pip install python-telegram-bot
```