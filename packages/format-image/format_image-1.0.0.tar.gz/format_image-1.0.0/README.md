# Image Converter

A simple Python script to convert images between formats using the Pillow library.

## Features
- Convert images to PNG, JPG, BMP, and WEBP formats.
- Supports batch conversion.
- Easy-to-use command-line tool.

## Installation

Ensure you have Python installed (>=3.6), then install the package:

```sh
pip install .
```

## Usage

### As a Python Script

```python
from image_converter import convert_format

convert_format("input/rose.jpg", "png")
```

### As a Command-Line Tool

After installation, you can use it from the terminal:

```sh
convert-image input/rose.jpg png
```

## Dependencies
- Pillow

## License
MIT License

## Author
Your Name - [GitHub Profile](https://github.com/yourusername)