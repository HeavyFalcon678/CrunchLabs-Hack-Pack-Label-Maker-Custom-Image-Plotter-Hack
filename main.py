code = """//This is the Custom Image hack for the Hack Pack LabelMaker

//////////////////////////////////////////////////
                //  LIBRARIES  //
//////////////////////////////////////////////////
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Stepper.h>
#include <ezButton.h>
#include <Servo.h>
#include <avr/pgmspace.h>

//////////////////////////////////////////////////
          //  PINS AND PARAMETERS  //
//////////////////////////////////////////////////

LiquidCrystal_I2C lcd(0x27, 16, 2);  // Set the LCD address to 0x27 for a 16x2 display

ezButton button1(14); //joystick button handler
#define INIT_MSG "Initializing..."
#define MODE_NAME "PLOT CUSTOM IMG "
#define PLOTTING "   PLOTTING...  "

// Set the grid resolution and desired drawing width (in steps)
// (Change GRID_SIZE here in the Python-generated code to 25, 40, etc.)
#define GRID_SIZE %s
#define DESIRED_WIDTH %s
// Compute the scale factor so that (GRID_SIZE * customImagescale) equals DESIRED_WIDTH
int customImagescale = DESIRED_WIDTH / GRID_SIZE;

// Calculate the number of bytes in the bitmap
#define BITMAP_SIZE ((GRID_SIZE * GRID_SIZE + 7) / 8)

//////////////////////////////////////////////////
  //  JOYSTICK, MOTOR, SERVO, ETC. SETUP
//////////////////////////////////////////////////

const int joystickXPin = A2;  
const int joystickYPin = A1;  
const int joystickButtonThreshold = 200;

int currentCharacter = 0;
int cursorPosition = 0;
int currentPage = 0;
const int charactersPerPage = 16;

const int stepCount = 200;
const int stepsPerRevolution = 2048;
Stepper xStepper(stepsPerRevolution, 6,8,7,9);
Stepper yStepper(stepsPerRevolution, 2,4,3,5);

int xPins[4] = {6, 8, 7, 9};
int yPins[4] = {2, 4, 3, 5};

const int SERVO_PIN  = 13;
Servo servo;
int angle = 30;

enum State { MainMenu, Editing, PrintConfirmation, Printing, plotCustomImg };
State currentState = MainMenu;
State prevState = Printing;

enum jState {LEFT, RIGHT, UP, DOWN, MIDDLE, UPRIGHT, UPLEFT, DOWNRIGHT, DOWNLEFT};
jState joyState = MIDDLE;
jState prevJoyState = MIDDLE;

boolean pPenOnPaper = false;
int lineCount = 0;

int xpos = 0;
int ypos = 0;
const int posS = 2;
const int posM = 7;
const int posL = 12;
bool joyUp;
bool joyDown;
bool joyLeft;
bool joyRight;
int button1State;
int joystickX;
int joystickY;

//////////////////////////////////////////////////
          //  BITMAP IMAGE DATA  //
//////////////////////////////////////////////////

// The image is stored as a bit-packed array. Each bit represents a dot (1 = draw, 0 = skip).
// The bits are stored in serpentine order: even rows left-to-right, odd rows right-to-left.
const uint8_t customImage[BITMAP_SIZE] PROGMEM = %s;

//////////////////////////////////////////////////
                //  S E T U P  //
//////////////////////////////////////////////////
void setup() {
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print(INIT_MSG);

  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  button1.setDebounceTime(50);
  servo.attach(SERVO_PIN);
  servo.write(angle);

  plot(false);

  yStepper.setSpeed(10);
  xStepper.setSpeed(8);

  penUp();
  homeYAxis();

  ypos = 0;
  xpos = 0;

  releaseMotors();
  lcd.clear();
}

////////////////////////////////////////////////
                //  L O O P  //
////////////////////////////////////////////////
void loop() {

  button1.loop();
  button1State = button1.getState();

  joystickX = analogRead(joystickXPin);
  joystickY = analogRead(joystickYPin);
  joyUp = joystickY < (512 - joystickButtonThreshold);
  joyDown = joystickY > (512 + joystickButtonThreshold);
  joyLeft = joystickX < (512 - joystickButtonThreshold);
  joyRight = joystickX > (512 + joystickButtonThreshold);

  switch (currentState) {
    case plotCustomImg:
      {
        if (prevState != plotCustomImg){
          lcd.clear();
          lcd.setCursor(0,0);
          lcd.print(MODE_NAME);
          lcd.setCursor(0,1);
          lcd.print(PLOTTING);
          cursorPosition = 5;
          prevState = plotCustomImg;
        }
        lcd.setCursor(cursorPosition, 1);
        plotcustomImage();
        homeYAxis();
        releaseMotors();
        lcd.clear();
        currentState = MainMenu;
        prevState = plotCustomImg;
      }
      break;

    case MainMenu:
      {
        if (prevState != MainMenu){
          lcd.clear();
          lcd.setCursor(0,0);
          lcd.print(MODE_NAME);
          lcd.setCursor(0,1);
          lcd.print("      START     ");
          cursorPosition = 5;
          prevState = MainMenu;
        }
        lcd.setCursor(cursorPosition, 1);
        lcd.blink();
        if (button1.isPressed()) {
          lcd.clear();
          lcd.noBlink();
          currentState = plotCustomImg;
          prevState = MainMenu;
        }
      }
      break;
  }
}

void line(int newx, int newy, bool drawing) {
  if (drawing < 2) {
      plot(drawing);
  }

  int i;
  long over = 0;

  long dx  = newx - xpos;
  long dy  = newy - ypos;
  int dirx = dx > 0 ? -1 : 1;
  int diry = dy > 0 ? 1 : -1;
  dx = abs(dx);
  dy = abs(dy);

  if (dx > dy) { 
    over = dx / 2; 
    for (i = 0; i < dx; i++) {
      xStepper.step(dirx);
      over += dy;
      if (over >= dx) {
        over -= dx;
        yStepper.step(diry);
      }
    }
  } else {
    over = dy / 2;
    for (i = 0; i < dy; i++) {
      yStepper.step(diry);
      over += dx;
      if (over >= dy) {
        over -= dy;
        xStepper.step(dirx);
      }
    }
  }

  xpos = newx;
  ypos = newy;
}

void plot(boolean penOnPaper) {
  if (penOnPaper)
    angle = 80;
  else
    angle = 25;

  servo.write(angle);
  if (penOnPaper != pPenOnPaper) delay(50);
  pPenOnPaper = penOnPaper;
}

void penUp(){
  servo.write(25);
}

void penDown(){
  servo.write(80);
}

void releaseMotors() {
  for (int i = 0; i < 4; i++) {
    digitalWrite(xPins[i], 0);
    digitalWrite(yPins[i], 0);
  }
  plot(false);
}

void homeYAxis(){
  yStepper.step(-3000);
}

void plotcustomImage(){
  Serial.println("CUSTOM IMG TIME");
  // Iterate over each row of the grid
  for (int row = 0; row < GRID_SIZE; row++){
    if (row %% 2 == 0) { // even row: left-to-right
      for (int col = 0; col < GRID_SIZE; col++){
        int index = row * GRID_SIZE + col;
        int byteIndex = index / 8;
        int bitIndex = index %% 8;
        uint8_t byteVal = pgm_read_byte_near(customImage + byteIndex);
        if ((byteVal >> bitIndex) & 1) {
          int x_end = row * customImagescale;
          int y_end = col * customImagescale * 2.65;
          Serial.print("X_goal: ");
          Serial.print(x_end);
          Serial.print(" Y_goal: ");
          Serial.print(y_end);
          Serial.println(" Plotting dot");
          line(x_end, y_end, 0);
          penDown();
          delay(80);
          penUp();
          delay(80);
        }
      }
    } else { // odd row: right-to-left
      for (int col = GRID_SIZE - 1; col >= 0; col--){
        int index = row * GRID_SIZE + col;
        int byteIndex = index / 8;
        int bitIndex = index %% 8;
        uint8_t byteVal = pgm_read_byte_near(customImage + byteIndex);
        if ((byteVal >> bitIndex) & 1) {
          int x_end = row * customImagescale;
          int y_end = col * customImagescale * 2.65;
          Serial.print("X_goal: ");
          Serial.print(x_end);
          Serial.print(" Y_goal: ");
          Serial.print(y_end);
          Serial.println(" Plotting dot");
          line(x_end, y_end, 0);
          penDown();
          delay(80);
          penUp();
          delay(80);
        }
      }
    }
  }
  releaseMotors();
}
"""

