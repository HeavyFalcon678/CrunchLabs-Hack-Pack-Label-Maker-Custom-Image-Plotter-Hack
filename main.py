code = """//This is the Custom Image hack for the Hack Pack LabelMaker


//////////////////////////////////////////////////
                //  LIBRARIES  //
//////////////////////////////////////////////////
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Stepper.h>
#include <ezButton.h>
#include <Servo.h>

//////////////////////////////////////////////////
          //  PINS AND PARAMETERS  //
//////////////////////////////////////////////////

LiquidCrystal_I2C lcd(0x27, 16, 2);  // Set the LCD address to 0x27 for a 16x2 display

ezButton button1(14); //joystick button handler
#define INIT_MSG "Initializing..." // Text to display on startup
#define MODE_NAME "PLOT CUSTOM IMG " //these are variables for the text which is displayed in different menus. 
#define PLOTTING "   PLOTTING...  " //try changing these, or making new ones and adding conditions for when they are used


// Joystick setup
const int joystickXPin = A2;  // Connect the joystick X-axis to this analog pin
const int joystickYPin = A1;  // Connect the joystick Y-axis to this analog pin
const int joystickButtonThreshold = 200;  // Adjust this threshold value based on your joystick

// Menu parameters
int currentCharacter = 0; //keep track of which character is currently displayed under the cursor
int cursorPosition = 0; //keeps track of the cursor position (left to right) on the screen
int currentPage = 0; //keeps track of the current page for menus
const int charactersPerPage = 16; //number of characters that can fit on one row of the screen

// Stepper motor parameters
const int stepCount = 200;
const int stepsPerRevolution = 2048;

// initialize the stepper library for both steppers:
Stepper xStepper(stepsPerRevolution, 6,8,7,9);
Stepper yStepper(stepsPerRevolution, 2,4,3,5); 

int xPins[4] = {6, 8, 7, 9};  // pins for x-motor coils
int yPins[4] = {2, 4, 3, 5};    // pins for y-motor coils

//Servo
const int SERVO_PIN  = 13;
Servo servo;
int angle = 30; // the current angle of servo motor


// Creates states to store what the current menu and joystick states are
// Decoupling the state from other functions is good because it means the sensor / screen aren't hardcoded into every single action and can be handled at a higher level
enum State { MainMenu, Editing, PrintConfirmation, Printing, plotCustomImg };
State currentState = MainMenu;
State prevState = Printing;

enum jState {LEFT, RIGHT, UP, DOWN, MIDDLE, UPRIGHT, UPLEFT, DOWNRIGHT, DOWNLEFT};
jState joyState = MIDDLE;
jState prevJoyState = MIDDLE;

boolean pPenOnPaper = false; // pen on paper in previous cycle
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
const long customImageSize = %s;

//////////////////////////////////////////////////
          //  LOGO VECTOR  //
//////////////////////////////////////////////////

//the first number is X coordinate, second is Y coordinate, and third is pen up / down (0 = up)

const uint8_t customImage[][2] = %s
;

//////////////////////////////////////////////////
                //  S E T U P  //
//////////////////////////////////////////////////
void setup() {
  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print(INIT_MSG); // print start up message

  pinMode(LED_BUILTIN, OUTPUT);

  Serial.begin(9600);

  button1.setDebounceTime(50);

  servo.attach(SERVO_PIN); // attaches the servo pin to the servo object
  servo.write(angle);

  plot(false);

  // set the speed of the motors 
  yStepper.setSpeed(10);    // set first stepper speed
  xStepper.setSpeed(8);   // set second stepper speed

  penUp(); //ensure that the servo is lifting the pen carriage away from the tape
  homeYAxis();//lower the Y axis all the way to the bottom

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

  switch (currentState) { //state machine that determines what to do with the input controls based on what mode the device is in
  
    case plotCustomImg:
      {
        if (prevState != plotCustomImg){
          lcd.clear();
          lcd.setCursor(0,0);
          lcd.print(MODE_NAME); //display the mode name
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

      if (button1.isPressed()) { //handles clicking options in text size setting
        lcd.clear();
        lcd.noBlink();
        currentState = plotCustomImg;
        prevState = MainMenu;
      }
    }
      break;
  }
}

void line(int newx,int newy, bool drawing) { 
//this function is an implementation of bresenhams line algorithm
//this algorithm basically finds the slope between any two points, allowing us to figure out how many steps each motor should do to move smoothly to the target
//in order to do this, we give this function our next X (newx) and Y (newy) coordinates, and whether the pen should be up or down (drawing)

  if (drawing < 2) { //checks if we should be drawing and puts the pen up or down based on that.
      plot(drawing); // dashed: 0= don't draw / 1=draw / 2... = draw dashed with variable dash width
  } else {
     
  }
  
  int i;
  long over= 0;
  
  long dx  = newx-xpos; //calculate the difference between where we are (xpos) and where we want to be (newx)
  long dy  = newy-ypos; //difference for Y
  int dirx = dx>0?-1:1; //this is called a ternary operator, it's basically saying: if dx is greater than 0, then dirx = -1, if dx is less than or equal to 0, dirx = 1.
  int diry = dy>0?1:-1; //this is called a ternary operator, it's basically saying: if dy is greater than 0, then diry = 1, if dy is less than or equal to 0, diry = -1.
  //the reason one of these ^ is inverted logic (1/-1) is due to the direction these motors rotate in the system.

  dx = abs(dx); //normalize the dx/dy values so that they are positive.
  dy = abs(dy); //abs() is taking the "absolute value" - basically it removes the negative sign from negative numbers

    //the following nested If statements check which change is greater, and use that to determine which coordinate (x or y) get's treated as the rise or the run in the slope calculation
    //we have to do this because technically bresenhams only works for the positive quandrant of the cartesian coordinate grid,
    // so we are just flipping the values around to get the line moving in the correct direction relative to it's current position (instead of just up an to the right)
  if(dx>dy) { 
    over = dx/2; 
    for(i=0; i<dx; i++) { //for however much our current position differs from the target,
      xStepper.step(dirx); //do a step in that direction (remember, dirx is always going to be either 1 or -1 from the ternary operator above)

      // Serial.print("Xsteps: ");
      // Serial.print(dirx);
      // Serial.print("  ");

      over += dy;
      if(over>=dx) {
        over -= dx;
        
        // Serial.print("Ysteps: ");
        // Serial.println(diry);

        yStepper.step(diry); 
      }
      //delay(1);
    }
  } else {
    over = dy/2;
    for(i=0; i<dy; i++) {
      yStepper.step(diry);
      // Serial.print("Ysteps: ");
      // Serial.print(diry);
      // Serial.print("  ");
      over += dx;
      if(over >= dy) {
        over -= dy;
        // Serial.print("Xsteps: ");
        // Serial.println(dirx);
        xStepper.step(dirx);
      }
      //delay(1);
    }
  }

  xpos = newx; //store positions
  ypos = newy; //store positions
}


void plot(boolean penOnPaper) { //used to handle lifting or lowering the pen on to the tape
  if(penOnPaper){//if the pen is already up, put it down
    angle = 80;
    } else {//if down, then lift up.
    angle = 25;
    }
    servo.write(angle);//actuate the servo to either position.
    if (penOnPaper != pPenOnPaper) delay(50); //gives the servo time to move before jumping into the next action
    pPenOnPaper = penOnPaper; //store the previous state.
}

void penUp(){ //singular command to lift the pen up
  servo.write(25);
}

void penDown(){ //singular command to put the pen down
  servo.write(80);
}

void releaseMotors() {
  for (int i = 0; i < 4; i++) { //deactivates all the motor coils
    digitalWrite(xPins[i], 0); //just picks each motor pin and send 0 voltage
    digitalWrite(yPins[i], 0);
  }
  plot(false);
}

void homeYAxis(){
  yStepper.step(-3000); //lowers the pen holder to it's lowest position.
}

void plotcustomImage(){ //plots a simplified version of your image, stored as coordinates in memory in the customImage array at the top
  int customImagescale = 54; //multiplied scale 
  Serial.println("CUSTOM IMG TIME");
  for(int i = 0; i < customImageSize; i++){//for each point in the shape we want to draw (in this case 22 points) execute the following 
    //(we step from one point to the next by increasing i by 1 each for loop, so we access the coordinates stored at row i)

    int x_end = (customImage[i][0])*customImagescale; //get the X for the point we want to hit
    int y_end = (customImage[i][1])*customImagescale*2.65;// get it's Y
    

    Serial.print("X_goal: ");
    Serial.print(x_end);
    Serial.print(" Y_goal: ");
    Serial.print(y_end);
    Serial.print(" Draw: ");
    Serial.println(customImage[i][2]);
    line(x_end, y_end, 0); //use our line function to head to that X and Y position, the third value is the pen up/down.
    penDown();
    delay(80);
    penUp();
    delay(80);
  }
  releaseMotors();
}"""


