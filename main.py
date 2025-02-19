import argparse
from label_image.label_image import process_image

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
    parser.add_argument("--threshold_factor", type=float, default=1.0, help="Adjust the threshold for dark/light pixels by deviating slightly from the default 1.0.  Try 1.3, for example.")

    args = parser.parse_args()

    process_image(
        image_path=args.image_path,
        draw_dark_pixels=args.draw_dark_pixels,
        num_points_width=args.num_points_width,
        num_steps_width=args.num_steps_width,
        threshold_factor=args.threshold_factor
    )


if __name__ == "__main__":
    main()
