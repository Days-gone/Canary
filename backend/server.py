from twisted.internet import protocol, reactor
from twisted.internet.protocol import ClientFactory
import json

user_list = []
uid_ptr = 0

def UpdateUserListMes():
    resp = {"Level":"system","Type":"login_back","user_num":len(user_list)}
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
        # rule: key is Pascal Name and value is all-little letter
        json_data = json.loads(data.decode("utf-8"))
        if (json_data['Level'] == 'system'):
            print("system call:")
            if (json_data['Type'] == 'login'):
                resp = {"Level":"system","Type":"login_back","user_num":len(user_list)}
                for i in range(len(user_list)):
                    if user_list[i].transport == self.transport:
                        user_list[i].user_name = json_data['Content']['Username']
                    resp['user' + str(i + 1)] = user_list[i].user_name
                MesBoardcast(resp)
        elif (json_data["Level"] == 'user'):
            from_name = json_data["Content"]["Sender"]
            resp = {"Level":"user","Type":"message"}
            # recv_name = json_data["Content"]["Recevier"]
            mes = json_data["Content"]["Message"]
            resp["Content"] = {"Sender":from_name,"Message":mes}
            MesBoardcast(resp)
        else:
            raise AttributeError("Level Not Exist")
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
