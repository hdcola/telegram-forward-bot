# telegram-forward-bot
将你的发言匿名转发到群聊的机器人

这个机器人的作用就是让群里的人通过机器人说话，目标是：

* 完全匿名了发言者的信息
* 规避公共群的个人信息被存档的问题
* 防止群中有他人的帐号出现问题，泄漏你的个人信息
* 通过对发出的内容加入顶和踩的功能让大家为匿名发送什么逐渐达成共识
* 用Bot完成群管理员和Bot管理员的日常设置和操作

注意，一个帐户注册后，你的`userid`是永远不变的，所以telegram并不真正安全。

## 安装

建议使用venv环境，本项目必须使用Python3，本人不打算再在Python2中做任何测试

```
python3 -m venv py3
source py3/bin/activate
pip install python-telegram-bot
```

## 使用

```
mkdir -p ~/.config/forwardbot/
```

将项目中的`config.json`复制到这个目录中。你也可以把配置文件放到你自己喜欢的地方。

### 配置

在`config.json`中配置你的信息

```
{
    "Admin": 0,                   // 管理员用户ID（通常为8~9位数字）
    "Token": "",                  // Bot的Token
    "Feedback": false,            // 是否打开转发时的Feedback
    "Update_shell": "",           // 执行升级的脚本路径，用以支持 /update 命令
    "Restart_shell": "",          // 执行重启服务的脚本路径，用以支持 /restart 命令
    "Publish_Group_ID": []        // 群ID（如：@channel）列表
}
```

有几种典型的使用方法：

* Admin/Publish_Group_ID相同时，你就可以做最简单的测试
* 可以在Publish_Group_ID中加入多个群或频道，这时发送的内容会发到多个你指定的频道里去，列表支持数字、字符串混合

### 管理员命令

当你是Publish_Group_ID中第一个群的管理员时，你可以向Bot发送以下管理指令

* `/help` 显示帮助
* `/feedbackon` 关闭所有匿名发送的反馈
* `/feedbackoff` 打开所有匿名发送的反馈

当你是Bot管理员时，你可以向Bot发送以下管理指令

* `/update` 执行config.json中的Update_shell的命令，参照`gitpull.sh`
* `/restart` 执行config.json中的Resatrt_shell的命令，参照`restart.sh`
* `/getconfig` 得到现有的Bot配置
* `/setfeedback` <str> 设置反馈按钮，每个按钮的文字用逗号分开
* `/setanswer` <str> 设置反馈按钮按下后的提示信息，应该和铵钮数量相同，用逗号分开

## 运行

### 手工运行

```
python main.py
```

会从`~/.config/forwardbot/`目录中读取配置文件和存取data。

也可以使用

```
python main.py -c /usr/local/etc/forwardbot
```

来指定配置文件和data的存储路径。

### 配置systemd运行

在你的venv或Python环境中安装systemd支持，你需要提前确认一下你的操作系统是不是支持systemd。

```
pip install systemd-python
```

修改`forwardbot_service.service`中的内容

```
[Unit]
## 修改为你的说明
Description=Telegram Forward Bot Service

[Service]
## 修改venv和main.py以及config.json目录的路径
ExecStart=/usr/bin/python path/to/your/main.py -c /home/pi/fbot/tssd
Restart=on-failure
Type=notify

[Install]
WantedBy=default.target
```

先将`forwardbot_service.service`文件放入`~/.config/systemd/user/`然后使用以下命令

查看所有的service配置

```
systemctl --user list-unit-files 
```

确定识别后，重新加载一下配置（每次更新service文件后都需要重新加载）

```
systemctl --user daemon-reload
```

启动/停止/查看/重启 service

```
systemctl --user start forwardbot_service
systemctl --user stop forwardbot_service
systemctl --user status forwardbot_service
systemctl --user restart forwardbot_service
```

可以查看服务的output

```
journalctl --user-unit forwardbot_service
```

如果一切正常，先enable service，再打开当前用户的开机启动

```
systemctl --user enable forwardbot_service
sudo loginctl enable-linger $USER
```

如果你不想放到你的用户下运行，可以放到System中。测试都正常后，执行以下操作

```
sudo mv ~/.config/systemd/user/forwardbot_service /etc/systemd/system/
sudo chown root:root /etc/systemd/system/forwardbot_service
sudo chmod 644 /etc/systemd/system/forwardbot_service
sudo systemctl daemon-reload
sudo systemctl enable forwardbot_service
sudo systemctl start forwardbot_service
```

## 感谢

* 感谢 https://github.com/python-telegram-bot/python-telegram-bot
* 代码不少使用了 https://github.com/Netrvin/telegram-submission-bot 感谢他的轮子
* 有如何在systemd中启动Python的程序感谢 https://github.com/torfsen/python-systemd-tutorial 的文章
* 感谢 https://github.com/systemd/python-systemd