import cv2

resizeFactor = 0.5
circle_radius = 2


def draw_points(means, image_filename, output_filename, color):
    orig = cv2.imread(image_filename)
    resize = cv2.resize(orig, (0, 0), fx=resizeFactor, fy=resizeFactor)
    for mean in means:
        x, y = mean[0], mean[1]
        cv2.circle(resize, (x, y), circle_radius, color, thickness=3)
    cv2.imwrite(output_filename, resize)


def draw_point_sets(point_sets, image_filename, output_filename, colors):
    orig = cv2.imread(image_filename)
    resize = cv2.resize(orig, (0, 0), fx=resizeFactor, fy=resizeFactor)
    for i, point_set in enumerate(point_sets):
        for mean in point_set:
            x, y = mean[0], mean[1]
            cv2.circle(resize, (x, y), circle_radius, colors[i], thickness=3)
    cv2.imwrite(output_filename, resize)
