code = """//This is the Custom Image hack for the Hack Pack LabelMaker

//////////////////////////////////////////////////
//           ASCII Art Preview                  //
//////////////////////////////////////////////////
/*
%s
*/

//////////////////////////////////////////////////
//               LIBRARIES                    //
//////////////////////////////////////////////////
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Stepper.h>
#include <ezButton.h>
#include <Servo.h>

//////////////////////////////////////////////////
//          PINS AND PARAMETERS               //
//////////////////////////////////////////////////

LiquidCrystal_I2C lcd(0x27, 16, 2);  // Set the LCD address to 0x27 for a 16x2 display

ezButton button1(14); // joystick button handler
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
//   JOYSTICK, MOTOR, SERVO, ETC. SETUP         //
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
//          BITMAP IMAGE DATA                 //
//////////////////////////////////////////////////

// The image is stored as a bit-packed array. Each bit represents a dot (1 = draw, 0 = skip).
// The bits are stored in serpentine order: even rows left-to-right, odd rows right-to-left.
const uint8_t customImage[BITMAP_SIZE] = %s;

//////////////////////////////////////////////////
//                SETUP                       //
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

//////////////////////////////////////////////////
//                LOOP                        //
//////////////////////////////////////////////////
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
        uint8_t byteVal = customImage[byteIndex];
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
      for (int col = GRID_SIZE - 1; col >= 0; col--){ // columns backwards saves some movement
        int index = (row+1) * GRID_SIZE - col - 1; // serpentine order
        int byteIndex = index / 8;
        int bitIndex = index %% 8;
        uint8_t byteVal = customImage[byteIndex];
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
