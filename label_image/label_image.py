from os.path import exists
import sys
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

from .ino_code_template import code


def generate_bitmap(image_path, grid_size, place_on_dark):
    # Open image, convert to grayscale, resize, and rotate as needed.
    image = Image.open(image_path)
    image = image.convert('L')
    image = image.resize((grid_size, grid_size))
    image = image.rotate(-90)
    pixels = np.array(image)
    average_brightness = np.mean(pixels)

    # Create a grid (2D list) with 1 if the pixel meets the threshold, else 0.
    matrix = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
    for i in range(grid_size):
        for j in range(grid_size):
            if (place_on_dark and pixels[i, j] < average_brightness) or (
                    not place_on_dark and pixels[i, j] > average_brightness):
                matrix[i][j] = 1
            else:
                matrix[i][j] = 0
    return matrix


def pack_bitmap(matrix, grid_size):
    # Create a list of bits in serpentine order:
    # even rows: left-to-right, odd rows: right-to-left.
    bit_list = []
    for i in range(grid_size):
        if i % 2 == 0:
            for j in range(grid_size):
                bit_list.append(matrix[i][j])
        else:
            for j in reversed(range(grid_size)):
                bit_list.append(matrix[i][j])
    # Pack bits into bytes (8 bits per byte, LSB first)
    n_bits = len(bit_list)
    n_bytes = (n_bits + 7) // 8
    byte_array = []
    for b in range(n_bytes):
        byte_val = 0
        for bit in range(8):
            index = b * 8 + bit
            if index < n_bits and bit_list[index]:
                byte_val |= (1 << bit)
        byte_array.append(byte_val)
    return byte_array


def plot_bitmap(matrix):
    # For preview: display the binary matrix as an image.
    matrix = np.rot90(matrix)
    matrix = ~matrix
    plt.figure(figsize=(6, 6))
    plt.imshow(matrix, cmap='gray', interpolation='nearest')
    plt.title("Image Preview (1 = dot, 0 = blank)")
    plt.show(block=False)


def check_make_file(image_file_name, grid_size, desired_width, byte_array_str):
    makeFile = input("Do you want to create code for this image? (Y/n) > ")
    if makeFile.lower() in ["y", "1", "true"]:
        print("Writing file...")
        writeFile(image_file_name, grid_size, desired_width, byte_array_str)
    else:
        print("No file created. Exiting...")
        exit()


def writeFile(image_file_name, grid_size, desired_width, byte_array_str):
    # filename = "LabelMakerCustomImage_%d_%d.ino" % (grid_size, desired_width)
    filename = f'LabelMakerCustomImage_{image_file_name}_{grid_size}_{desired_width}.ino'
    with open(filename, 'w') as file:
        generatedCode = code % (grid_size, desired_width, byte_array_str)
        file.write(generatedCode)
    print(f"Arduino code file created. Filename: {filename}")
    print("Exiting...")
    exit()


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
    image_file_name = image_path.split("/")[-1].split(".")[0]
    check_make_file(image_file_name, pixel_width, step_width, byte_array_str)

    # Wait until the plot window is closed.
    plot_num = plt.gcf().number
    while plt.fignum_exists(plot_num):
        plt.pause(0.1)
