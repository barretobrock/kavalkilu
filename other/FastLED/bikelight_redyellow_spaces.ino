#include "FastLED.h"

// Data pins
#define FORK_PIN 3 // Blue
#define R_LOWER_PIN 4
#define L_LOWER_PIN 5
#define R_UPPER_PIN 6
#define L_UPPER_PIN 7
#define R_BACK_PIN 8
#define L_BACK_PIN 9
// LEDs
#define FORK_LEDS 14
#define UL_LEDS 53
#define R_BACK_LEDS 26
#define L_BACK_LEDS 56
// Other settings
#define LED_TYPE WS2812B
#define COLOR_ORDER GRB
#define BRIGHTNESS 50

// LED positioning
int backOffset = 35,
    backStop = backOffset + 26, // Where the tail light section begins
    totalLen = backStop;

// Light strips
CRGB fleds[FORK_LEDS],
     ruleds[UL_LEDS],
     luleds[UL_LEDS],
     rlleds[UL_LEDS],
     llleds[UL_LEDS],
     lbleds[L_BACK_LEDS],
     rbleds[R_BACK_LEDS];

void setup() {
  delay(2000);
  // Initialize the fork LEDs
  FastLED.addLeds<LED_TYPE, FORK_PIN, COLOR_ORDER>(fleds, FORK_LEDS).setCorrection(TypicalLEDStrip);
  // Initialize the Lower leg LEDs
  FastLED.addLeds<LED_TYPE, R_LOWER_PIN, COLOR_ORDER>(rlleds, UL_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.addLeds<LED_TYPE, L_LOWER_PIN, COLOR_ORDER>(llleds, UL_LEDS).setCorrection(TypicalLEDStrip);
  // Initialize the Upper leg LEDs
  FastLED.addLeds<LED_TYPE, R_UPPER_PIN, COLOR_ORDER>(ruleds, UL_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.addLeds<LED_TYPE, L_UPPER_PIN, COLOR_ORDER>(luleds, UL_LEDS).setCorrection(TypicalLEDStrip);
  // Initialize rear and tail LEDS
  FastLED.addLeds<LED_TYPE, R_BACK_PIN, COLOR_ORDER>(rbleds, R_BACK_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.addLeds<LED_TYPE, L_BACK_PIN, COLOR_ORDER>(lbleds, L_BACK_LEDS).setCorrection(TypicalLEDStrip);
  // set global brightness
  FastLED.setBrightness(BRIGHTNESS);
  // set all LEDs to black starting out
  FastLED.clear();
  delay(1000);
}

void pulses(uint8_t h, uint8_t s, uint8_t v, int wait) {
  // Issue a front <-> back pulse
  CRGB col = CHSV(h, s, v);
  CRGB backcol;
  CRGB ocol = CHSV(random8(0, 120), 255, 255);
  CRGB ocol2 = CHSV(random8(0, 120), 255, 255);
  CRGB blk = CRGB::Black;

  // Back lights are a bit different in hue
  if (h > 10)
  {
    backcol = CHSV(h + 10, s, v);
  } else {
    backcol = col;
  }
  for (int i=0; i<totalLen; i++) {
    if (i < FORK_LEDS) {
      fleds[i] = col;
      if (i < FORK_LEDS - 1) {
        fleds[i+1] = blk;
      }
    }
    if (i < UL_LEDS) {
      ruleds[i] = col;
      luleds[i] = col;
      rlleds[i] = col;
      llleds[i] = col;
      if (i < UL_LEDS - 1) {
        ruleds[i+1] = blk;
        luleds[i+1] = blk;
        rlleds[i+1] = blk;
        llleds[i+1] = blk;
      }
    }
    if (i >= backOffset && i < backStop) {
      lbleds[i - backOffset] = backcol;
      rbleds[i - backOffset] = backcol;
      if (i < backStop - 1) {
        lbleds[i - backOffset + 1] = blk;
        rbleds[i - backOffset + 1] = blk;
      }
    }

    if (i % 20 == 0 || (i + 1) % 20 == 0) {
      for(int x = 26, y=36, z=46; x<36, y<46, z<56; x++, y++, z++)
      {
        // Tail light stuff
        lbleds[x] = ocol;
        lbleds[y] = ocol2;
        lbleds[z] = ocol;
      }
    } else if (i % 10 == 0) {
      for(int x = 26, y=36, z=46; x<36, y<46, z<56; x++, y++, z++)
      {
        // Tail light stuff
        //lbleds[x] = ocol;
        lbleds[y] = ocol2;
        //lbleds[z] = ocol;
      }
    } else {
      for(int x = 26, y=36, z=46; x<36, y<46, z<56; x++, y++, z++)
      {
        // Tail light stuff
        lbleds[x] = blk;
        lbleds[y] = blk;
        lbleds[z] = blk;
      }
    }

    FastLED.show();
    delay(wait);
  }
}

/*
void tail_arrows(uint8_t h, uint8_t s, uint8_t v, int wait) {
  // Tail lights
  CRGB col = CHSV(h, s, v);
  EVERY_N_MILLISECONDS(wait)
  {
    for (int i=26,j=45,k=46; i<36,j>37,k<56; i++,j--,k++)
    {
      if (i % 2 == 0) {
        lbleds[i] = col;
        lbleds[j] = CRGB::Black;
        lbleds[k] = col;
      } else {
        lbleds[i] = CRGB::Black;
        lbleds[j] = col;
        lbleds[k] = CRGB::Black;
      }
      FastLED.show();
    }
  }
}
*/

void tail_fadeall() { for(int i = 26; i < 56; i++) { lbleds[i] = CRGB::Black; } }

void tail_cylon(uint8_t h, uint8_t s, uint8_t v, int wait) {
  // Tail lights
  CRGB col1 = CHSV(random8(0,80), s, v);
  CRGB col2 = CHSV(random8(0,80), s, v);
  CRGB col3 = CHSV(random8(0,80), s, v);
  for (int i=26,j=45,k=46; i<36,j>37,k<56; i++,j--,k++)
  {
    lbleds[i] = col1;
    lbleds[j] = col2;
    lbleds[k] = col3;
    // Show the leds
    FastLED.show();
    delay(wait);
    //tail_fadeall();
    //FastLED.show();
    // Wait a little bit before we loop around and do it again
  }
  col1 = CHSV(random8(0,80), s, v);
  col2 = CHSV(random8(0,80), s, v);
  col3 = CHSV(random8(0,80), s, v);
  for (int i=35,j=36,k=55; i>25,j<46,k>45; i--,j++,k--)
  {
    lbleds[i] = col1;
    lbleds[j] = col2;
    lbleds[k] = col3;
    // Show the leds
    delay(wait);
    FastLED.show();
    //tail_fadeall();
    //FastLED.show();
    // Wait a little bit before we loop around and do it again
  }
}


// main program
void loop() {
  pulses(0, 255, 255, 10);
  pulses(32, 255, 255, 10);
  pulses(random(0, 64), 255, 255, 10);
  pulses(0, 255, 255, 10);
  pulses(15, 255, 255, 10);
}

