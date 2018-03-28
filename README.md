# micropython_IoT
Simple tests of micropython on ESP8266 (using Wemos D1 mini Pro board).

Requirements:
- https://micropython.org/download micropython firmware flashed to device (esptool required)
- Adafruit ampy tool for uploading scripts (https://github.com/adafruit/ampy)

Flashing firmware step-by-step:
1. Erase flash with cmd:
      esptool --port COM4 erase_flash
2. Flashing for flash size up to 16MB:
      esptool --port COM4 --baud 460800 write_flash --flash_size=detect 0 esp8266-20171101-v1.9.3.bin
   Flashing for flash size 32MB (for example Wemos D1 mini Pro):
      esptool --port COM4 --baud 460800 write_flash -fm dio -fs 32m 0 esp8266-20171101-v1.9.3.bin

Uploading files and working with console:
1. Uploading:
    sudo ampy --port /dev/ttyUSB0 put main.py   // on linux
    ampy --port COM4 -b115200 put main.py       // on windows
2. Starting console (picocom on linux or putty on windows):
    sudo picocom /dev/ttyUSB0 -b115200
    putty -serial COM4 -sercfg 115200


