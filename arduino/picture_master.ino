/*
  picture_master.ino

  Purpose
  - Runs on an Arduino Mega2560 and controls two ILI9488 TFT displays and two touch controllers.
  - Loads images from an SD card (raw RGB565 or 24-bit BMP), displays left/right images,
    and exposes a simple touch-selection UI.
  - Receives commands over USB Serial to show images, forwards line-control commands to the
    line-follow robot via the hardware UART `Serial1`, and reports ACKs/timeouts back over USB.

  Hardware summary
  - Mega2560 hardware UART: `Serial1` (RX1 = D19, TX1 = D18) used to communicate with the
    line robot (HC-05 or a connected UNO). USB `Serial` is used for PC/debug control.
  - Two ILI9488 TFT panels (left/right) using shared SPI and separate CS/DC/RST pins.
  - SD card on SPI with CS = D6 stores numbered image files (4-digit IDs, e.g. 0012.BMP).
  - Two touch controllers attached to a shared touch bus with separate CS/IRQ lines.

  Protocol (high level)
  - Commands received from USB or Bluetooth (format examples):
      TO;PIC;CMD;SHOW;A;B   -- display image A on left, B on right
      TO;LINE;CMD;LEFT      -- forward to line robot (via Serial1)
  - Responses / events emitted:
      ACK;FROM;PIC;STATE;DONE;A;...;B;...  -- image load result
      DEC;FROM;PIC;SEL;LEFT;A;...;B;...    -- touch selection decision

  Notes
  - This file focuses on robustness: it validates image formats/sizes, provides fallbacks
    when loading fails, and uses a modest read buffer for BMP decoding to keep memory usage low.
  - Do not change hardware pin constants without updating wiring and the README.
 */

#include <LCDWIKI_GUI.h>
#include <LCDWIKI_SPI.h>
#include <LCDWIKI_TOUCH.h>
#include <SPI.h>
#include <SD.h>

// Picture master Mega 2560 pinout:
// TFT1 (left):   CS=D10, DC=D9, RST=D8
// TFT2 (right):  CS=A0, DC=A2, RST=D7
// Shared SPI:    MOSI=D51, MISO=D50, SCK=D52
// Line robot link: Serial1 (HC-05) (RX1=D19, TX1=D18)
// Touch bus:     CLK=D22, DO=D23, DIN=D24
// Left touch:    CS=D25, IRQ=D26
// Right touch:   CS=D27, IRQ=D28

// Hardware pin map.
const uint8_t TFT1_CS = 10;
const uint8_t TFT2_CS = A0;
const uint8_t TFT1_DC = 9;
const uint8_t TFT1_RST = 8;
const uint8_t TFT2_DC = A2;
const uint8_t TFT2_RST = 7;
const uint8_t TFT_LED = A3;

const uint8_t TOUCH_CLK = 22;
const uint8_t TOUCH_DO = 23;
const uint8_t TOUCH_DIN = 24;
const uint8_t LEFT_TOUCH_CS = 25;
const uint8_t LEFT_TOUCH_IRQ = 26;
const uint8_t RIGHT_TOUCH_CS = 27;
const uint8_t RIGHT_TOUCH_IRQ = 28;

LCDWIKI_SPI my_lcd1(ILI9488, TFT1_CS, TFT1_DC, TFT1_RST, TFT_LED);
LCDWIKI_SPI my_lcd2(ILI9488, TFT2_CS, TFT2_DC, TFT2_RST, TFT_LED);
LCDWIKI_TOUCH left_touch(LEFT_TOUCH_CS, TOUCH_CLK, TOUCH_DO, TOUCH_DIN, LEFT_TOUCH_IRQ);
LCDWIKI_TOUCH right_touch(RIGHT_TOUCH_CS, TOUCH_CLK, TOUCH_DO, TOUCH_DIN, RIGHT_TOUCH_IRQ);

