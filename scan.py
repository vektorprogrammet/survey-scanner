#!/usr/bin/python3
from os import makedirs
import cv2
import numpy as np
import sys
from pdf_to_jpeg import convert_to_jpg
from jpegs_to_square_centers import scan_for_squares


pdf_filename = "vikhammer.pdf"
if len(sys.argv) > 1:
    pdf_filename = sys.argv[1]
else:
    print("Please provide a pdf file")
    #exit(1)

export_dirname = '/tmp/survey/raw/%s' % pdf_filename
makedirs(export_dirname, exist_ok=True)


test_image_filenames = convert_to_jpg(pdf_filename, export_dirname)
# scan_for_lines(test_image_filenames)
test_centers = scan_for_squares(test_image_filenames)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
test_centers = np.float32(test_centers)

flags = cv2.KMEANS_RANDOM_CENTERS
compactness, labels, means = cv2.kmeans(test_centers, 37, None, criteria, 10, flags)
