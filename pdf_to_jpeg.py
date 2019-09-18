import timeit
from pdf2image import convert_from_path


def convert_to_jpg(pdf_filename, export_path) -> list:
    # Convert to jpg
    print('Starting conversion to jpg...')
    start = timeit.default_timer()
    pages = convert_from_path(pdf_filename, 500)
    end = timeit.default_timer()
    print('Successfully converted %d pages in %d seconds.' % (len(pages), end - start))

    # Save images
    print('Saving to %s/...' % export_path)
    image_filenames = []
    for i, page in enumerate(pages):
        image_filename = '%s/p%d.jpg' % (export_path, i)
        image_filenames.append(image_filename)
        page.save(image_filename, 'JPEG')
    print('Saved all images')
    return image_filenames
