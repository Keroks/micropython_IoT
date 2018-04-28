'''
Created on 24.03.2018

@author: Adam Skorek
'''
import esp
esp.osdebug(None)

from machine import Pin, I2C, Timer, ADC
import time
import network
import usocket as socket
import ParserAT
import mfrc522
from os import uname

led = Pin(2, Pin.OUT)
ssid = 'Niepokoj_Hotel'
password = 'N13p0k0j4c3'
wlan = network.WLAN(network.STA_IF)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = socket.getaddrinfo("192.168.1.40", 9999)[0][-1]

rotatedPrevious = False
rotated = False
skipOneRead = True

if uname()[0] == 'WiPy':
    rdr = mfrc522.MFRC522("GP14", "GP16", "GP15", "GP22", "GP17")
elif uname()[0] == 'esp8266':
    rdr = mfrc522.MFRC522(12, 15, 14, 0, 13)
else:
    raise RuntimeError("Unsupported platform")


def do_connect():
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('Network config:', wlan.ifconfig())


def check_connection(t):
    if not wlan.isconnected():
        print('Network disconnected! Will try to reconnect!')
        wlan.connect(ssid, password)
    else:
        print("Connected!")


def led_cmd(operand, params):
    if operand == "=":
        if params == "ON":
            led(0)
            return "LED ON"
        elif params == "OFF":
            led(1)
            return "LED OFF"
        else:
            return "WRONG PARAMS"
    else:
        return "WRONG OPERAND"


def read_card(t):
    (stat, tag_type) = rdr.request(rdr.REQIDL)

    global rotated
    global rotatedPrevious
    global skipOneRead

    if stat == rdr.OK:
        # print('REQIDL returned OK!')
        rotated = True
        skipOneRead = True
    else:
        # print('REQIDL returned {}!'.format(stat))
        if not skipOneRead:
            rotated = False
        skipOneRead = False

    if rotated != rotatedPrevious:
            if rotated:
                print('+ROT=1')
                sock.sendto(b"+ROT=1\r\n", addr)
            else:
                print('+ROT=0')
                sock.sendto(b"+ROT=0\r\n", addr)
            rotatedPrevious = rotated
    # else:
        # print('No change!')
        # (stat, raw_uid) = rdr.anticoll()
        #
        # if stat == rdr.OK:
        #
        #     print("New card detected")
        #     print("  - tag type: 0x%02x" % tag_type)
        #     print("  - uid	 : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
        #     print("")
        #
        #     if rdr.select_tag(raw_uid) == rdr.OK:
        #
        #         key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        #
        #         if rdr.auth(rdr.AUTHENT1A, 8, key, raw_uid) == rdr.OK:
        #             print("Address 8 data: %s" % rdr.read(8))
        #             rdr.stop_crypto1()
        #         else:
        #             print("Authentication error")
        #     else:
        #         print("Failed to select tag")


def main():
    led(1)
    do_connect()
    led(0)
    parser = ParserAT.ParserAT()
    parser.add_command("LED", led_cmd)
    # print("Will send to:", addr)
    sock.bind(("", 9999))
    sock.setblocking(False)

    timCon = Timer(-1)
    timCon.init(period=10000, mode=Timer.PERIODIC, callback=check_connection)
    timRfid = Timer(1)
    timRfid.init(period=100, mode=Timer.PERIODIC, callback=read_card)

    while True:
        # print("Working...")
        try:
            recv = sock.recv(100)
        except OSError:
            # print("No data at the moment!")
            pass
        else:
            # print("Received: ")
            # print(recv)
            response = parser.parse(recv.decode("utf-8"))
            if isinstance(response, tuple):
                for rspStr in response:
                    sock.sendto(rspStr.encode("utf-8"), addr)
            elif isinstance(response, str):
                sock.sendto(response.encode("utf-8"), addr)

        time.sleep(1)


if __name__ == '__main__':
    main()
