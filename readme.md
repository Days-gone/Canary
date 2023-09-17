# Canary-多人聊天室
# 关键字：
 **QT、OOP、Twisted、SQLite3** 
# 环境配置：
 **QT**  >= 6.5 <br>
 **Python**  >= 3.10 <br>
 **Twisted** 
# 启动方法：
1、在frontend/launcher.cpp中修改你的服务器IP地址。<br>
2、在你的服务器上运行backend/db_server.py，请确保对应端口允许tcpsocket连接接入<br>
3、运行QT生成的chat可执行文件，先注册再登陆