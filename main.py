#!/usr/bin/python3
import json
import timeit
import uuid
from os import makedirs, path
import cv2
import numpy as np
import sys
from convert import convert_to_jpg
from scan import scan_for_squares, scan_for_checks
from typing import Tuple
from print import log
from kmeans import merge_overlapping_means, remove_around_means
from draw import draw_point_sets


def get_args() -> Tuple[str, int]:
    pdf_fname = ""
    k = 0
    try:
        pdf_fname = sys.argv[1]
        k = int(sys.argv[2])
    except (ValueError, IndexError):
        log("Usage: ./main.py file.pdf k")
        exit(1)
    finally:
        pass

    if not path.isfile(pdf_fname):
        log("{} is not a valid file".format(pdf_fname))
        exit(1)

    return pdf_fname, k


(pdf_filename, k_centers) = get_args()

log("Starting survey scan of {}. Looking for {} boxes.". format(pdf_filename, k_centers))

export_dirname = '/tmp/survey/{}'.format(uuid.uuid4())
makedirs(export_dirname)


raw_dir = '{}/raw'.format(export_dirname)
makedirs(raw_dir)
test_image_filenames = convert_to_jpg(pdf_filename, raw_dir)

log('Starting scan for boxes.')
start = timeit.default_timer()
test_centers = scan_for_squares(test_image_filenames)
end = timeit.default_timer()
log('Scanned {} pages in {} seconds.'.format(len(test_image_filenames), int(end - start)))

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 0.1)
test_centers = np.float32(test_centers)

flags = cv2.KMEANS_RANDOM_CENTERS
compactness, labels, means = cv2.kmeans(test_centers, k_centers, None, criteria, 10, flags)
# TODO: Fix k means
# Too many means are placed on top of a few boxes, likely because those boxes get detected the most.
# We can do a second pass, where we first go over the test_centers array, and remove all points that already
# correspond to a mean (within some threshold)
# For the means, we remove any duplicates. (take the mean of any means that overlap)
# We will then be left with a number of means that is less than k (37). This difference will be our new k
# Run k-means once more with the new k and combine with the old means


marked_dir = '{}/marked'.format(export_dirname)
makedirs(marked_dir)
unique_means = np.array(merge_overlapping_means(means, 10**2)).astype(int)
draw_point_sets([test_centers, means, unique_means], test_image_filenames[0], "{}/means.jpg".format(export_dirname), [(255, 200, 200), (200, 200, 255), (50, 50, 230)])
page_dicts = scan_for_checks(test_image_filenames, unique_means, marked_dir)
box_coordinates = {}
for box_num, mean in enumerate(unique_means):
    x, y = mean[0], mean[1]
    box_coordinates[box_num] = {'x': int(x), 'y': int(y)}

output = {'boxes': box_coordinates, 'pages': page_dicts, 'images_folder': export_dirname}
print(json.dumps(output, indent=2, sort_keys=True))
