#!/usr/bin/python3
from os import makedirs, path
import cv2
import numpy as np
import sys
from convert import convert_to_jpg
from scan import scan_for_squares


pdf_filename = ""
k_centers = 0
try:
    pdf_filename = sys.argv[1]
    k_centers = int(sys.argv[2])
except (ValueError, IndexError):
    print("Usage: ./main.py file.pdf k")
    exit(1)
finally:
    pass

if not path.isfile(pdf_filename):
    print("{} is not a valid file".format(pdf_filename))
    exit(1)

print("Starting survey scan of {}. Looking for {} boxes.". format(pdf_filename, k_centers))

export_dirname = '/tmp/survey/raw/%s' % pdf_filename
makedirs(export_dirname, exist_ok=True)


test_image_filenames = convert_to_jpg(pdf_filename, export_dirname)
test_centers = scan_for_squares(test_image_filenames)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
test_centers = np.float32(test_centers)

flags = cv2.KMEANS_RANDOM_CENTERS
compactness, labels, means = cv2.kmeans(test_centers, k_centers, None, criteria, 10, flags)
