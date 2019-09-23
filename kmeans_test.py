from kmeans import *


means = [(1000, 1000), (1200, 1200), (1204, 1204)]
new_means = merge_overlapping_means(means, 10**2)
assert new_means == [(1000, 1000), (1202, 1202)]

centers = [(900, 900), (1002, 1002), (998, 1002), (1998, 1998)]
new_centers = remove_around_means(centers, means, 10**2)
assert new_centers == [(900, 900), (1998, 1998)]
