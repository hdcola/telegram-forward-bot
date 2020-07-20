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

## 使用

```
mkdir ~/.forwardbot/
```

将项目中的`config.json`和`data.json`复制到这个目录中。你也可以把配置文件放到你自己喜欢的地方。

### 配置

在`config.json`中配置你的信息

```
{
    "Admin": 0,                   //管理员用户ID（通常为8~9位数字）
    "Token": "",                  //Bot的Token
    "Group_ID": [],               //审核群或用户的ID
    "Publish_Group_ID": []        //群ID（如：@channel）列表
}
```

有几种典型的使用方法：

* Admin/Group_ID/Publish_Group_ID相同时，你就可以做最简单的测试
* 可以在Publish_Group_ID中加入多个群或频道，这时发送的内容会发到多个你指定的频道里去，列表支持数字、字符串混合

当用户存在于目标Publish_Group_ID中，哪么不需要审核就会直发，当用户不存在于目标群中，哪么会通过Group_ID的群审核后才能发送出来。

## 运行

```
python main.py
```

会从`~/.forwardbot`目录中读取配置文件和存取data。

也可以使用

```
python main.py -c /usr/local/etc/forwardbot
```

来指定配置文件和data的存储路径。