#define BLACK   0x0000
#define BLUE    0x001F
#define RED     0xF800
#define GREEN   0x07E0
#define CYAN    0x07FF
#define MAGENTA 0xF81F
#define YELLOW  0xFFE0
#define WHITE   0xFFFF

// Blood-splat overlay colors.
static const uint16_t BLOOD_DARK = 0x2800;
static const uint16_t BLOOD_MAIN = 0x7800;
static const uint16_t BLOOD_BRIGHT = 0xB000;
static const uint16_t BLOOD_BLACKISH = 0x1000;

// SD card wiring:
// MOSI=D11, MISO=D12, SCK=D13, CS=D6
const uint8_t SD_CS_PIN = 6;

// Timeout waiting for ACK from the line robot after forwarding a command (milliseconds)
const unsigned long LINE_ACK_TIMEOUT = 25000;

bool sdReady = false;
bool selectionPending = false;
uint8_t selectedLeftImage = 0;
uint8_t selectedRightImage = 0;

String usbBuf;
String lineBuf;

bool lineAckPending = false;
unsigned long lineAckDeadline = 0;

// Utility: read little-endian 16-bit value from an open `File`.
// Used by BMP parser to interpret header fields.
static uint16_t read16(File &f)
{
  uint16_t result;
  ((uint8_t *)&result)[0] = f.read();
  ((uint8_t *)&result)[1] = f.read();
  return result;
}

// Utility: read little-endian 32-bit value from an open `File`.
// Used by BMP parser to obtain offsets, image dimensions, etc.
static uint32_t read32(File &f)
{
  uint32_t result;
  ((uint8_t *)&result)[0] = f.read();
  ((uint8_t *)&result)[1] = f.read();
  ((uint8_t *)&result)[2] = f.read();
  ((uint8_t *)&result)[3] = f.read();
  return result;
}

static const char *const IMAGE_EXTENSIONS[] = { ".RAW565", ".RGB565", ".565", ".RAW", ".BIN", ".BMP" };
static const uint8_t IMAGE_EXTENSION_COUNT = sizeof(IMAGE_EXTENSIONS) / sizeof(IMAGE_EXTENSIONS[0]);

// Return an estimate of free SRAM on AVR (Mega2560). Useful to size temporary buffers.
int freeRam() {
  extern int __heap_start, *__brkval;
  int v;
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval);
}

// Check whether an image file with ID `imgNum` exists on the SD card in any supported format.
// Accepts numeric IDs 1..9999 and looks for extensions defined in `IMAGE_EXTENSIONS`.
static bool imageExists(int imgNum)
{
  if (!sdReady || imgNum < 1 || imgNum > 9999) {
    return false;
  }
  char path[16];
  for (uint8_t i = 0; i < IMAGE_EXTENSION_COUNT; i++) {
    sprintf(path, "%04d%s", imgNum, IMAGE_EXTENSIONS[i]);
    if (SD.exists(path)) {
      return true;
    }
  }
  return false;
}

