from setuptools import setup, find_packages

setup(
    name="format_image",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Pillow",  # Ensure PIL (Pillow) is installed
    ],
    entry_points={
        "console_scripts": [
            "convert-image=image_converter:convert_format",  # Command-line tool
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple image format converter using Pillow",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/image_converter",  # Replace with actual repo URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