from sys import *
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from os.path import exists

# Variables
place_on_dark = argv[2]

# Makes sure file is a jpg or png
string = str(argv[1])
chopped = ""
N = 4
while(N > 0):
  chopped += string[-N]
  N = N-1

if exists(argv[1]) and (chopped == ".png" or chopped == ".jpg" or chopped == "jpeg"):
  
  image_path = argv[1]
else:
  print("ERROR: Image not found or invalid filename.")
  exit()
place_on_dark = int(place_on_dark)
grid_size = 25
# Constants - do not change


def generate_dot_positions(image_path, grid_size=20, place_on_dark=False):
    image = Image.open(image_path)
    image = image.convert('L') # Greyscale everything
    image = image.resize((grid_size, grid_size)) # Resize image to the size of our label maker

    image = image.rotate(-90) # The image is always rotated for some reason
    pixels = np.array(image)
    average_brightness = np.mean(pixels)
    
    # Write the positions of pixels that are above/below (depending on place_on_dark) the average threshold  
    dot_positions = []
    for i in range(grid_size):
        
        # Store this col of calculated dots
        nextCol = []
        
        for j in range(grid_size):
            if (place_on_dark and pixels[i, j] < average_brightness) or (not place_on_dark and pixels[i, j] > average_brightness):
                nextCol.append((i, j))
        
        # Reverse every other one so it draws on down and up passes
        if i % 2 == 1:
           nextCol.reverse()

        dot_positions = [*dot_positions, *nextCol]
    
    return dot_positions

