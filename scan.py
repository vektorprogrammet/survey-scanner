#!/usr/bin/python3
from pdf2image import convert_from_path
from os import makedirs, path
import cv2
import timeit
import numpy as np

minLineLength = 100;
maxLineLength = 130;
maxLineGap = 10;
resizeFactor = 0.5;

pdf_filename = 'vikhammer.pdf'
dirname = '/tmp/survey/raw/%s' % pdf_filename
makedirs(dirname, exist_ok=True)

def line_len(line):
    for x1, y1, x2, y2 in line:
        return np.sqrt((x2-x1)**2 + (y2-y1)**2)

# Convert to jpg
print('Starting conversion to jpg...')
start = timeit.default_timer()
pages = convert_from_path(pdf_filename, 500)
end = timeit.default_timer()
print('Successfully converted %d pages in %d seconds.' % (len(pages), end - start))

# Save images
print('Saving to %s/...' % dirname)
image_filenames = []
for i, page in enumerate(pages):
    image_filename = '%s/p%d.jpg' % (dirname,i)
    image_filenames.append(image_filename)
    page.save(image_filename, 'JPEG')
print('Saved all images')

# Scan for lines
print('Starting scan of %d images' % len(image_filenames))
image_filenames = ['/tmp/survey/raw/vikhammer.pdf/p2.jpg'] # For testing
for i, fname in enumerate(image_filenames):
    print('Scanning %s (%d of %d)' % (fname, i+1, len(image_filenames)))
    img = cv2.imread(fname)
    img2 = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img2 = cv2.resize(img2, (0,0), fx = resizeFactor, fy = resizeFactor)
    img2 = cv2.cv2.blur(img2, (3,3))
    canny = cv2.Canny(img2, 0, 100)
    lines = cv2.HoughLinesP(canny,1,np.pi/360, 30, minLineLength, maxLineGap)

    print('Found %d lines' % len(lines))
    cannyColor = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
    for line in lines:
        if line_len(line) < maxLineLength:
            for x1,y1,x2,y2 in line:
                cv2.line(cannyColor,(x1,y1),(x2,y2),(0,255,0),2)

    cv2.imshow('Lines', cannyColor)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

