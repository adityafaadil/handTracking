import cv2
import time
import pyautogui
import autopy
import numpy as np
import HandTrackingModule as Htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


def set_scroll(set_fingers, set_lm_list, set_img):
    if set_fingers == [0, 1, 0, 0, 0]:
        cv2.circle(set_img, (set_lm_list[8][1], set_lm_list[8][2]), 7, (0, 255, 0), cv2.FILLED)
        pyautogui.scroll(100)
    elif fingers == [0, 1, 1, 0, 0]:
        cv2.circle(set_img, (set_lm_list[8][1], set_lm_list[8][2]), 7, (0, 255, 0), cv2.FILLED)
        cv2.circle(set_img, (set_lm_list[12][1], set_lm_list[12][2]), 7, (0, 255, 0), cv2.FILLED)
        pyautogui.scroll(-100)


def set_volume(set_img):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # Set Value Min and Max for Volume Bar
    h_min = 50
    h_max = 300
    slide_bar = 400
    max_bar = 150
    percent_max = 100
    percent_min = 0

    # Jarak Antara Ibu Jari dan Kelingking
    length, set_img, line_loc = detector.find_distance(4, 20, set_img)

    # Set Volume Bar
    vol_bar = np.interp(length, [h_min, h_max], [slide_bar, max_bar])
    vol_per = np.interp(length, [h_min, h_max], [percent_min, percent_max])
    smoothness = 4
    vol_per = smoothness * round(vol_per / smoothness)
    volume.SetMasterVolumeLevelScalar(vol_per / 100, None)

    print(vol_per, length)

    if vol_per == 0:
        cv2.circle(set_img, (line_loc[4], line_loc[5]), 11, (0, 0, 255), cv2.FILLED)

    elif vol_per == 100:
        cv2.circle(set_img, (line_loc[4], line_loc[5]), 11, (0, 0, 255), cv2.FILLED)

    # Showing Bar Volume
    cv2.rectangle(set_img, (30, 150), (55, 400), (255, 255, 255), 3)
    cv2.rectangle(set_img, (30, int(vol_bar)), (55, 400), (255, 255, 255), cv2.FILLED)
    cv2.putText(set_img, f'{int(vol_per)}%', (25, 430), cv2.FONT_HERSHEY_COMPLEX, 0.9, (255, 255, 255), 3)


detector = Htm.HandDetector(max_hands=2, detection_con=0.85, track_con=0.8)
mode = ""


# Set Tinggi dan Lebar Frame CV
w_cam, h_cam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, w_cam)
cap.set(4, h_cam)

# Size Screen (1366 x 768)
w_scr, h_scr = autopy.screen.size()
frame_reduction = 100
p_time = 0


# previous and Current loc of x and y
p_locX, p_locY = 0, 0
c_locX, c_locY = 0, 0


while True:

    # Find the landmarks
    success, img = cap.read()
    hands, img = detector.find_hands(img)
    lm_list = detector.find_position(img, z_axis=True, draw=False)
    fingers = []

    # Checking Fingers Up Or No
    if len(lm_list) != 0:
        fingers = detector.fingers_up()

        # Checking Gesture Hand
        if (fingers == [0, 0, 0, 0, 0]) & (detector.active == 0):
            mode = 'N'
        elif (fingers == [0, 1, 0, 0, 0] or fingers == [0, 1, 1, 0, 0]) & (detector.active == 0):
            mode = 'Scroll'
            detector.active = 1
        elif (fingers == [1, 0, 0, 0, 1]) & (detector.active == 0):
            mode = 'Volume'
            detector.active = 1
        elif (fingers == [1, 1, 0, 0, 0]) & (detector.active == 0):
            mode = 'Cursor'
            detector.active = 1

    # Scroll
    if mode == 'Scroll':
        detector.active = 1
        if fingers == [0, 0, 0, 0, 0]:
            detector.active = 0
            mode = 'N'
            print(mode)
        else:
            if len(lm_list) != 0:
                set_scroll(fingers, lm_list, img)

    # Volume
    if mode == 'Volume':
        detector.active = 1

        # Checking Fingers Up Or Not
        if len(lm_list) != 0:
            if fingers[-1] == 0:
                detector.active = 0
                mode = 'N'
                print(mode)
            else:
                set_volume(img)
        print(fingers)

    # Cursor
    if mode == 'Cursor':
        detector.active = 1
        drag = True
        cv2.rectangle(img, (20, 20), (620, 450), (255, 255, 255), 3)
        if fingers == [0, 0, 0, 0, 0]:
            detector.active = 0
            mode = 'N'
            print(mode)
        else:
            if len(lm_list) != 0:
                # Posisi Jari Telunjuk
                x1, y1 = lm_list[8][1], lm_list[8][2]

                # Convert Coordinates because my screen window is 1366x720
                # and cv window is 640x480 and so have to convert agar sesuai
                x = np.interp(x1, (frame_reduction, w_cam - frame_reduction), (0, w_scr))
                y = np.interp(y1, (frame_reduction, w_cam - frame_reduction), (0, w_scr))

                # Memperhalus Gerakan Cursor
                c_locX = p_locX + (x - p_locX) / 8
                c_locY = p_locY + (y - p_locY) / 8

                # Membuat Dot di Ujung Jari Tangan (Ibu Jari, Jari Telunjuk, Jari Tengah, Jari Kelingking)
                cv2.circle(img, (lm_list[20][1], lm_list[20][2]), 7, (0, 255, 0), cv2.FILLED)
                cv2.circle(img, (lm_list[8][1], lm_list[8][2]), 7, (0, 255, 0), cv2.FILLED)
                cv2.circle(img, (lm_list[4][1], lm_list[4][2]), 7, (0, 255, 0), cv2.FILLED)

                # Koordinat Untuk Menggerakan Mouse
                autopy.mouse.move(w_scr - c_locX, c_locY)
                p_locX, p_locY = c_locX, c_locY
                print(p_locX, p_locY)

                # Klik kiri
                if fingers == [0, 1, 0, 0, 0]:
                    cv2.circle(img, (lm_list[4][1], lm_list[4][2]), 10, (0, 0, 255), cv2.FILLED)  # thumb
                    pyautogui.click()

                # Klik Kanan
                if fingers[1] == 1 and fingers[4] == 1:
                    cv2.circle(img, (lm_list[20][1], lm_list[20][2]), 10, (0, 0, 255), cv2.FILLED)
                    pyautogui.click(button='right')
            print(fingers)

    # FPS
    c_time = time.time()
    fps = 1 / ((c_time + 0.01) - p_time)
    p_time = c_time
    frame_flip = cv2.flip(img, 1)
    cv2.putText(frame_flip, f'FPS:{int(fps)}', (480, 50), cv2.FONT_ITALIC, 1, (255, 255, 255), 2)

    # Menampilkan Screen
    cv2.imshow('Virtual Mouse', frame_flip)
    if cv2.waitKey(1) == chr(27):
        cv2.destroyAllWindows()
