def remove_around_means(values, means, variance):
    outside_one_std = []
    for value in values:
        if is_outside_one_std(value, means, variance):
            outside_one_std.append(value)
    return outside_one_std


def is_outside_one_std(value, means, variance):
    for mean in means:
        if (value[0] - mean[0])**2 + (value[1] - mean[1])**2 < variance:
            return False
    return True


def merge_overlapping_means(means, variance):
    dupe_sets = []
    unique_means = []

    for i, mean in enumerate(means):
        exists_in_dupes, dupe_set = exists_in_set(mean, dupe_sets, variance)
        if exists_in_dupes:
            dupe_set.append(mean)
            continue

        exists_in_proceeding = exists_in_list(mean, means[i + 1:], variance)
        if exists_in_proceeding:
            dupe_sets.append([mean])
            continue

        unique_means.append(mean)

    for dupe_set in dupe_sets:
        sum_x = 0
        sum_y = 0
        for dupe in dupe_set:
            sum_x += dupe[0]
            sum_y += dupe[1]
        avg = (sum_x / len(dupe_set), sum_y / len(dupe_set))
        unique_means.append(avg)

    return unique_means


def exists_in_set(needle, haystacks, variance):
    for haystack in haystacks:
        for hay in haystack:
            if (hay[0] - needle[0])**2 + (hay[1] - needle[1])**2 < variance:
                return True, haystack
    return False, {}


def exists_in_list(needle, haystack, variance):
    for hay in haystack:
        if (hay[0] - needle[0])**2 + (hay[1] - needle[1])**2 < variance:
            return True
    return False
