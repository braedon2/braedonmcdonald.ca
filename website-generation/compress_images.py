import os
import sys
from PIL import Image

yellow_text = '\033[93m'
end_text_coloring = '\033[0m'
compressed_image_suffix = '_resized'

def compress_images(path):
    print(f'Compressing images in {path}')

    original_images = []
    compressed_images = []
    images_to_compress = []

    for fname in os.listdir(path):
        if os.path.isdir(os.path.join(path, fname)):
            print(f'{yellow_text}Warning: directory detected in provided path. Skipping...{end_text_coloring}')
            continue

        fnameroot, _ = os.path.splitext(fname)
        if fnameroot.endswith(compressed_image_suffix):
            compressed_images.append(fname)
        else:
            original_images.append(fname)

    for fname in original_images:
        fnameroot, fextensinon = os.path.splitext(fname)
        if fnameroot + compressed_image_suffix + fextensinon not in compressed_images:
            images_to_compress.append(fname)

    num_images_to_compress = len(images_to_compress)
    images_compressed = 0
    print(f'    {len(compressed_images)} already compressed')
    print(f'    Compressing {num_images_to_compress} images')

    for fname in images_to_compress:
        fnameroot, fextensinon = os.path.splitext(fname)
        with Image.open(os.path.join(path, fname)) as image:
            print(f'    Compressing {fname}, original size: {image.size}, {images_compressed+1}/{num_images_to_compress}...')
            image.save(os.path.join((path), fnameroot + compressed_image_suffix + fextensinon), optimize=True, quality=90)
        images_compressed += 1

if __name__ == '__main__':
    compress_images(sys.argv[1])