// Draw an image stored as raw RGB565 pixel data. The file must be exactly (width * height * 2)
// bytes to match the target display. Reads one row at a time into a temporary buffer to
// limit peak RAM usage and invokes `Draw_Pixe` for each pixel.
static bool drawRaw565File(LCDWIKI_SPI &lcd, File &imageFile)
{
  const uint16_t displayW = lcd.Get_Display_Width();
  const uint16_t displayH = lcd.Get_Display_Height();
  const uint32_t expectedSize = (uint32_t)displayW * displayH * 2UL;

  if (imageFile.size() != expectedSize) {
    Serial.print(F("Raw size mismatch: got "));
    Serial.print((unsigned long)imageFile.size());
    Serial.print(F(" expected "));
    Serial.println((unsigned long)expectedSize);
    return false;
  }

  // Push full blocks of pixels instead of individual pixels.
  // The chunk size is based on available SRAM with a safety margin.
  int ramBudget = freeRam() - 1024;
  if (ramBudget < 1024) {
    ramBudget = 1024;
  }

  uint32_t maxPixelsByRam = (uint32_t)ramBudget / 2UL;
  uint32_t maxPixelsInImage = (uint32_t)displayW * displayH;
  uint32_t pixelsPerChunk32 = (maxPixelsByRam < maxPixelsInImage) ? maxPixelsByRam : maxPixelsInImage;
  if (pixelsPerChunk32 < displayW) {
    pixelsPerChunk32 = displayW;
  }
  pixelsPerChunk32 -= (pixelsPerChunk32 % displayW);
  if (pixelsPerChunk32 == 0) {
    pixelsPerChunk32 = displayW;
  }
  uint16_t pixelsPerChunk = (uint16_t)pixelsPerChunk32;

  uint16_t *chunkBuf = (uint16_t *)malloc((size_t)pixelsPerChunk * sizeof(uint16_t));
  if (!chunkBuf) {
    return false;
  }

  lcd.Fill_Screen(BLACK);
  lcd.Set_Addr_Window(0, 0, displayW - 1, displayH - 1);

  bool firstChunk = true;
  uint32_t pixelsRemaining = (uint32_t)displayW * displayH;
  while (pixelsRemaining > 0) {
    uint16_t chunkPixels = (pixelsRemaining < pixelsPerChunk) ? (uint16_t)pixelsRemaining : pixelsPerChunk;
    uint32_t bytesNeeded = (uint32_t)chunkPixels * 2UL;
    if (imageFile.read((uint8_t *)chunkBuf, bytesNeeded) != (int)bytesNeeded) {
      free(chunkBuf);
      return false;
    }

    lcd.Push_Any_Color(chunkBuf, chunkPixels, firstChunk, 0);
    firstChunk = false;
    pixelsRemaining -= chunkPixels;
  }

  free(chunkBuf);
  return true;
}

// Decode and draw a 24-bit uncompressed BMP file. This implementation reads the BMP header,
// validates format constraints (24-bit, no compression), computes row offsets, and streams
// pixel data in small chunks to the display. The BMP loader supports both bottom-up and
// top-down images via the height sign.
static bool drawBmpFile(LCDWIKI_SPI &lcd, File &bmpFile)
{
  if (read16(bmpFile) != 0x4D42)
  {
    return false;
  }

  (void)read32(bmpFile);
  (void)read32(bmpFile);
  uint32_t bmpImageOffset = read32(bmpFile);
  uint32_t headerSize = read32(bmpFile);
  int32_t bmpWidth = (int32_t)read32(bmpFile);
  int32_t bmpHeight = (int32_t)read32(bmpFile);

  if (read16(bmpFile) != 1)
  {
    return false;
  }

  uint16_t bmpDepth = read16(bmpFile);
  uint32_t compression = read32(bmpFile);
  if (bmpDepth != 24 || compression != 0 || headerSize < 40)
  {
    return false;
  }

  bool flip = true;
  if (bmpHeight < 0)
  {
    bmpHeight = -bmpHeight;
    flip = false;
  }

  if (bmpWidth > lcd.Get_Display_Width() || bmpHeight > lcd.Get_Display_Height())
  {
    return false;
  }

  lcd.Fill_Screen(BLACK);
  lcd.Set_Addr_Window(0, 0, bmpWidth - 1, bmpHeight - 1);

  uint32_t rowSize = (bmpWidth * 3 + 3) & ~3;

  // Read one whole row at a time, convert it to RGB565 in SRAM, and push the row as a block.
  size_t srcBytes = (size_t)rowSize;
  size_t dstPixels = (size_t)bmpWidth;
  uint8_t *srcRow = (uint8_t *)malloc(srcBytes);
  uint16_t *dstRow = (uint16_t *)malloc(dstPixels * sizeof(uint16_t));
  if (!srcRow || !dstRow) {
    if (srcRow) free(srcRow);
    if (dstRow) free(dstRow);
    return false;
  }

  bool firstChunk = true;
  for (int32_t row = 0; row < bmpHeight; row++)
  {
    uint32_t pos = bmpImageOffset + (flip ? (bmpHeight - 1 - row) : row) * rowSize;
    bmpFile.seek(pos);

    if (bmpFile.read(srcRow, srcBytes) != (int)srcBytes)
    {
      free(srcRow);
      free(dstRow);
      return false;
    }

    for (int32_t x = 0; x < bmpWidth; x++)
    {
      uint32_t idx = (uint32_t)x * 3UL;
      uint8_t b = srcRow[idx];
      uint8_t g = srcRow[idx + 1];
      uint8_t r = srcRow[idx + 2];
      dstRow[x] = lcd.Color_To_565(r, g, b);
    }

    lcd.Push_Any_Color(dstRow, bmpWidth, firstChunk, 0);
    firstChunk = false;
  }

  free(srcRow);
  free(dstRow);
  return true;
}

