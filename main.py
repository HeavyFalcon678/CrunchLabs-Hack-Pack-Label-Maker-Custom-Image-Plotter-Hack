import argparse
from label_image.label_image import process_image


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
    parser.add_argument("--num_points_width", type=int, default=25,
                        help="Points are drawn in a grid with dimensions num_points_width x num_points_width (default: 25)")
    parser.add_argument("--num_steps_width", type=int, default=1350,
                        help="Overall width of drawing in stepper motor steps (default: 1350)")

    args = parser.parse_args()

    process_image(
        image_path=args.image_path,
        draw_dark_pixels=args.draw_dark_pixels,
        num_points_width=args.num_points_width,
        num_steps_width=args.num_steps_width
    )


if __name__ == "__main__":
    main()
