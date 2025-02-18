import argparse
from os.path import exists
from label_image.label_image import generate_bitmap, pack_bitmap, plot_bitmap, check_make_file
import matplotlib.pyplot as plt
import sys


def process_image(image_path: str, draw_dark_pixels: bool = True, pixel_width: int = 25, step_width: int = 1350):
    """Process the image to generate a binary bitmap, pack it into a byte array, and
     output code for the Arduino Nano on the HackPack Label Maker. Also displays the generated bitmap."""
    # Validate that the file exists and has an allowed extension.
    allowed_ext = ('.png', '.jpg', '.jpeg')
    if not exists(image_path) or not image_path.lower().endswith(allowed_ext):
        print("ERROR: Image not found or invalid filename.")
        sys.exit(1)

    # Process the image: generate a binary grid and pack it into a byte array.
    matrix = generate_bitmap(image_path, pixel_width, draw_dark_pixels)
    plot_bitmap(matrix)
    byte_array = pack_bitmap(matrix, pixel_width)

    # Format the byte array as a C array string, e.g., {0x3F, 0xA7, ...}
    byte_array_str = "{" + ", ".join("0x%02X" % b for b in byte_array) + "}"
    check_make_file(pixel_width, step_width, byte_array_str)

    # Wait until the plot window is closed.
    plot_num = plt.gcf().number
    while plt.fignum_exists(plot_num):
        plt.pause(0.1)

# TODO: Add a threshold to the image processing function to determine if a pixel is dark or light, relative to the average brightness of the image.
# TODO: Add a function to get an ai-generated image.


def main():
    parser = argparse.ArgumentParser(
        description="Process an image to generate code for the HackPack Label Maker."
    )
    parser.add_argument("--image_path", default="images/heavy_falcon.jpeg",
                        help="Path to the image file (.png, .jpg, .jpeg)")
    parser.add_argument("--draw_dark_pixels", type=bool, default=True,
                        help="True if you want to draw points for dark pixels, "
                             "False if you want to draw points for light pixels")
    parser.add_argument("--pixel_width", type=int, default=25,
                        help="Points are drawn in a grid with dimensions pixel_width x pixel_width (default: 25)")
    parser.add_argument("--step_width", type=int, default=1350,
                        help="Overall width of drawing in stepper motor steps (default: 1350)")

    args = parser.parse_args()

    process_image(
        image_path=args.image_path,
        draw_dark_pixels=args.draw_dark_pixels,
        pixel_width=args.pixel_width,
        step_width=args.step_width
    )


if __name__ == "__main__":
    main()
