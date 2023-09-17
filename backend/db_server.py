from twisted.internet import protocol, reactor
import sqlite3
import json

class User:
    def __init__(self, uid, ip, port, transport, user_name='default'):
        self.uid = uid
        self.user_name = user_name + str(uid)
        self.ip = ip
        self.port = port
        self.transport = transport


class Echo(protocol.Protocol):
    user_list = []
    uid_ptr = 0

    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

    # create a table to save the username and password
    def createTable(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT
            )
        ''')

    def UpdateUserListMes(self):
        resp = {"Level": "system", "Type": "login_back", "Login_bool": "true", "User_num": len(self.user_list)}
        for i in range(len(self.user_list)):
            resp['user' + str(i + 1)] = self.user_list[i].user_name
        return resp


    def MesBoardcast(self,mes):
        for i in range(len(self.user_list)):
            self.user_list[i].transport.write(json.dumps(mes).encode("utf-8"))
        print(mes)

    def connectionMade(self):
        ip = self.transport.getPeer().host
        port = self.transport.getPeer().port
        user = User(self.uid_ptr, ip, port, self.transport)
        self.user_list.append(user)

    def dataReceived(self, data):
        response = self.processData(data)

    def handleLogin(self, data):
        print("Login")
        username = data['Content']['Username']
        password = data['Content']['Password']

        # Retrieve the user from the database
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()

        if row and row[2] == password:
            # Username and password match
            # Send a response to the client
            response = {
                "Level": "system",
                "Type": "login_back",
                "Login_bool": "true",
                "User_num": len(self.user_list)
            }
            # Update the username for the connected user
            for user in self.user_list:
                if user.transport == self.transport:
                    user.user_name = username
                    break

            # Broadcast the response to all users
            self.MesBoardcast(self.UpdateUserListMes())
        else:
            # Username or password is incorrect
            response = {
                "Level": "system",
                "Type": "login_back",
                "Login_bool": "false"
            }
            # Send the response only to the current client
            self.transport.write(json.dumps(response).encode("utf-8"))

    def handleRegister(self, data):
        print("register")
        username = data['Content']['Username']
        password = data['Content']['Password']

        # Check if the username already exists in the database
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()

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
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()

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

    def handleMessage(self, data):
        print("Message")
        from_name = data["Content"]["Sender"]
        mes = data["Content"]["Message"]
        response = {
            "Level": "user",
            "Type": "message",
            "Content": {"Sender": from_name, "Message": mes},
        }
        self.MesBoardcast(response)

    def processData(self, data):
        json_data = json.loads(data.decode("utf-8"))
        if json_data['Level'] == 'system' and json_data['Type'] == 'login':
            self.handleLogin(json_data)
        elif json_data['Level'] == 'system' and json_data['Type'] == 'register':
            self.handleRegister(json_data)
        elif json_data['Level'] == 'user' and json_data['Type'] == 'message':
            self.handleMessage(json_data)
        else:
            print("Unknown Message")
            print(json_data)
            pass

    def connectionLost(self, reason):
        # 连接断开时停止reactor
        for user in self.user_list:
            if user.transport == self.transport:
                self.user_list.remove(user)
                self.MesBoardcast(self.UpdateUserListMes())
                break
        # reactor.stop()


class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()


if __name__ == "__main__":
    # 启动Twisted服务器
    reactor.listenTCP(8080, EchoFactory())
    reactor.run()
