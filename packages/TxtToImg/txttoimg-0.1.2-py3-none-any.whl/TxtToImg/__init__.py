import cv2
import requests
import numpy as np

class Txt2Img():
    def __init__(self, text, url=None, width=800, height=600, **kwargs):
        
        print("""
txt2img - A Python library to create images with customizable text overlays.

Created by Nelvin Jaziel Márquez.
For questions or feedback, contact me at: nelvinjazieldeveloper@gmail.com

If you find this library useful, consider supporting its development with a donation.
Your contribution helps keep this project alive and growing. Thank you! 💖

Donate via Binance Pay: 753731469
Or send crypto to this address (USDT TRC20): TFDvNrq3oCHb4f6udyEJ4idHPBE5LBozfS
""")
        
        """
        Initializes the Img2Txt class.

        Parameters:
            text (str): Text to be added to the image.
            url (str, optional): URL of the background image. If not provided, a gradient will be used.
            width (int, optional): Width of the image. Default is 800.
            height (int, optional): Height of the image. Default is 600.
            **kwargs: Optional arguments for customization:
                - text_color (tuple): Text color in BGR format. Default is white (255, 255, 255).
                - text_background_color (tuple): Text background color in BGR format. Default is black (0, 0, 0).
                - gradient_color (tuple): Gradient color in BGR format. Default is white (255, 255, 255).
                - font (int): OpenCV font type. Default is cv2.FONT_HERSHEY_SIMPLEX.
                - font_scale (float): Font size. Default is 1.5.
                - font_thickness (int): Font thickness. Default is 3.
                - text_position (str): Position of the text. Can be "top", "bottom", or "center". Default is "center".
        """
        self.text = text
        self.url = url
        self.width = width
        self.height = height

        # Default values for optional arguments
        self.text_color = kwargs.get("text_color", (255, 255, 255))  # White
        self.text_background_color = kwargs.get("text_background_color", (0, 0, 0))  # Black
        self.gradient_color = kwargs.get("gradient_color", (255, 255, 255))  # White
        self.font = kwargs.get("font", cv2.FONT_HERSHEY_SIMPLEX)  # Simple font
        self.font_scale = kwargs.get("font_scale", 1.5)  # Font size
        self.font_thickness = kwargs.get("font_thickness", 3)  # Font thickness
        self.text_position = kwargs.get("text_position", "center")  # Text position

    def open_image_from_url(self):
        try:
            # Download the image from the URL
            response = requests.get(self.url, stream=True)
            if response.status_code == 200:
                # Convert the downloaded image into a NumPy array
                image_array = np.asarray(bytearray(response.raw.read()), dtype=np.uint8)
                # Decode the array into an OpenCV image
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                # Resize the image to the desired size
                image = cv2.resize(image, (self.width, self.height))
                return image
            else:
                print(f"Error downloading the image. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error processing the URL: {e}")
            return None

    def create_gradient(self):
        # Create a gradient background
        background = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        for y in range(self.height):
            color = tuple(int(c * (y / self.height)) for c in self.gradient_color)
            cv2.line(background, (0, y), (self.width, y), color, 1)
        return background

    def add_text(self, img):
        # Get the size of the text
        (text_width, text_height), _ = cv2.getTextSize(self.text, self.font, self.font_scale, self.font_thickness)

        # Calculate the text position based on the specified alignment
        if self.text_position == "top":
            x = (self.width - text_width) // 2
            y = text_height + 20  # Top margin
        elif self.text_position == "bottom":
            x = (self.width - text_width) // 2
            y = self.height - 20  # Bottom margin
        elif self.text_position == "center":
            x = (self.width - text_width) // 2
            y = (self.height + text_height) // 2
        else:
            raise ValueError("Invalid text position. Use 'top', 'bottom', or 'center'.")

        # Create a background for the text
        margin = 10  # Margin around the text
        cv2.rectangle(
            img,
            (x - margin, y - text_height - margin),
            (x + text_width + margin, y + margin),
            self.text_background_color,
            -1,  # Fill the rectangle
        )

        # Overlay the text on the image
        cv2.putText(img, self.text, (x, y), self.font, self.font_scale, self.text_color, self.font_thickness, cv2.LINE_AA)

    def create(self):
        # Open the image from the URL or create a gradient
        if self.url:
            img = self.open_image_from_url()
            if img is None:
                print("Using gradient background.")
                img = self.create_gradient()
        else:
            img = self.create_gradient()

        # Add the text to the image
        self.add_text(img)

        self.img = img
    
    def show(self):
        cv2.imshow(self.text, self.img)
        cv2.waitKey(0)  # Wait until the user presses a key
        cv2.destroyAllWindows()  # Close all OpenCV windows
        
    def download(self):
        cv2.imwrite(self.text + ".jpg", self.img)