// Load and draw an image by numeric ID. Tries raw RGB565 formats first for speed, then
// falls back to a BMP file named `XXXX.BMP` (where XXXX is a zero-padded 4-digit number).
// Returns true on success, false on any failure.
static bool bmpDraw(LCDWIKI_SPI &lcd, int imgNum)
{
  if (!sdReady || imgNum < 1 || imgNum > 9999)
  {
    return false;
  }

  char filename[16];
  const char *const rawExtensions[] = { ".RAW565", ".RGB565", ".565", ".RAW", ".BIN" };
  for (uint8_t i = 0; i < sizeof(rawExtensions) / sizeof(rawExtensions[0]); i++)
  {
    sprintf(filename, "%04d%s", imgNum, rawExtensions[i]);
    File rawFile = SD.open(filename, FILE_READ);
    if (!rawFile)
    {
      continue;
    }

    bool ok = drawRaw565File(lcd, rawFile);
    rawFile.close();
    if (ok)
    {
      Serial.print(F("Raw image loaded: "));
      Serial.println(filename);
      return true;
    }
  }

  sprintf(filename, "%04d.BMP", imgNum);
  File bmpFile = SD.open(filename, FILE_READ);
  if (!bmpFile)
  {
    Serial.print(F("Open fail: "));
    Serial.println(filename);
    return false;
  }

  bool ok = drawBmpFile(lcd, bmpFile);
  bmpFile.close();
  if (ok)
  {
    Serial.print(F("BMP image loaded: "));
    Serial.println(filename);
  }
  return ok;
}

// Display a simple text fallback on the given `lcd` when image loading fails.
static void showFallbackText(LCDWIKI_SPI &lcd, int imgNum, const char *prompt)
{
  lcd.Set_Text_Size(2);
  lcd.Set_Text_Back_colour(BLACK);
  lcd.Fill_Screen(BLACK);
  char buf[32];
  sprintf(buf, "Image %d", imgNum);
  lcd.Print_String((uint8_t*)buf, 20, 80);
  lcd.Set_Text_Size(1);
  lcd.Print_String((uint8_t*)prompt, 20, 120);
}

// Record the currently displayed left/right image IDs and arm the touch-selection UI.
static void armSelection(int leftImg, int rightImg)
{
  selectedLeftImage = leftImg;
  selectedRightImage = rightImg;
  selectionPending = true;
}

// Emit a selection decision message over USB serial. This is used when a user touches the
// left or right touch surface to choose between the two displayed images.
static void sendSelectionDecision(const char *side)
{
  char msg[96];
  sprintf(msg, "DEC;FROM;PIC;SEL;%s;A;%u;B;%u", side, selectedLeftImage, selectedRightImage);
  Serial.println(msg);
  selectionPending = false;
}

static void drawFilledCircle(LCDWIKI_SPI &lcd, int16_t cx, int16_t cy, int16_t radius, uint16_t color)
{
  int16_t r2 = radius * radius;
  for (int16_t y = -radius; y <= radius; ++y) {
    for (int16_t x = -radius; x <= radius; ++x) {
      if ((x * x) + (y * y) <= r2) {
        lcd.Draw_Pixe(cx + x, cy + y, color);
      }
    }
  }
}

