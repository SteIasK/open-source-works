#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "hook.cpp"
#include <QFileDialog>
#include <QMessageBox>
#include <QCloseEvent>
#include <QSystemTrayIcon>
#include <QIcon>
#include <QStyle>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    this->setWindowFlags(windowFlags() & ~Qt::WindowMaximizeButtonHint);
    this->setFixedSize(800, 600);

    ui->setupUi(this);
    ui->textEdit->setReadOnly(true);  // QTextEdit
    ui->label->setStyleSheet("QLabel{color:rgb(255,255,255);}");

    QSystemTrayIcon *trayIcon = new QSystemTrayIcon(this);
    QIcon icon = QApplication::style()->standardIcon(QStyle::SP_MessageBoxInformation);
    trayIcon->setIcon(icon);
    trayIcon->setToolTip("Hook正在后台运行");

    // 点击托盘图标恢复窗口
    connect(trayIcon, &QSystemTrayIcon::activated, [this](){
        this->showNormal();
    });

    trayIcon->show();

    // 创建定时器并连接信号槽
    timer = new QTimer(this);
    connect(timer, &QTimer::timeout, this, &MainWindow::writeLog);
    timer->start(100);  // 每100毫秒检查一次，可以根据需要调整时间间隔
}

MainWindow::~MainWindow()
{
    status=0;
    delete ui;
}

void MainWindow::closeEvent(QCloseEvent *event) {
    QMessageBox msgBox(this);
    msgBox.setWindowFlags(msgBox.windowFlags() & ~Qt::WindowCloseButtonHint);
    msgBox.setWindowTitle("程序退出");
    msgBox.setText("请选择操作方式：");

    // 自定义按钮（文字 + 角色）
    QPushButton *hideBtn = msgBox.addButton("隐藏到托盘", QMessageBox::YesRole);
    QPushButton *exitBtn = msgBox.addButton("直接退出", QMessageBox::NoRole);
    QPushButton *cancelBtn = msgBox.addButton("取消", QMessageBox::RejectRole);

    msgBox.setDefaultButton(hideBtn); // 默认选中"隐藏到托盘"
    msgBox.exec(); // 显示对话框

    if (msgBox.clickedButton() == hideBtn) {
        this->hide();
        event->ignore();
    } else if (msgBox.clickedButton() == exitBtn) {
        event->accept();
        QApplication::quit();
    } else {
        event->ignore(); // 取消操作
    }
}

void MainWindow::on_startButton_clicked()
{
    if (status==0)
    {
        status=1;
        output.push("开始监听");
        hook();
    }
    else
    {
        output.push("已经在运行中了");
    }
}


void MainWindow::on_stopButton_clicked()
{
    if (status==1)
    {
        output.push("结束监听");
        status=0;
    }
}

void MainWindow::writeLog()
{
    while (!output.empty())
    {
        string tmp="检测到输入："+output.front();
        ui->textEdit->append(QString::fromStdString(tmp));
        output.pop();
    }
}

void MainWindow::on_clearButton_clicked()
{
    ui->textEdit->clear();  // 清空 QTextEdit
}


void MainWindow::on_saveButton_clicked()
{
    // 获取 QTextEdit 的纯文本内容
    QString text = ui->textEdit->toPlainText();

    // 打开文件对话框让用户选择保存路径
    QString fileName = QFileDialog::getSaveFileName(
        this,
        "保存日志文件",
        QDir::homePath(),
        "文本文件 (*.txt);;所有文件 (*)"
        );

    if (fileName.isEmpty()) {
        return; // 用户取消保存
    }

    QFile file(fileName);
    if (file.open(QIODevice::WriteOnly | QIODevice::Text)) {
        QTextStream out(&file);
        out << text;  // 写入文件
        file.close();
        QMessageBox::information(this, "成功", "日志已保存到文件！");
    } else {
        QMessageBox::warning(this, "错误", "无法保存文件！");
    }
}

