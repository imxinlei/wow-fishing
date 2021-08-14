import time
import math
import threading
import random
from array import array

import win32api, win32gui, win32con

class WowWindow:

    handler = 0
    lastCheckAt = time.time()

    left = 0
    top = 0
    right = 0
    bottom = 0
    height = 0
    top = 0

    def __init__(self):
        if self._getWowWindow() == 0:
            self._startNewWow()

    def _getWowWindow(self):
        self.handler = win32gui.FindWindow(None, '魔兽世界')
        if self.handler != 0:
            self.left, self.top, self.right, self.bottom = win32gui.GetWindowRect(self.handler)
            self.width = self.right - self.left
            self.height = self.bottom - self.top
            print(self.handler, self.left, self.top, self.right, self.bottom)
        return self.handler

    def _startNewWow(self):
        battleHandler = win32gui.FindWindow(None, '暴雪战网')
        if battleHandler == 0:
            raise Exception("battle client is not start", 1)

        win32gui.ShowWindow(battleHandler, 5)
        win32gui.SetForegroundWindow(battleHandler)
        time.sleep(1)

        print('launching from battle net...')
        win32gui.PostMessage(battleHandler, win32con.WM_KEYDOWN, 13, 0)
        win32gui.PostMessage(battleHandler, win32con.WM_KEYUP, 13, 0)

        time.sleep(15)

        if self._getWowWindow() == 0:
            raise Exception("wow client starts failed", 1)

        print('wow window starts success')
        print('choosing character...')
        win32gui.PostMessage(self.handler, win32con.WM_KEYDOWN, 13, 0)
        win32gui.PostMessage(self.handler, win32con.WM_KEYUP, 13, 0)

        time.sleep(10)
        return self.handler

    def testLogout(self):
        if time.time() - self.lastCheckAt <= 180:
            return self.handler

        self.lastCheckAt = time.time()
        self.press(27)
        self.press(27)
        self.press(27)

        time.sleep(3)

        if self._getWowWindow() != 0:
            # k and esc to close system menu
            self.press(75)
            time.sleep(0.5)
            self.press(27)
            return self.handler

        print('wow is currently logged out')
        return self._startNewWow()

    def press(self, key):
        if self.handler != 0:
            win32gui.PostMessage(self.handler, win32con.WM_KEYDOWN, key, 0)
            win32gui.PostMessage(self.handler, win32con.WM_KEYUP, key, 0)

    def moveTo(self, percX, percY):
        if self.handler != 0:
            win32api.SetCursorPos((int(self.left + self.width * percX), int(self.top + self.height * percY)))

    def rclick(self, percX, percY):
        if (self.handler != 0):
            param = win32api.MAKELONG(int(self.width * percX - 4), int(self.height * percY - 30))
            win32gui.PostMessage(self.handler, win32con.WM_RBUTTONDOWN, 0, param)
            win32gui.PostMessage(self.handler, win32con.WM_RBUTTONUP, 0, param)
