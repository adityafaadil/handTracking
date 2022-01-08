import cv2
import mediapipe as mp
import time
import math

# previous loc of x and y
class HandDetector:
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        self.mode = mode
        self.maxHands = max_hands
        self.detectionCon = detection_con
        self.trackCon = track_con
        self.key_points = [4, 8, 12, 16, 20]
        self.active = 0
        self.fingers = []
        self.lm_list = []

        # Detect The Hands
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode, max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True, flipType=True):
        """
        Finds hands in a BGR image.
        :param img: Image to find the hands in.
        :param draw: Flag to draw the output on the image.
        :return: Image with or without drawings
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        all_hands = []
        h, w, c = img.shape
        if self.results.multi_hand_landmarks:
            for handType, handLms in zip(self.results.multi_handedness, self.results.multi_hand_landmarks):
                myHand = {}
                # lmList
                mylmList = []
                xList = []
                yList = []
                for id, lm in enumerate(handLms.landmark):
                    px, py = int(lm.x * w), int(lm.y * h)
                    mylmList.append([px, py])
                    xList.append(px)
                    yList.append(py)

                # bbox
                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                boxW, boxH = xmax - xmin, ymax - ymin
                bbox = xmin, ymin, boxW, boxH
                cx, cy = bbox[0] + (bbox[2] // 2), \
                         bbox[1] + (bbox[3] // 2)

                myHand["lmList"] = mylmList
                myHand["bbox"] = bbox
                myHand["center"] = (cx, cy)

                # draw
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
                    cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                                  (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                                  (255, 255, 255), 1)

        if draw:
            return all_hands, img
        else:
            return all_hands

    def find_position(self, img, hand_no=0, draw=True, color=(255, 0, 255), z_axis=False):
        self.lm_list = []
        cx, cy = 0, 0

        # Checking Multiple Hand
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_no]
            for i, lm in enumerate(my_hand.landmark):

                #  print(id, lm)
                h, w, c = img.shape
                if not z_axis:
                    cx, cy = int(lm.x * w), int(lm.y * h)

                    # print(i, cx, cy)
                    self.lm_list.append([i, cx, cy])
                elif z_axis:
                    cx, cy, cz = int(lm.x * w), int(lm.y * h), round(lm.z, 3)

                    # print(i, cx, cy, cz)
                    self.lm_list.append([i, cx, cy, cz])
                if draw:
                    cv2.circle(img, (cx, cy), 5, color, cv2.FILLED)
        return self.lm_list

    def fingers_up(self):
        fingers = []

        # Thumb
        if self.lm_list[self.key_points[0]][1] > self.lm_list[self.key_points[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Fingers
        for i in range(1, 5):
            if self.lm_list[self.key_points[i]][2] < self.lm_list[self.key_points[i] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def find_distance(self, p1, p2, img, draw=True):

        # Get Distance Key Points
        x1, y1 = self.lm_list[p1][1], self.lm_list[p1][2]
        x2, y2 = self.lm_list[p2][1], self.lm_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            # Draw Dot and Line on Key Points
            cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)

        # Distance Two Points
        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]


def main():
    p_time = 0
    cap = cv2.VideoCapture(0)
    detector = HandDetector(max_hands=2)
    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        img = detector.find_hands(img)
        lm_list = detector.find_position(img, z_axis=True, draw=False)
        if len(lm_list) != 0:
            print(lm_list[4])

        c_time = time.time()
        fps = 1 / (c_time - p_time)
        p_time = c_time

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
