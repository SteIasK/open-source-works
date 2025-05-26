#include <windows.h>
#include <iostream>
#include <map>
#include <queue>
#include <string>

using namespace std;

// 全局变量
static HHOOK keyboardHook = nullptr;
static int status = 0;
static queue<string> output;

// 按键代码到字符串的映射表
static const map<DWORD, string> keyMap = {
    {0x30, "0"}, {0x60, "0"}, {0x31, "1"}, {0x61, "1"}, {0x32, "2"}, {0x62, "2"},
    {0x33, "3"}, {0x63, "3"}, {0x34, "4"}, {0x64, "4"}, {0x35, "5"}, {0x65, "5"},
    {0x36, "6"}, {0x66, "6"}, {0x37, "7"}, {0x67, "7"}, {0x38, "8"}, {0x68, "8"},
    {0x39, "9"}, {0x69, "9"},
    {0x41, "a"}, {0x42, "b"}, {0x43, "c"}, {0x44, "d"}, {0x45, "e"}, {0x46, "f"},
    {0x47, "g"}, {0x48, "h"}, {0x49, "i"}, {0x4A, "j"}, {0x4B, "k"}, {0x4C, "l"},
    {0x4D, "m"}, {0x4E, "n"}, {0x4F, "o"}, {0x50, "p"}, {0x51, "q"}, {0x52, "r"},
    {0x53, "s"}, {0x54, "t"}, {0x55, "u"}, {0x56, "v"}, {0x57, "w"}, {0x58, "x"},
    {0x59, "y"}, {0x5A, "z"},
    {0x6A, "*"}, {0x6B, "+"}, {0x6D, "-"}, {0x6E, "."}, {0x6F, "/"},
    {0x0D, "Enter"}, {0xA0, "Shift"}, {0xA1, "Shift"}, {0x08, "Backspace"}, {0x20, "Space"}
};

// 低级键盘钩子回调函数
LRESULT CALLBACK LowLevelKeyboardProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode >= 0) { // 仅处理有效消息
        KBDLLHOOKSTRUCT* ks = (KBDLLHOOKSTRUCT*)lParam;
        if (ks->flags & 0x80) { // 按键释放事件 (flags: 128 或 129)
            auto it = keyMap.find(ks->vkCode);
            if (it != keyMap.end()) {
                output.push(it->second); // 将按键字符串加入队列
            }
        }
    }
    return CallNextHookEx(nullptr, nCode, wParam, lParam); // 传递消息给下一个钩子
}

// 安装和运行键盘钩子
int hook() {
    // 安装低级键盘钩子
    keyboardHook = SetWindowsHookEx(WH_KEYBOARD_LL, LowLevelKeyboardProc, GetModuleHandle(nullptr), 0);
    if (!keyboardHook) {
        cout << "键盘钩子安装失败" << endl;
        return -1;
    }

    // 消息循环
    MSG msg;
    status = 1;
    while (status == 1) {
        if (PeekMessage(&msg, nullptr, 0, 0, PM_REMOVE)) {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        } else {
            Sleep(1); // 降低 CPU 占用
        }
    }

    // 卸载钩子
    UnhookWindowsHookEx(keyboardHook);
    keyboardHook = nullptr;
    return 0;
}
