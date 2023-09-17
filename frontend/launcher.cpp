#include "launcher.h"
#include "chat.h"
#include "ui_launcher.h"

Launcher::Launcher(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::Launcher)
{
    ui->setupUi(this);
    _socket = std::make_shared<QTcpSocket>();
}

Launcher::~Launcher()
{
    delete ui;
}

void Launcher::on_LoginBtn_clicked()
{
//    _socket->connectToHost("10x1.42.174.249",8080);
    qDebug() << "login\n";
    _socket->connectToHost("localhost",8080);

    if (_socket->waitForConnected(5000)){
        QJsonObject mes;
        mes["Level"] = "system";
        mes["Type"] = "login";
        QJsonObject content;
        content["Username"] = ui->NameInput->text();
        content["Password"] = ui->KeyInput->text();
        mes["Content"] = content;

        QJsonDocument doc(mes);
        _socket->write(doc.toJson());
    }

    if (_socket->waitForReadyRead(5000)){
        QJsonDocument doc = QJsonDocument::fromJson(_socket->readAll());
        if (doc.isNull() || !doc.isObject()){
            throw std::runtime_error("Server Data Error\n");
        }
        QJsonObject recv = doc.object();
        if (recv["Login_bool"].toString() != "true"){
            QString er_info = recv["Login_info"].toString();
            QMessageBox::information(this,"Fatal", er_info);
            return ;
        }
        QVector<QString> name_list;
        int total = recv["User_num"].toInt();
        for(int i {1}; i <= total; ++ i){
            QString key = "user" + QString::number(i);
            name_list.emplace_back(recv[key].toString());
        }
        for(auto i:name_list)
        {
            qDebug() << i << "\n";
        }

        _chat = std::make_shared<Chat>(ui->NameInput->text(),_socket,this);
        _chat->Update(name_list);
        this->close();
        _chat->show();
    }
}

void Launcher::on_RegiBtn_clicked()
{
    qDebug() << "register\n";
    _socket->connectToHost("localhost",8080);
    if (_socket->waitForConnected(5000)){
        QJsonObject mes;
        mes["Level"] = "system";
        mes["Type"] = "register";
        QJsonObject content;
        content["Username"] = ui->NameInput->text();
        content["Password"] = ui->KeyInput->text();
        mes["Content"] = content;

        QJsonDocument doc(mes);
        _socket->write(doc.toJson());
    }

    if (_socket->waitForReadyRead(5000)){
        QJsonDocument doc = QJsonDocument::fromJson(_socket->readAll());

        if (doc.isNull() || !doc.isObject()){
            throw std::runtime_error("Server Data Error\n");
        }

        QJsonObject recv = doc.object();
        if (recv["Regi_bool"].toBool()) {
            QString react = recv["Register_info"].toString();
            QMessageBox::information(this,"Tips", react);
        } else{
            QString react = recv["Register_info"].toString();
            QMessageBox::information(this,"Tips", react);
        }
    }
    _socket->close();
}

