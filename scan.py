#!/usr/bin/python3
from pdf2image import convert_from_path
from os import makedirs, path
import cv2
import timeit

font = cv2.FONT_HERSHEY_COMPLEX

pdf_filename = 'vikhammer.pdf'
dirname = '/tmp/survey/raw/%s' % pdf_filename
makedirs(dirname, exist_ok=True)



print('Starting conversion to jpg...')
start = timeit.default_timer()
pages = convert_from_path(pdf_filename, 500)
end = timeit.default_timer()
print('Successfully converted %d pages in %d seconds.' % (len(pages), end - start))

print('Saving to %s/...' % dirname)
image_filenames = []
for i, page in enumerate(pages):
    image_filename = '%s/p%d.jpg' % (dirname,i)
    image_filenames.append(image_filename)
    page.save(image_filename, 'JPEG')
print('Saved all images')

print('Starting scan of %d images' % len(image_filenames))

image_filenames = ['/tmp/survey/raw/vikhammer.pdf/p2.jpg']
for i, fname in enumerate(image_filenames):
    print('Scanning %s (%d of %d)' % (fname, i+1, len(image_filenames)))
    img = cv2.imread(fname)
    img2 = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img2 = cv2.cv2.blur(img2, (3,3))
    canny  = cv2.Canny(img2, 170, 255)
    contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    for j, cnt in enumerate(contours):
        # We approximate the contour with an approximated contour, and count
        # the number of verticess in the resulting approximation.
        # Clearly, this is error prone, so a better solution must be deviced
        approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        if len(approx) == 4:
            cv2.drawContours(img, [cnt], 0, (0, 255, 0), 3)
            cv2.putText(img, 'Box', (x, y), font, 1, 0)
            cv2.putText(img, '%d' % j , (x, y + 40), font, 1, 0)
            print('Box %d:' % j)
            print(cnt)
        else:
            cv2.drawContours(img, [cnt], 0, (0, 100, 0), 2)


    cv2.imshow('Contours', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

