#include "nRF24L01.h" //NRF24L01 library created by TMRh20 https://github.com/TMRh20/RF24
#include "RF24.h"
#include "SPI.h"

// Pin connected to Signal pin of leak detector
#define LEAK_PIN 4
// Signaling (alarm and LED) pin
#define SIGNAL_PIN 3

// ce, csn pins
RF24 radio(9, 10);
const uint64_t pipe = 0xE6E6E6E6E6E6; // Needs to be the same for communicating between 2 NRF24L01
int SentMessage[1] = {000}; // Used to store value before being sent through the NRF24L01

void setup(void) {
  // Setup water sensor as input
  pinMode(LEAK_PIN, INPUT);
  // Setup LED as output
  pinMode(SIGNAL_PIN, OUTPUT);

  radio.begin();
  // Max power
  radio.setPALevel(RF24_PA_MAX);
  // Min speed (likely for better range?)
  radio.setDataRate(RF24_250KBPS);
  // 8 bits CRC
  radio.setCRCLength(RF24_CRC_8);
  // Increase the delay between retries & # of retries
  radio.setRetries(15, 15);
  radio.setAutoAck(false);
  radio.openWritingPipe(pipe); // Get NRF24L01 ready to transmit
}

void sound_alarm() {
  for (int i=0; i<50; i++) {
    digitalWrite(SIGNAL_PIN, HIGH);
    delay(10);
    digitalWrite(SIGNAL_PIN, LOW);
    delay(10);
  }
}

void loop(void) {
  /* Water detector will switch LOW when water is detected
   *  LED will then be illuminated and activate the buzzer when water is detected
   *  and swtich both off when no water is present
   */
  if (digitalRead(LEAK_PIN) == HIGH) {
    sound_alarm();
    SentMessage[0] = 1;
    radio.write(SentMessage, 1); // Send value through NRF24L01
  } else {
    digitalWrite(SIGNAL_PIN, LOW);
  }
  delay(500);
}