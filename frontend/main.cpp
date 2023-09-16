#include "chat.h"
#include "launcher.h"

#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    auto l = std::make_shared<Launcher>();
    l->show();
    return a.exec();
}
