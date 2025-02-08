# imageCompressionTest
Just a little thing to make images fit more easily on a small EEPROM for the RP2040 Smartwatch.

## Features
- Compress images into a custom `.cmi` format using a 16-color EGA-like palette.
- Supports optional image resizing or scaling before compression.
- Decompresses `.cmi` files and renders them to a viewable format.

## Requirements
- Python 3.x
- Pillow (`PIL`) library
- NumPy library

## Installation

To install the required dependencies, run:

```bash
pip install pillow numpy
```

## Usage

### Compress an Image
To compress an image into the `.cmi` format:

```bash
python main.py -c <input_image> -r <width,height>
```

Or, to scale the image:

```bash
python main.py -c <input_image> -s <scale_factor>
```

### Decompress a .cmi File
To decompress and view a `.cmi` image:

```bash
python main.py <compressed_file.cmi>
```

## Notes
- The program supports both resolution resizing (`-r`) and scaling (`-s`), but not both at the same time.
- The `.cmi` format uses Run-Length Encoding (RLE) to reduce file size.
