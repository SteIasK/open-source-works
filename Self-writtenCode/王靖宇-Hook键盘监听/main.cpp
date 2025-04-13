#include "mainwindow.h"
#include <QApplication>
#include <QCoreApplication>
#include <QFile>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

    // 从文件加载 QSS
    QFile styleFile("E:\\文档\\QTProject\\QHook\\style.qss");  // 使用资源系统

    if (styleFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
        QString styleSheet = QLatin1String(styleFile.readAll());
        a.setStyleSheet(styleSheet);
        styleFile.close();
    } else {
        qWarning() << "无法加载样式表文件:" << styleFile.errorString();
    }

    MainWindow w;
    w.show();
    return a.exec();
}
