import cv2
import numpy as np
import imutils
from typing import List, Dict
from print import log

resizeFactor = 0.5

square_side = 36.5  # TODO: This value depends on resize factor: this is for 0.5 (also, this is absolute pixel count)
side_thresh = 10
square_perimeter = 4 * square_side
perimeter_thresh = 4 * side_thresh
square_area = square_side ** 2
area_thresh = side_thresh ** 2

check_range = 50
check_thresh = 10
blank_box_mean = 103

circle_radius = 35
color_green = (0, 255, 0)


def scan_for_squares(image_filenames) -> np.ndarray:
    log('Looking for checkboxes in {} images'.format(len(image_filenames)))
    centers = []
    for i, fname in enumerate(image_filenames):
        log('Scanning {} ({} of {}):'.format(fname, i + 1, len(image_filenames)), end=' ')
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
        center_count = 0
        for c in contours:
            peri = cv2.arcLength(c, True)
            c_approx = cv2.approxPolyDP(c, 0.04 * peri, True)
            if len(c_approx) == 4 \
                    and square_area - area_thresh < cv2.contourArea(c) < square_area + area_thresh \
                    and square_perimeter - perimeter_thresh < peri < square_perimeter + perimeter_thresh:
                cv2.drawContours(resize, [c_approx], -1, color_green, 4)
                moments = cv2.moments(c)
                center_x = int(moments["m10"] / moments["m00"])
                center_y = int(moments["m01"] / moments["m00"])
                centers.append([center_x, center_y])
                center_count += 1
        log('{} boxes'.format(center_count))
    return np.vstack(centers)


def scan_for_checks(image_filenames: List[str], centers: np.ndarray, export_dir) -> List[Dict]:
    log('Scanning centers for checks in {} files'.format(len(image_filenames)))
    page_dicts = []
    for page_num, fname in enumerate(image_filenames):
        log('Scanning {} ({} of {}):'.format(fname, page_num + 1, len(image_filenames)))
        orig = cv2.imread(fname)
        resize = cv2.resize(orig, (0, 0), fx=resizeFactor, fy=resizeFactor)
        grey = cv2.cvtColor(resize, cv2.COLOR_RGB2GRAY)
        canny = cv2.Canny(grey, 0, 100)
        dilate_kernel = np.ones((5, 5), np.uint8)
        dilate = cv2.dilate(canny, dilate_kernel)
        boxes_dict = {}
        for center_num, center in enumerate(centers):
            x, y = center[0], center[1]
            mean = np.mean(dilate[int(y - check_range / 2):int(y + check_range / 2), int(x - check_range / 2):int(x + check_range / 2)])
            if mean > blank_box_mean + check_thresh:
                boxes_dict[center_num] = True
                cv2.circle(resize, (x, y), circle_radius, color_green, thickness=3)
        page_dicts.append({'page': page_num, 'boxes': boxes_dict})
        cv2.imwrite('{}/{}.jpg'.format(export_dir, str(page_num)), resize)
    return page_dicts
