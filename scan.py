#!/usr/bin/python3
from pdf2image import convert_from_path
from os import makedirs
import cv2
import timeit
import numpy as np
import imutils

minLineLength = 30
maxLineLength = 50
maxLineGap = 5
threshold = 50
resizeFactor = 0.5

angle_thresh = 5 * np.pi/180

test_pdf_filename = 'vikhammer.pdf'
dirname = '/tmp/survey/raw/%s' % test_pdf_filename
makedirs(dirname, exist_ok=True)

square_side = 36.5  # TODO: This value depends on resize factor: this is for 0.5
side_thresh = 10
square_perimeter = 4 * square_side
perimeter_thresh = 4 * side_thresh
square_area = square_side**2
area_thresh = side_thresh**2


def line_len(line):
    for x1, y1, x2, y2 in line:
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def convert_to_jpg(pdf_filename, location) -> list:
    # Convert to jpg
    print('Starting conversion to jpg...')
    start = timeit.default_timer()
    pages = convert_from_path(pdf_filename, 500)
    end = timeit.default_timer()
    print('Successfully converted %d pages in %d seconds.' % (len(pages), end - start))

    # Save images
    print('Saving to %s/...' % location)
    image_filenames = []
    for i, page in enumerate(pages):
        image_filename = '%s/p%d.jpg' % (location, i)
        image_filenames.append(image_filename)
        page.save(image_filename, 'JPEG')
    print('Saved all images')
    return image_filenames


def scan_for_lines(image_filenames):
    # Scan for lines
    print('Starting scan_for_lines of %d images' % len(image_filenames))
    for i, fname in enumerate(image_filenames):
        print('Scanning %s (%d of %d)' % (fname, i + 1, len(image_filenames)))
        img = cv2.imread(fname)
        img2 = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img2 = cv2.resize(img2, (0, 0), fx=resizeFactor, fy=resizeFactor)
        canny = cv2.Canny(img2, 0, 100)
        dilate_kernel = np.ones((5, 5), np.uint8)
        dilate = cv2.dilate(canny, dilate_kernel)
        erode_kernel = np.ones((5, 5), np.uint8)
        erode = cv2.erode(dilate, erode_kernel)
        cv2.imwrite('erode.jpg', erode)
        lines = cv2.HoughLinesP(erode, rho=1, theta=np.pi / 180, threshold=130, minLineLength=minLineLength, maxLineGap=maxLineGap)

        print('Found %d lines' % len(lines))
        cannyColor = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
        horisontal_lines = []
        vertical_lines = []
        for line in lines:
            if line_len(line) < maxLineLength:
                for x1, y1, x2, y2 in line:
                    angle = np.arctan2(y2-y1, x2-x1)
                    if -angle_thresh < angle < angle_thresh\
                            or -angle_thresh < angle + np.pi < angle_thresh:
                        cv2.line(cannyColor, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        horisontal_lines.append(line)
                    if -angle_thresh < angle + (np.pi / 2) < angle_thresh \
                            or -angle_thresh < angle - (np.pi / 2) < angle_thresh:
                        cv2.line(cannyColor, (x1, y1), (x2, y2), (255, 0, 0), 2)
                        vertical_lines.append(line)

        cv2.imwrite('lines.jpg', cannyColor)


def scan_for_squares(image_filenames) -> list:
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
                    and square_area - area_thresh < cv2.contourArea(c) < square_area + area_thresh\
                    and square_perimeter - perimeter_thresh < peri < square_perimeter + perimeter_thresh:
                cv2.drawContours(resize, [c_approx], -1, (0, 255, 0), 4)
                moments = cv2.moments(c)
                center_x = int(moments["m10"] / moments["m00"])
                center_y = int(moments["m01"] / moments["m00"])
                centers.append((center_x, center_y))
        cv2.imwrite('contours.jpg', resize)
    return centers


test_image_filenames = ['/tmp/survey/raw/vikhammer.pdf/p2.jpg']  # For testing
#scan_for_lines(test_image_filenames)
centers = scan_for_squares(test_image_filenames)
