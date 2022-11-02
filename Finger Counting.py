import numpy as np
import cv2


def skin_mask(img):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 48, 80], dtype="uint8")
    upper = np.array([20, 255, 255], dtype="uint8")
    skin_region_HSV = cv2.inRange(hsv_img, lower, upper)
    blurred = cv2.blur(skin_region_HSV, (2, 2))
    ret, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)

    return thresh


def get_cnt_hull(mask_img):
    contours, hierarchy = cv2.findContours(mask_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = max(contours, key=lambda x: cv2.contourArea(x))
    hull = cv2.convexHull(contours)

    return contours, hull


def get_defects(contours):
    hull = cv2.convexHull(contours, returnPoints=False)
    defects = cv2.convexityDefects(contours, hull)

    return defects


cap = cv2.VideoCapture(0)

while cap.isOpened():
    _, img = cap.read()

    try:
        mask_img = skin_mask(img)
        contours, hull = get_cnt_hull(mask_img)
        cv2.drawContours(img, [contours], -1, (255, 255, 0), 2)
        cv2.drawContours(img, [hull], -1, (0, 255, 255), 2)
        defects = get_defects(contours)

        if defects is not None:
            cnt = 0
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i][0]
                start = tuple(contours[s][0])
                end = tuple(contours[e][0])
                far = tuple(contours[f][0])

                a = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                c = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)

                angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))
                if angle <= np.pi / 2:
                    cnt += 1
                    cv2.circle(img, far, 4, [0, 0, 255], -1)
            if cnt > 0:
                cnt += 1
            cv2.putText(img, str(cnt), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.imshow("img", img)
    except:
        pass

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

