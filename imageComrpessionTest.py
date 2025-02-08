import argparse
import os
from PIL import Image, ImageEnhance
import numpy as np

PALETTE = [
    (0, 0, 0),
    (0, 0, 170),
    (0, 170, 0),
    (0, 170, 170),
    (170, 0, 0),
    (170, 0, 170),
    (170, 85, 0),
    (170, 170, 170),
    (85, 85, 85),
    (85, 85, 255),
    (85, 255, 85),
    (85, 255, 255),
    (255, 85, 85),
    (255, 85, 255),
    (255, 255, 85),
    (255, 255, 255),
]

def find_nearest_color(rgb):
    r, g, b = map(int, rgb)
    min_distance = float('inf')
    best_index = 0
    for i, (pr, pg, pb) in enumerate(PALETTE):
        pr, pg, pb = map(int, (pr, pg, pb))
        distance = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if distance < min_distance:
            min_distance = distance
            best_index = i
    return best_index

def rle_compress(pixel_data):
    compressed = bytearray()
    i = 0
    while i < len(pixel_data):
        run_length = 1
        while i + run_length < len(pixel_data) and pixel_data[i] == pixel_data[i + run_length] and run_length < 15:
            run_length += 1
        compressed.append((run_length << 4) | pixel_data[i])
        i += run_length
    return compressed

def rle_decompress(compressed_data, total_pixels):
    pixel_data = []
    for byte in compressed_data:
        run_length = (byte >> 4) & 0x0F
        color = byte & 0x0F
        pixel_data.extend([color] * run_length)
    return pixel_data[:total_pixels]

def compress_image(input_path, output_path, resolution=None, scale=None):
    image = Image.open(input_path)
    hsv_image = image.convert("HSV")
    h, s, v = hsv_image.split()
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2).convert('RGB')

    if resolution:
        width, height = resolution
        image = image.resize((width, height))
    elif scale:
        width, height = image.size
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = image.resize((new_width, new_height))

    pixels = np.array(image)
    pixel_data = []

    for y in range(image.height):
        for x in range(image.width):
            pixel_data.append(find_nearest_color(pixels[y, x]))

    compressed_pixels = rle_compress(pixel_data)

    original_size = os.path.getsize(input_path)
    compressed_size = len(compressed_pixels) + 6
    reduction_percent = (1 - (compressed_size / original_size)) * 100

    with open(output_path, 'wb') as f:
        f.write(image.width.to_bytes(3, byteorder='big'))
        f.write(image.height.to_bytes(3, byteorder='big'))
        f.write(compressed_pixels)

    print(f"Image compressed and saved as {output_path}")
    print(f"Original size: {original_size} bytes")
    print(f"Compressed size: {compressed_size} bytes")
    print(f"Compression reduction: {reduction_percent:.2f}%")

def decompress_image(input_path):
    with open(input_path, 'rb') as f:
        width = int.from_bytes(f.read(3), byteorder='big')
        height = int.from_bytes(f.read(3), byteorder='big')
        compressed_data = f.read()

    total_pixels = width * height
    pixel_data = rle_decompress(compressed_data, total_pixels)

    pixels = np.zeros((height, width, 3), dtype=np.uint8)
    index = 0
    for y in range(height):
        for x in range(width):
            pixels[y, x] = PALETTE[pixel_data[index]]
            index += 1

    image = Image.fromarray(pixels, mode='RGB')
    image.show()

def main():
    parser = argparse.ArgumentParser(description="Compress and decompress images to/from .cmi format with 16 colors.")
    parser.add_argument('-c', '--compress', metavar='INPUT_IMAGE', help="Compress the input image to .cmi format.")
    parser.add_argument('file', metavar='FILE', nargs='?', help="Decompress and display the specified .cmi file.")
    parser.add_argument('-r', '--resolution', metavar='WIDTH,HEIGHT', type=str, help="Resize the image to the given resolution (e.g., 100,100).")
    parser.add_argument('-s', '--scale', metavar='SCALE', type=float, help="Scale the image by the given factor (e.g., 0.5 for 50%).")
    args = parser.parse_args()

    resolution = None
    if args.resolution:
        width, height = map(int, args.resolution.split(','))
        resolution = (width, height)

    if args.compress:
        if args.scale and args.resolution:
            print("Error: Cannot use both -s (scale) and -r (resolution) together.")
            return
        input_image_path = args.compress
        if not os.path.isfile(input_image_path):
            print(f"Error: File '{input_image_path}' not found.")
            return
        output_cmi_path = os.path.splitext(input_image_path)[0] + '.cmi'
        compress_image(input_image_path, output_cmi_path, resolution, args.scale)
    elif args.file:
        cmi_file_path = args.file
        if not os.path.isfile(cmi_file_path):
            print(f"Error: File '{cmi_file_path}' not found.")
            return
        decompress_image(cmi_file_path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
