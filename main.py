from sys import argv
from os.path import exists
from label_image.label_image import generate_bitmap, pack_bitmap, plot_bitmap, checkMakeFile
import matplotlib.pyplot as plt

if __name__ == "main":
  # Variables
  place_on_dark = argv[2]
  string = str(argv[1])
  chopped = ""
  N = 4
  while N > 0:
    chopped += string[-N]
    N -= 1

  if exists(argv[1]) and (chopped == ".png" or chopped == ".jpg" or chopped == "jpeg"):
    image_path = argv[1]
  else:
    print("ERROR: Image not found or invalid filename.")
    exit()

  place_on_dark = int(place_on_dark)

  # Change this value for higher resolution (e.g. 40 instead of 25)
  grid_size = 40 # For example, 40 for more dots in the same space

  # Define the fixed physical width (in steps) for the drawing.
  desired_width = 1350

  # Process the image: generate a binary grid and pack it into a byte array.
  matrix = generate_bitmap(image_path, grid_size, place_on_dark)
  plot_bitmap(matrix)
  byte_array = pack_bitmap(matrix, grid_size)

  # Format the byte array as a C array string, e.g., {0x3F, 0xA7, ...}
  byte_array_str = "{"
  byte_array_str += ", ".join("0x%02X" % b for b in byte_array)
  byte_array_str += "}"

  checkMakeFile(grid_size, desired_width, byte_array_str)

  # Wait until the plot window is closed
  plotNum = plt.gcf().number
  while plt.fignum_exists(plotNum):
    plt.pause(0.1)
