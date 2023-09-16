#include "chat.h"
#include "ui_chat.h"

Chat::Chat(QString selfname,std::shared_ptr<QTcpSocket>sock,QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::Chat)
    , _sock(sock)
    ,_self_name(selfname)
{
    ui->setupUi(this);
    connect(_sock.get(),&QTcpSocket::readyRead,this,&Chat::DataReceived);
}

Chat::~Chat()
{
    delete ui;
}

void Chat::Update(QVector<QString> vec)
{
    ui->UserList->clear();
    for(auto &i :vec){
        ui->UserList->addItem(i);
    }
}


void Chat::DataReceived(){
    QJsonDocument doc = QJsonDocument::fromJson(_sock->readAll());
    if (doc.isNull() || !doc.isObject()){
        throw std::runtime_error("Server Data Error\n");
    }
    QJsonObject recv = doc.object();

    if (recv["Level"] == "system"){
        if(recv["Type"] == "login_back"){
            QVector<QString> name_list;
            int total = recv["user_num"].toInt();
            for(int i {1}; i <= total; ++ i){
                QString key = "user" + QString::number(i);
                name_list.emplace_back(recv[key].toString());
            }
            Update(name_list);
        }
    }
    else{
        if (recv["Type"] == "message"){
            QString sender = recv["Content"].toObject()["Sender"].toString();
            QString message = recv["Content"].toObject()["Message"].toString();
            if (sender != _self_name)AddMessage(sender,message);
        }
    }
}


void Chat::on_Sendbtn_clicked()
{
    QJsonObject mes;
    mes["Level"] = "user";
    mes["Type"] = "message";
    QJsonObject content;
    content["Message"] = ui->Input->toPlainText();
    content["Sender"] = _self_name;
    mes["Content"] = content;

    QJsonDocument doc(mes);
    _sock->write(doc.toJson());
    AddMessage(_self_name,ui->Input->toPlainText());

}

void Chat::AddMessage(QString username, QString mes)
{
    ui->ShowLog->append(username + ":\n" + mes);
    ui->Input->clear();
}

