#define ON  0x0 // low voltage  = on   (see relais specifications)
#define OFF 0x1 // high voltage = off 

// relais control connection pins
uint8_t PIN_GREEN = 4;
uint8_t PIN_YELLOW = 5;
uint8_t PIN_RED = 7;
uint8_t PINS[] = { PIN_GREEN, PIN_YELLOW, PIN_RED };

void setup() {
  Serial.begin(9600);
  Serial.flush();

  // define all pins as output and set them to OFF, 
  // which is necessary if a low-level-trigger relais is used
  for (uint8_t pin : PINS) {
    pinMode(pin, OUTPUT);
    set(pin, OFF);
  }
}

int queue[4]; // create queue array of size 4 (maximum command length is now 4 bytes)
int cursor = 0; // keep track of current queue position

void loop() {

  while (Serial.available()) {
    // read the current byte and add it to the queue array
    int value = Serial.read();

    // 0xff as command terminator -> process command bytes
    if (value == 0xff) { 

      // reply our data for debug
      for (int current : queue) {
        Serial.write(current);
      }
      Serial.flush();

      // process our collected data queue, reset, startover
      execute();
      cursor = 0;
      delete[] queue;
      return;
    }

    queue[cursor] = value;
    cursor++;
  }
}

void execute() {
  int mode = queue[0];
  int data = queue[1];

  set(PINS[mode], data ? ON : OFF);
}

void set(uint8_t pin, uint8_t mode) {
  digitalWrite(pin, mode);
}
