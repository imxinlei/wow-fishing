import time
import math
import random
import ctypes
from array import array

from win32gui import GetWindowText, GetForegroundWindow, GetWindowRect, GetCursorInfo

import wow_window

dll = ctypes.windll.LoadLibrary('wasapi/wasapi.dll')

startAudioCapture = dll.startCapture
startAudioCapture.argtypes = []
startAudioCapture.restype = ctypes.c_int

stopAudioCapture = dll.stopCapture
stopAudioCapture.argtypes = []
stopAudioCapture.restype = ctypes.c_int

getPeakVolume = dll.peakVolume
getPeakVolume.argtypes = []
getPeakVolume.restype = ctypes.c_float

if __name__ == "__main__":
    try:
        wow = wow_window.WowWindow()

        if startAudioCapture() != 0:
            raise Exception("start audio capture failed", 1)

        while True:

            wow.testLogout()

            if GetWindowText(GetForegroundWindow()) != "魔兽世界":
                print("wow window is not activated.")
                time.sleep(2)
                continue

            # destroy trash & open shells & start fish
            wow.press(50)
            time.sleep(1)
            wow.press(51)
            time.sleep(0.5)
            wow.press(49)

            # get default cursor
            wow.moveTo(0.05, 0.05)
            time.sleep(0.5)
            normalCursor = GetCursorInfo()[1]

            startedAt = time.time()
            found = False
            point = 0, 0

            time.sleep(1)

            # find the float by search for 6 circles
            #
            for i in range(6):
                if found:
                    break

                r = 3 * i
                pointsCount = math.floor(1.4 * r + 3.75)

                for j in range(pointsCount):
                    angle = j * 360 / pointsCount
                    point = (50 + r * math.cos(angle * 3.14 / 180), 50 + r * math.sin(angle * 3.14 / 180))
                    wow.moveTo(point[0] / 100, point[1] / 100)
                    time.sleep(0.04)

                    if GetCursorInfo()[1] != normalCursor:
                        found = True
                        break

            if not found:
                continue

            getPeakVolume()
            while time.time() - startedAt <= 26:
                v = getPeakVolume()
                if v > 0.14:
                    # print(v)
                    wow.rclick(point[0] / 100, point[1] / 100)
                    break
                time.sleep(0.5)

    except KeyboardInterrupt:
        print("Ctrl-c received! Sending kill to threads...")

    except Exception:
        stopCapture()
        print("terminated")
