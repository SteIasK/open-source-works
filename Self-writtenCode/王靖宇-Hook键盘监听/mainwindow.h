#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTimer>

QT_BEGIN_NAMESPACE
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();
public:
    void writeLog();
    QTimer *timer;
protected:
    void closeEvent(QCloseEvent *event) override;

private slots:
    void on_startButton_clicked();

    void on_stopButton_clicked();

    void on_clearButton_clicked();

    void on_saveButton_clicked();

private:
    Ui::MainWindow *ui;
};
#endif // MAINWINDOW_H