def plot_dots(dot_positions, grid_size=20):
    x_coords, y_coords = zip(*dot_positions) if dot_positions else ([], [])
    
    # I think plt renders x,y upside down?
    y_coords = [grid_size - 1 - y for y in y_coords]
    
    # Setup the plot
    plt.figure(figsize=(6, 6))
    plt.scatter(x_coords, y_coords, color='black')
    plt.xlim(0, grid_size)
    plt.ylim(0, grid_size)
    plt.title("Image Preview")
    plt.gca().invert_yaxis()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True)
    plt.show(block=False)

def checkMakeFile():
  makeFile = input("Do you want to create code for this image? (Y/n) > ")
  if makeFile == "Y" or makeFile == "y" or makeFile == "1" or makeFile == "True" or makeFile == "true":
    print("Writing file...")
    writeFile()
  elif makeFile == "n" or makeFile == "N" or makeFile == "0" or makeFile == "False" or makeFile == "false":
    print("No file created. Exiting...")
    exit()    
  else:
    print("Not a valid option. Options: (Y/N)") 
    checkMakeFile()
    


def writeFile():
  filename = "LabelMakerCustomImage.ino"
  file = open(filename, 'w')
  file.truncate()

  generatedCode = code % (length, img)

  file.write(generatedCode)
  file.close()
  print(f"Arduino code file created. Filename: {filename}")
  print("Exiting...")
  exit()

# Process and show results
dots = generate_dot_positions(image_path, grid_size, place_on_dark)
plot_dots(dots, grid_size)
#print(dots)

img = ""

for i in str(dots):
    if i == "(":
        img += "{"
    elif i == ")":
        img += "}"
    elif i == "]":
        img += "}"
    elif i == "[":
        img += "{"
    else:
        img += i
        
#print(img)        
length = len(dots)
# Expand the dots into pen-up pen-down points

checkMakeFile()


# Wait for plot to be closed
plotNum = plt.gcf().number
while plt.fignum_exists(plotNum):
    plt.pause(0.1)