from sys import *
from sys import argv
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from os.path import exists
import math

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
grid_size = 60  # For example, 40 for more dots in the same space

# Define the fixed physical width (in steps) for the drawing.
desired_width = 1350


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
    # rotate the image 90 degrees to match the physical orientation
    matrix = np.rot90(matrix)
    plt.figure(figsize=(6, 6))
    plt.imshow(matrix, cmap='gray', interpolation='nearest')
    plt.title("Image Preview (1 = dot, 0 = blank)")
    plt.show(block=False)


def checkMakeFile():
    makeFile = input("Do you want to create code for this image? (Y/n) > ")
    if makeFile.lower() in ["y", "1", "true"]:
        print("Writing file...")
        writeFile()
    elif makeFile.lower() in ["n", "0", "false"]:
        print("No file created. Exiting...")
        exit()
    else:
        print("Not a valid option. Options: (Y/N)")
        checkMakeFile()


def writeFile():
    filename = "LabelMakerCustomImage.ino"
    with open(filename, 'w') as file:
        generatedCode = code % (grid_size, desired_width, byte_array_str)
        file.write(generatedCode)
    print(f"Arduino code file created. Filename: {filename}")
    print("Exiting...")
    exit()


# Process the image: generate a binary grid and pack it into a byte array.
matrix = generate_bitmap(image_path, grid_size, place_on_dark)
plot_bitmap(matrix)
byte_array = pack_bitmap(matrix, grid_size)

# Format the byte array as a C array string, e.g., {0x3F, 0xA7, ...}
byte_array_str = "{"
byte_array_str += ", ".join("0x%02X" % b for b in byte_array)
byte_array_str += "}"

checkMakeFile()

# Wait until the plot window is closed
plotNum = plt.gcf().number
while plt.fignum_exists(plotNum):
    plt.pause(0.1)
