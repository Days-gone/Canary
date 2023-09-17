from twisted.internet import protocol, reactor
from twisted.internet.protocol import ClientFactory
import sqlite3
import json

user_list = []
uid_ptr = 0
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# create a table to save the username and password
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
''')


def UpdateUserListMes():
    resp = {"Level":"system","Type":"login_back","Login_bool":"true","User_num":len(user_list)}
    for i in range(len(user_list)):
        resp['user' + str(i + 1)] = user_list[i].user_name
    return resp

def MesBoardcast(mes):
    for i in range(len(user_list)):
        user_list[i].transport.write(json.dumps(mes).encode("utf-8"))
    print(mes)


class User:
    def __init__(self, uid, ip, port, transport,user_name = 'default'):
        self.uid = uid
        self.user_name = user_name + str(uid)
        self.ip = ip
        self.port = port
        self.transport = transport

    def Lost(self):
        user_list.remove(self)

class Echo(protocol.Protocol):
    def connectionMade(self):
        ip = self.transport.getPeer().host
        port = self.transport.getPeer().port
        user = User(uid_ptr, ip, port, self.transport)
        user_list.append(user)

    def dataReceived(self, data):
        response = self.processData(data)

    def processData(self, data):
        json_data = json.loads(data.decode("utf-8"))
        if json_data['Level'] == 'system' and json_data['Type'] == 'login':
            print("Login")
            username = json_data['Content']['Username']
            password = json_data['Content']['Password']

            # Retrieve the user from the database
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()

            if row and row[2] == password:
                # Username and password match
                # Send a response to the client
                response = {
                    "Level": "system",
                    "Type": "login_back",
                    "Login_bool": "true",
                    "Login_info": "Login Succeeded!",
                    "User_num": len(user_list)
                }
                # Update the username for the connected user
                for user in user_list:
                    if user.transport == self.transport:
                        user.user_name = username
                        break

                # Broadcast the response to all users
                MesBoardcast(UpdateUserListMes())
            else:
                # Username or password is incorrect
                response = {
                    "Level": "system",
                    "Type": "login_back",
                    "Login_bool": "false",
                    "Login_info": "Password Dismatch!"
                }
                # Send the response only to the current client
                self.transport.write(json.dumps(response).encode("utf-8"))

        elif json_data['Level'] == 'system' and json_data['Type'] == 'register':
            print("register")
            username = json_data['Content']['Username']
            password = json_data['Content']['Password']

            # Check if the username already exists in the database
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()

            if row:
                # Username already exists
                response = {
                    "Level": "system",
                    "Type": "register_back",
                    "Register_bool": "false",
                    "Register_info": "Username already exists. Please choose a different username."
                }
                # Send the response only to the current client
                print("register fail")
                self.transport.write(json.dumps(response).encode("utf-8"))
            else:
                # Insert the new user into the database
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()

                # Send a response to the client
                response = {
                    "Level": "system",
                    "Type": "register_back",
                    "Register_bool": "true",
                    "Register_info": "Registration successful!"
                }
                # Send the response only to the current client
                print("register done")
                self.transport.write(json.dumps(response).encode("utf-8"))

        elif json_data['Level'] == 'user' and json_data['Type'] == 'message':
                print("Message")
                from_name = json_data["Content"]["Sender"]
                mes = json_data["Content"]["Message"]
                response = {
                    "Level": "user",
                    "Type": "message",
                    "Content":{"Sender":from_name,"Message":mes},
                }
                MesBoardcast(response)
        else:
            print("Unknown Message")
            print(json_data)
            pass
    
    def connectionLost(self, reason):
        # 连接断开时停止reactor
        for user in user_list:
            if user.transport == self.transport:
                user.Lost()
                MesBoardcast(UpdateUserListMes())
                break
        # reactor.stop()
        

class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()


class ForwardingClientProtocol(protocol.Protocol):
    def __init__(self, message):
        self.message = message

    def connectionMade(self):
        # 连接成功后，发送消息
        self.transport.write(self.message)

    def connectionLost(self, reason):
        # 连接断开时停止reactor
        reactor.stop()


class ForwardingClientFactory(ClientFactory):
    def __init__(self, message):
        self.protocol = ForwardingClientProtocol(message)


# 启动Twisted服务器
reactor.listenTCP(8080, EchoFactory())
reactor.run()