static void drawBloodSplatAt(LCDWIKI_SPI &lcd, int16_t cx, int16_t cy, uint8_t variant)
{
  int8_t dripX = 0;
  int8_t dripY = 1;
  if (variant == 1) {
    dripX = -1;
    dripY = 1;
  } else if (variant == 2) {
    dripX = 1;
    dripY = 0;
  } else if (variant == 3) {
    dripX = -1;
    dripY = 0;
  }

  int16_t leftSpike = (variant & 1) ? 36 : 42;
  int16_t rightSpike = (variant & 2) ? 34 : 28;
  int16_t upperSpike = (variant == 2) ? 18 : 26;
  int16_t lowerSpike = (variant == 3) ? 50 : 46;

  // Main splat body.
  drawFilledCircle(lcd, cx - 24, cy + 6, 22, BLOOD_DARK);
  drawFilledCircle(lcd, cx - 5, cy - 4, 28, BLOOD_MAIN);
  drawFilledCircle(lcd, cx + 22, cy + 10, 18, BLOOD_DARK);
  drawFilledCircle(lcd, cx + 4, cy + 26, 24, BLOOD_MAIN);
  drawFilledCircle(lcd, cx - 12, cy + 20, 12, BLOOD_BRIGHT);

  // Irregular splashes around the center.
  drawFilledCircle(lcd, cx - leftSpike, cy - 10, 7, BLOOD_MAIN);
  drawFilledCircle(lcd, cx - 34, cy + 30, 6, BLOOD_DARK);
  drawFilledCircle(lcd, cx - 12, cy - 28, 5, BLOOD_BRIGHT);
  drawFilledCircle(lcd, cx + rightSpike, cy - upperSpike, 8, BLOOD_MAIN);
  drawFilledCircle(lcd, cx + 42, cy + 18, 6, BLOOD_DARK);
  drawFilledCircle(lcd, cx + 14, cy + lowerSpike, 5, BLOOD_BRIGHT);

  // Drips downward.
  for (int16_t i = -10; i <= 10; ++i) {
    lcd.Draw_Pixe(cx + i, cy + 36, BLOOD_MAIN);
  }
  for (int16_t y = 0; y < 28; ++y) {
    lcd.Draw_Pixe(cx - 15 + (dripX * (y / 8)), cy + 38 + (dripY * y), BLOOD_DARK);
    if (y < 20) lcd.Draw_Pixe(cx + 16 - (dripX * (y / 10)), cy + 40 + y, BLOOD_DARK);
    if (y < 16) lcd.Draw_Pixe(cx + 2 + (dripX * 3), cy + 44 + y, BLOOD_BLACKISH);
  }
}

static void drawBloodOverlay(LCDWIKI_SPI &lcd)
{
  const int16_t w = lcd.Get_Display_Width();
  const int16_t h = lcd.Get_Display_Height();

  const int16_t marginX = 42;
  const int16_t marginY = 54;

  int16_t x1 = random(marginX, (w / 2) - marginX);
  int16_t y1 = random(marginY, (h / 2) - marginY);
  int16_t x2 = random((w / 2) + marginX, w - marginX);
  int16_t y2 = random(marginY, (h / 2) - marginY);
  int16_t x3 = random(marginX, (w / 2) - marginX);
  int16_t y3 = random((h / 2) + marginY, h - marginY);
  int16_t x4 = random((w / 2) + marginX, w - marginX);
  int16_t y4 = random((h / 2) + marginY, h - marginY);

  drawBloodSplatAt(lcd, x1, y1, (uint8_t)random(0, 4));
  drawBloodSplatAt(lcd, x2, y2, (uint8_t)random(0, 4));
  drawBloodSplatAt(lcd, x3, y3, (uint8_t)random(0, 4));
  drawBloodSplatAt(lcd, x4, y4, (uint8_t)random(0, 4));
}

