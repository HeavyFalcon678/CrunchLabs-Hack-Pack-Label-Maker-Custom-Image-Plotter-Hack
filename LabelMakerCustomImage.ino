//This is the Custom Image hack for the Hack Pack LabelMaker


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
const long customImageSize = 345;

//////////////////////////////////////////////////
          //  LOGO VECTOR  //
//////////////////////////////////////////////////

//the first number is X coordinate, second is Y coordinate, and third is pen up / down (0 = up)

const uint8_t customImage[][2] = {{0, 11}, {0, 12}, {1, 15}, {1, 14}, {1, 13}, {1, 12}, {1, 11}, {1, 10}, {1, 9}, {1, 8}, {1, 7}, {1, 6}, {2, 5}, {2, 6}, {2, 7}, {2, 8}, {2, 9}, {2, 10}, {2, 11}, {2, 12}, {2, 13}, {2, 14}, {2, 15}, {2, 16}, {3, 19}, {3, 18}, {3, 17}, {3, 16}, {3, 15}, {3, 14}, {3, 13}, {3, 12}, {3, 11}, {3, 10}, {3, 9}, {3, 8}, {3, 7}, {3, 6}, {3, 5}, {3, 4}, {4, 3}, {4, 4}, {4, 5}, {4, 6}, {4, 7}, {4, 8}, {4, 9}, {4, 10}, {4, 11}, {4, 12}, {4, 13}, {4, 14}, {4, 15}, {4, 16}, {4, 17}, {4, 18}, {4, 19}, {4, 20}, {5, 21}, {5, 20}, {5, 19}, {5, 18}, {5, 17}, {5, 16}, {5, 15}, {5, 14}, {5, 13}, {5, 12}, {5, 11}, {5, 10}, {5, 9}, {5, 8}, {5, 7}, {5, 6}, {5, 5}, {5, 4}, {5, 3}, {5, 2}, {6, 1}, {6, 2}, {6, 3}, {6, 4}, {6, 5}, {6, 6}, {6, 7}, {6, 8}, {6, 9}, {6, 10}, {6, 11}, {6, 12}, {6, 13}, {6, 14}, {6, 15}, {6, 16}, {6, 17}, {6, 18}, {6, 19}, {6, 20}, {6, 21}, {6, 22}, {7, 22}, {7, 21}, {7, 20}, {7, 19}, {7, 18}, {7, 17}, {7, 16}, {7, 15}, {7, 14}, {7, 13}, {7, 12}, {7, 11}, {7, 10}, {7, 9}, {7, 8}, {7, 7}, {7, 6}, {7, 5}, {7, 4}, {7, 3}, {7, 2}, {7, 1}, {8, 1}, {8, 2}, {8, 3}, {8, 4}, {8, 5}, {8, 6}, {8, 7}, {8, 8}, {8, 9}, {8, 10}, {8, 11}, {8, 12}, {8, 13}, {8, 14}, {8, 15}, {8, 16}, {8, 19}, {8, 20}, {8, 21}, {8, 22}, {8, 23}, {9, 23}, {9, 22}, {9, 21}, {9, 20}, {9, 19}, {9, 18}, {9, 16}, {9, 15}, {9, 14}, {9, 13}, {9, 12}, {9, 11}, {9, 10}, {9, 9}, {9, 8}, {9, 7}, {9, 6}, {9, 5}, {9, 4}, {9, 3}, {9, 2}, {9, 1}, {10, 1}, {10, 2}, {10, 3}, {10, 4}, {10, 5}, {10, 6}, {10, 7}, {10, 8}, {10, 9}, {10, 10}, {10, 11}, {10, 12}, {10, 13}, {10, 14}, {10, 15}, {10, 16}, {10, 17}, {10, 18}, {10, 19}, {10, 20}, {10, 21}, {10, 22}, {10, 23}, {11, 22}, {11, 21}, {11, 19}, {11, 18}, {11, 17}, {11, 16}, {11, 14}, {11, 13}, {11, 12}, {11, 11}, {11, 10}, {11, 9}, {11, 8}, {11, 7}, {11, 6}, {11, 5}, {11, 4}, {11, 3}, {11, 2}, {11, 1}, {12, 2}, {12, 3}, {12, 4}, {12, 9}, {12, 10}, {12, 11}, {12, 12}, {12, 13}, {12, 14}, {12, 16}, {12, 17}, {12, 18}, {12, 21}, {12, 22}, {12, 23}, {13, 23}, {13, 22}, {13, 21}, {13, 20}, {13, 19}, {13, 18}, {13, 17}, {13, 15}, {13, 14}, {13, 13}, {13, 12}, {13, 11}, {13, 10}, {13, 9}, {13, 3}, {14, 10}, {14, 11}, {14, 12}, {14, 13}, {14, 14}, {14, 15}, {14, 16}, {14, 17}, {14, 18}, {14, 19}, {14, 20}, {14, 21}, {14, 22}, {14, 23}, {15, 23}, {15, 22}, {15, 21}, {15, 20}, {15, 19}, {15, 18}, {15, 17}, {15, 16}, {15, 15}, {15, 14}, {15, 13}, {15, 12}, {15, 11}, {16, 12}, {16, 13}, {16, 14}, {16, 15}, {16, 16}, {16, 17}, {16, 18}, {16, 19}, {16, 20}, {16, 21}, {16, 22}, {17, 22}, {17, 21}, {17, 20}, {17, 19}, {17, 18}, {17, 17}, {17, 16}, {17, 15}, {17, 14}, {17, 13}, {17, 12}, {18, 12}, {18, 13}, {18, 14}, {18, 15}, {18, 16}, {18, 17}, {18, 18}, {18, 19}, {18, 20}, {18, 21}, {19, 20}, {19, 19}, {19, 18}, {19, 17}, {19, 16}, {19, 15}, {19, 14}, {19, 13}, {19, 12}, {20, 12}, {20, 13}, {20, 14}, {20, 15}, {20, 16}, {20, 17}, {20, 18}, {20, 19}, {20, 20}, {21, 20}, {21, 19}, {21, 18}, {21, 17}, {21, 16}, {21, 15}, {21, 14}, {21, 13}, {21, 12}, {21, 11}, {21, 10}, {22, 10}, {22, 11}, {22, 12}, {22, 13}, {22, 14}, {22, 15}, {22, 16}, {22, 17}, {22, 18}, {22, 19}, {23, 16}, {23, 15}, {23, 14}, {23, 13}, {23, 12}, {23, 11}, {23, 10}, {24, 13}, {24, 14}}
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
}