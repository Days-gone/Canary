#ifndef CHAT_H
#define CHAT_H

#include <QMainWindow>
#include <QJsonObject>
#include <QJsonDocument>
#include <QTcpSocket>

QT_BEGIN_NAMESPACE
namespace Ui { class Chat; }
QT_END_NAMESPACE

class Chat : public QMainWindow
{
    Q_OBJECT


public:
    explicit Chat(QString selfname,std::shared_ptr<QTcpSocket>sock,QWidget *parent = nullptr);
    ~Chat();
    void Update(QVector<QString> vec);

private slots:
    void DataReceived();
    void on_Sendbtn_clicked();
    void AddMessage(QString username, QString mes);

private:
    Ui::Chat *ui;
    std::shared_ptr<QTcpSocket> _sock;
    QString _self_name;
};
#endif // CHAT_H
