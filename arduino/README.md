FINAL_CLONE

Contents
- picture_master.ino  — Mega2560 master that displays images, accepts touch selection, forwards line commands via Serial1.
- line_robot.ino    — UNO line-follow robot sketch (expects config.h).
- config.h         — Pin mapping for the line robot (sensors + motor inversion).
- line_robot_README.md — Brief notes on wiring and commands.

Wiring (summary)
- Picture Master (Mega2560):
  - TFT1 (left): CS=D10, DC=D9, RST=D8
  - TFT2 (right): CS=A0, DC=A2, RST=D7
  - Shared SPI: MOSI=D51, MISO=D50, SCK=D52
  - SD Card: CS=D6 (MOSI=D11,MISO=D12,SCK=D13)
  - Touch: CLK=D22, DO=D23, DIN=D24; Left CS=D25 IRQ=D26; Right CS=D27 IRQ=D28
  - Line robot link: Serial1 (HC-05) (RX1=D19, TX1=D18)
  - HC-05:

- Line robot (UNO):
  - Motor pins: D4 (dir), D5 (PWM left), D7 (dir), D6 (PWM right)
  - Line sensors: pins 2,3,8,9,12 (see config.h)
  - HC-05 wiring: Currently testing with gravity pinout, otherwise TX->D10, RX->D11 (using voltage divider on RX)

Protocol (example messages)
- Master to Picture: `TO;PIC;CMD;SHOW;12;13` — ask picture unit to display images 12 (left) and 13 (right). Current images are 1 through 29 but will update with more/different ones later.
- Picture ACK: `ACK;FROM;PIC;STATE;DONE;A;12;OK;B;13;OK` — will confirm when images finish loading, approx ~60 seconds. Not required for continued operation of system, but good if you need to know. 
- Master to Line: `TO;LINE;CMD;LEFT` / `RIGHT` / `STOP` — instruct line robot.
- Line ACK: `ACK;FROM;LINE;STATE;DONE`
- Selection decision from picture master to PC: `DEC;FROM;PIC;SEL;LEFT;A;12;B;13`

How to run 
1. Flash the `line_robot.ino` to the UNO and `picture_master.ino` to the Mega2560.
2. Prepare SD card with images as 4-digit numbered files (e.g., `0012.BMP`, `0013.RGB565`). Will prefer rgb over bmp for speed.
3. Once powered, the Mega's HC-05 TX/RX to the UNO's HC-05 RX/TX will sync for Serial command forwarding.
4. On the PC, open a serial monitor at 115200 to see debug and selection messages from the Mega.

Line Tracker process

- What it does: 
    Follows a line using five reflectance sensors and basic PID-ish steering; accepts remote branch commands (LEFT/RIGHT/STOP) over HC‑05 and ACKs when the branch action completes.

- How it operates: 
    reads 5 sensors (pins in `config.h`) and computes a weighted error to steer using a simple proportional + derivative (and optional integral) correction. Motors are driven via paired direction/PWM pins (4/5 and 7/6). When it receives `TO;LINE;CMD;LEFT` or `TO;LINE;CMD;RIGHT` over SoftwareSerial (HC‑05), it sets a remote target and waits until a fork is detected (outer sensors both see the line). At the fork it biases steering toward the chosen side; once the center sensor (`sensorPins[2]`) reacquires the new line the robot clears the bias and resumes normal PID-based following for the remainder of the course. The robot continues to watch for the final stop marker (all sensors active) and will stop and send `ACK;FROM;LINE;STATE;DONE` when that full bar is detected. Smooth motor ramps use `rampToward`. Key parameters (sensor pins, weights, speeds, PID constants) live in `config.h` and at the top of the sketch.


Master picture/display controller process

- What it does: 
    Runs on an Arduino Mega to display two images (left/right) from an SD card onto two ILI9488 TFTs, accept remote commands over USB, and forward control to the line robot.

- How it operates: 
    listens on USB Serial for command strings like `TO;PIC;CMD;SHOW;A;B` to load image A on the left TFT and B on the right TFT (supports raw RGB565 and 24-bit BMP). It draws images using `bmpDraw`/`drawRaw565File`, arms a touch-based selection UI, and when a touch selection occurs it emits a decision message (selection) on USB. It forwards line-robot commands (`TO;LINE;CMD;...`) to `Serial1` (hardware UART) and waits for ACK/timeouts. Hardware pins and SD/TFT wiring are defined at the top of the file.