// Poll both touch controllers when a selection is armed. Debounces with a short delay
// after a selection to avoid duplicate events.
static void pollTouchSelection()
{
  if (!selectionPending) {
    return;
  }

  left_touch.TP_Scan(0);
  if (left_touch.TP_Get_State() & TP_PRES_DOWN) {
    drawBloodOverlay(my_lcd1);
    sendSelectionDecision("LEFT");
    delay(150);
    return;
  }

  right_touch.TP_Scan(0);
  if (right_touch.TP_Get_State() & TP_PRES_DOWN) {
    drawBloodOverlay(my_lcd2);
    sendSelectionDecision("RIGHT");
    delay(150);
  }
}

// Forward a raw command string to the line robot over `Serial1` and start an ACK timeout.
static void sendLineCommand(const String &cmd)
{
  Serial1.print(cmd);
  Serial1.print("\r\n");
  lineAckPending = true;
  lineAckDeadline = millis() + LINE_ACK_TIMEOUT;
}

// Parse and handle commands received over USB Serial. Supported commands:
//  - TO;PIC;CMD;SHOW;A;B  -> display image A (left) and B (right)
//  - TO;LINE;CMD;...      -> forward to the line robot via Serial1
// The parser tolerates a leading "BT: " prefix which may appear when receiving bridged
// Bluetooth/serial lines.
static void handleUsbCommand(String cmd)
{
  cmd.trim();
  while (cmd.startsWith("BT: ")) {
    cmd.remove(0, 4);
  }
  cmd.trim();

  if (cmd.startsWith("TO;PIC;CMD;SHOW;")) {
    String args = cmd.substring(strlen("TO;PIC;CMD;SHOW;"));
    args.trim();
    int sep = args.indexOf(';');
    if (sep < 0) {
      Serial.println("ERR;FROM;PIC;BADFMT");
      return;
    }

    int a = args.substring(0, sep).toInt();
    int b = args.substring(sep + 1).toInt();

    if (a < 1 || b < 1) {
      Serial.println("ERR;FROM;PIC;RANGE");
      return;
    }

    // Check availability, then attempt to draw on each display. Show a text fallback if load fails.
    bool aOk = imageExists(a);
    bool bOk = imageExists(b);

    if (!bmpDraw(my_lcd1, a)) {
      showFallbackText(my_lcd1, a, "Load failed");
    }
    delay(20);
    if (!bmpDraw(my_lcd2, b)) {
      showFallbackText(my_lcd2, b, "Load failed");
    }

    armSelection(a, b);

    // Emit an ACK summarizing whether each file was found.
    char ack[80];
    sprintf(
      ack,
      "ACK;FROM;PIC;STATE;DONE;A;%d;%s;B;%d;%s",
      a,
      aOk ? "OK" : "MISS",
      b,
      bOk ? "OK" : "MISS"
    );
    Serial.println(ack);
    return;
  }

  if (cmd.startsWith("TO;LINE;CMD;")) {
    sendLineCommand(cmd);
    return;
  }

  Serial.println("ERR;FROM;PIC;UNKNOWN");
}

// Non-blocking serial reader for USB: collects characters until newline, then dispatches
// the accumulated line to `handleUsbCommand`.
static void processUsb()
{
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\r' || c == '\n') {
      if (!usbBuf.length()) {
        continue;
      }
      handleUsbCommand(usbBuf);
      usbBuf = "";
      continue;
    }
    usbBuf += c;
  }
}

// Handle a single line-oriented response received from the line robot (Serial1).
// Currently the handler prints the message and clears the pending ACK flag when an
// ACK is observed.
static void handleLineResponse(String msg)
{
  msg.trim();
  if (!msg.length()) {
    return;
  }
  Serial.println(msg);
  if (msg.startsWith("ACK")) {
    lineAckPending = false;
  }
}

