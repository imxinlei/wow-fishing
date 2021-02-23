import time
import math
import threading
import random
from array import array

import pyaudio
import pyautogui
from win32gui import GetWindowText, GetForegroundWindow, GetWindowRect, GetCursorInfo

import wow_window

class STATUS():
    IDLE = 0
    FINDING = 1
    FOUND = 2
    TERMINATED = 3

SOUND_CHUNK_SIZE = 1024
MIN_VOLUME = 1000

status = STATUS.IDLE
startedAt = 0

def listen():
    global status
    global startedAt

    p = pyaudio.PyAudio()
    stream = p.open(
        format = pyaudio.paInt16,
        channels = 1,
        rate = 44100,
        input = True,
        frames_per_buffer = SOUND_CHUNK_SIZE,
    )

    continuesCount = 0

    while status != STATUS.TERMINATED:
        chunk = array('h', stream.read(SOUND_CHUNK_SIZE))
        if status != STATUS.FOUND:
            continuesCount = 0
            continue

        vol = max(chunk)
        if vol >= MIN_VOLUME:
            continuesCount = continuesCount + 1
            if continuesCount > 2:
                time.sleep(random.uniform(0.1, 0.6))
                pyautogui.click(button="right")
                status = STATUS.IDLE
                # print("got a fish!")
        else:
            continuesCount = 0

if __name__ == "__main__":

    listen_t = threading.Thread(target=listen)
    listen_t.start()

    wow = wow_window.WowWindow()

    try:
        while True:

            wow.testLogout()

            if GetWindowText(GetForegroundWindow()) != "魔兽世界":
                print("wow window is not activated.")
                time.sleep(2)
                continue

            wow.press(50)
            time.sleep(1)

            wow.press(51)
            time.sleep(0.5)

            status = STATUS.FINDING

            # go through the edges of 10 circles around the center
            #
            wow.press(49)
            wow.moveTo(0.05, 0.05)
            time.sleep(0.5)
            normalCursor = GetCursorInfo()[1]

            startedAt = time.time()
            time.sleep(1)

            # find the float by search for 6 circles
            #
            for i in range(6):
                if status != STATUS.FINDING:
                    break

                r = 3 * i
                pointsCount = math.floor(1.4 * r + 3.75)

                for j in range(pointsCount):
                    angle = j * 360 / pointsCount
                    point = (50 + r * math.cos(angle * 3.14 / 180), 50 + r * math.sin(angle * 3.14 / 180))
                    wow.moveTo(point[0] / 100, point[1] / 100)
                    time.sleep(0.04)

                    if GetCursorInfo()[1] != normalCursor:
                        status = STATUS.FOUND
                        break

            if status != STATUS.FOUND:
                # print("float not found")
                status = STATUS.IDLE
                continue

            while status == STATUS.FOUND and time.time() - startedAt <= 26:
                time.sleep(1)

        status = STATUS.TERMINATED

    except KeyboardInterrupt:
        print("Ctrl-c received! Sending kill to threads...")
        status = STATUS.TERMINATED
