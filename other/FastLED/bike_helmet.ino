#include "FastLED.h"

// Data pins
#define RIGHT_PIN 2
#define LEFT_PIN 3
// LEDs
#define LEFT_LEDS 28
#define RIGHT_LEDS 28
// Other settings
#define LED_TYPE WS2812B
#define COLOR_ORDER GRB
#define BRIGHTNESS 50

// Light strips
CRGB lleds[LEFT_LEDS],
     rleds[RIGHT_LEDS];

uint32_t color = CRGB::Red;
uint32_t col_red = CRGB::Red;
uint32_t black = CRGB::Black;
uint32_t col_pick;

void setup() {
  delay(2000); // initial delay of a few seconds is recommended
  // Initialize LEDs
  FastLED.addLeds<LED_TYPE, LEFT_PIN, COLOR_ORDER>(lleds, LEFT_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.addLeds<LED_TYPE, RIGHT_PIN, COLOR_ORDER>(rleds, RIGHT_LEDS).setCorrection(TypicalLEDStrip);
  // set global brightness
  FastLED.setBrightness(BRIGHTNESS);
  // set all LEDs to black starting out
  FastLED.clear();
}

void check_strips(struct CRGB *led_group, uint8_t from, uint8_t to, uint32_t color) {
  unsigned int barLength = abs(to - from) + 1;
  for (int i = from; i < barLength; i++) {
    led_group[i] = color;
  }
}

int done=0;
// main program
void loop() {

  for (int j=0; j<7; j++) {
    lleds[j] = black;
    rleds[j] = black;
  }
  FastLED.show();
  delay(100);
  for (int j=0; j<7; j++) {
    lleds[j] = col_red;
    rleds[j] = col_red;
  }
  FastLED.show();
  delay(100);
  // Top Helmet
  if (done == 0) {
    for (int i = 7; i < LEFT_LEDS; i++) {
      lleds[i] = col_red;
      rleds[i] = col_red;
      FastLED.show();
      delay(50);
    }
    done = 1;
  }
}