// Non-blocking reader for `Serial1` (the line robot connection). Buffers incoming
// characters until a newline is received and then forwards the accumulated message
// to `handleLineResponse`. Also enforces an ACK timeout for commands forwarded
// with `sendLineCommand`.
static void processLineRobot()
{
  while (Serial1.available()) {
    char c = Serial1.read();
    if (c == '\r' || c == '\n') {
      if (!lineBuf.length()) {
        continue;
      }
      handleLineResponse(lineBuf);
      lineBuf = "";
      continue;
    }
    lineBuf += c;
  }

  if (lineAckPending && millis() > lineAckDeadline) {
    Serial.println("ERR;FROM;LINE;TIMEOUT");
    lineAckPending = false;
  }
}

void setup()
{
  Serial.begin(115200);
  Serial1.begin(38400);
  randomSeed((unsigned long)micros() ^ (unsigned long)analogRead(A15));

  pinMode(TFT1_CS, OUTPUT);
  pinMode(TFT2_CS, OUTPUT);
  pinMode(TFT1_DC, OUTPUT);
  pinMode(TFT1_RST, OUTPUT);
  pinMode(TFT2_DC, OUTPUT);
  pinMode(TFT2_RST, OUTPUT);
  pinMode(SD_CS_PIN, OUTPUT);
  pinMode(53, OUTPUT);
  pinMode(LEFT_TOUCH_CS, OUTPUT);
  pinMode(LEFT_TOUCH_IRQ, INPUT_PULLUP);
  pinMode(RIGHT_TOUCH_CS, OUTPUT);
  pinMode(RIGHT_TOUCH_IRQ, INPUT_PULLUP);

  digitalWrite(TFT1_CS, HIGH);
  digitalWrite(TFT2_CS, HIGH);
  digitalWrite(SD_CS_PIN, HIGH);
  digitalWrite(53, HIGH);
  digitalWrite(LEFT_TOUCH_CS, HIGH);
  digitalWrite(RIGHT_TOUCH_CS, HIGH);

  Serial.println(F("Init TFT1"));
  my_lcd1.Init_LCD();
  my_lcd1.Set_Rotation(0);
  my_lcd1.Fill_Screen(BLACK);

  delay(50);

  Serial.println(F("Init TFT2"));
  my_lcd2.Init_LCD();
  my_lcd2.Set_Rotation(0);
  my_lcd2.Fill_Screen(BLACK);

  left_touch.TP_Init(my_lcd1.Get_Rotation(), my_lcd1.Get_Display_Width(), my_lcd1.Get_Display_Height());
  right_touch.TP_Init(my_lcd2.Get_Rotation(), my_lcd2.Get_Display_Width(), my_lcd2.Get_Display_Height());

  my_lcd1.Set_Text_Mode(0);
  my_lcd1.Set_Text_Size(2);
  my_lcd1.Set_Text_colour(WHITE);
  my_lcd1.Print_String((uint8_t*)"Picture Robot", 20, 20);

  // Initialize SD card and report status on both Serial and the left display.
  sdReady = SD.begin(SD_CS_PIN);
  if (sdReady) {
    Serial.println(F("SD ready on D6"));
    my_lcd1.Set_Text_Size(1);
    my_lcd1.Print_String((uint8_t*)"SD OK", 20, 50);
  } else {
    Serial.println(F("SD init failed on D6"));
    my_lcd1.Set_Text_Size(1);
    my_lcd1.Set_Text_colour(RED);
    my_lcd1.Print_String((uint8_t*)"SD FAIL", 20, 50);
    my_lcd1.Set_Text_colour(WHITE);
  }
  // Report free SRAM so you can tune buffer sizes (Mega2560 has ~8 KiB SRAM)
  Serial.print(F("Free RAM: "));
  Serial.println(freeRam());
}

void loop()
{
  processUsb();
  processLineRobot();
  pollTouchSelection();
}
