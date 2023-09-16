#ifndef LAUNCHER_H
#define LAUNCHER_H

#include <QDialog>
#include <QDebug>
#include <QResource>
#include <QTcpSocket>
#include <QJsonObject>
#include <QJsonDocument>

#include "chat.h"

namespace Ui {
class Launcher;
}

class Launcher : public QDialog, public std::enable_shared_from_this<Launcher>
{
    Q_OBJECT

public:
    explicit Launcher(QWidget *parent = nullptr);
    ~Launcher();

private slots:
    void on_LoginBtn_clicked();

    void on_ExitBtn_clicked();

private:
    Ui::Launcher *ui;
    std::shared_ptr<QTcpSocket> _socket;
    std::shared_ptr<Chat> _chat;
};

#endif // LAUNCHER_H
