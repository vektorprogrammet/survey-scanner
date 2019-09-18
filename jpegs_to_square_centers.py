import cv2
import numpy as np
import imutils

resizeFactor = 0.5

square_side = 36.5  # TODO: This value depends on resize factor: this is for 0.5
side_thresh = 10
square_perimeter = 4 * square_side
perimeter_thresh = 4 * side_thresh
square_area = square_side ** 2
area_thresh = side_thresh ** 2


def scan_for_squares(image_filenames) -> np.ndarray:
    print('Starting scan_for_lines of %d images' % len(image_filenames))
    centers = []
    for i, fname in enumerate(image_filenames):
        print('Scanning %s (%d of %d)' % (fname, i + 1, len(image_filenames)))
        orig = cv2.imread(fname)
        resize = cv2.resize(orig, (0, 0), fx=resizeFactor, fy=resizeFactor)
        img2 = cv2.cvtColor(resize, cv2.COLOR_RGB2GRAY)
        canny = cv2.Canny(img2, 0, 100)
        dilate_kernel = np.ones((5, 5), np.uint8)
        dilate = cv2.dilate(canny, dilate_kernel)
        erode_kernel = np.ones((5, 5), np.uint8)
        erode = cv2.erode(dilate, erode_kernel)
        contours = cv2.findContours(erode.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        for c in contours:
            peri = cv2.arcLength(c, True)
            c_approx = cv2.approxPolyDP(c, 0.04 * peri, True)
            if len(c_approx) == 4 \
                    and square_area - area_thresh < cv2.contourArea(c) < square_area + area_thresh \
                    and square_perimeter - perimeter_thresh < peri < square_perimeter + perimeter_thresh:
                cv2.drawContours(resize, [c_approx], -1, (0, 255, 0), 4)
                moments = cv2.moments(c)
                center_x = int(moments["m10"] / moments["m00"])
                center_y = int(moments["m01"] / moments["m00"])
                centers.append([center_x, center_y])
        cv2.imwrite('contours.jpg', resize)
    return np.vstack(centers)
