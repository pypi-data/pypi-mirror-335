# TxtToImg

TxtToImg is a Python library that allows you to add text to an image, either by providing a URL for the background image or by generating a gradient background.

## Installation

To install TxtToImg, you can use pip:

```
pip install TxtToImg
```

## Usage

Here's an example of how to use the TxtToImg class:

```python
from TxtToImg import Txt2Img

# Create an instance of the Txt2Img class
img_generator = Txt2Img(
    text="Hello, World!",
    url="https://example.com/background.jpg",
    width=800,
    height=600,
    text_color=(255, 255, 255),  # White text
    text_background_color=(0, 0, 0),  # Black background
    font_scale=2,
    font_thickness=3,
    text_position="center"
)

# Create the image
img_generator.create()

# Show the image
img_generator.show()

# Save the image
img_generator.download()
```

## API

The TxtToImg class has the following methods:

- `__init__(self, text, url=None, width=800, height=600, **kwargs)`: Initializes the TxtToImg class with the specified parameters.
- `open_image_from_url(self)`: Downloads the image from the provided URL and returns it as a NumPy array.
- `create_gradient(self)`: Creates a gradient background image.
- `add_text(self, img)`: Adds the specified text to the image.
- `create(self)`: Generates the final image by either opening the image from the URL or creating a gradient background, and then adding the text to the image.
- `show(self)`: Displays the generated image using OpenCV.
- `download(self)`: Saves the generated image to a file with the same name as the text.

## License

This project is licensed under the [MIT License](LICENSE).