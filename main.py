'''
Created on 24.03.2018

@author: Adam Skorek
'''

import micropython
micropython.alloc_emergency_exception_buf(100)

from machine import Pin, I2C, Timer, ADC
from mpu6050 import MPU
import time
import network
import usocket as socket
import ParserAT
import CommandsAT
import ujson

ssid = 'TestSSID'
password = 'TestPassword'
wlan = network.WLAN(network.STA_IF)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = socket.getaddrinfo("192.168.1.40", 9999)[0][-1]

# mpu6050 pints: SCL - D6 (GPIO12) / SDA - D7 (GPIO13)
i2c = I2C(scl=Pin(12), sda=Pin(13))
accelerometer = MPU(i2c, 2)
triggers = [0] * 2
rotated_prev = rotated = False


def do_connect():
    wlan.active(True)
    if not wlan.isconnected():
        # print('Connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    # print('Network config:', wlan.ifconfig())


def check_connection(t):
    if not wlan.isconnected():
        # print('Network disconnected! Will try to reconnect!')
        wlan.connect(ssid, password)
    # else:
        # print("Connected!")


def check_rotation(t):
    if not accelerometer.initialized:
        return
    try:
        position = accelerometer.read_position()
    except OSError:
        sock.sendto('+ERROR_ACCELEROMETER\r\n'.encode('UTF-8'), addr)
        return
    roll = position[1][0]
    pitch = position[1][1]
    yaw = position[1][2]
    # print("Rotation angles: {}, {}, {}".format(roll, pitch, yaw))
    # print("Triggers: {}, {}".format(triggers[0], triggers[1]))
    global rotated
    global rotated_prev
    if triggers[0] <= roll <= triggers[1] and -10 < pitch < 10:
        rotated = True
    else:
        rotated = False

    if rotated != rotated_prev:
        sock.sendto('+ROT={}\r\n'.format(int(rotated)).encode('UTF-8'), addr)

    rotated_prev = rotated


def main():
    do_connect()
    parser = ParserAT.ParserAT()
    global triggers
    parser.add_command("ACC", CommandsAT.cmd_AT_accel(accelerometer, triggers))
    parser.add_command("RESET", CommandsAT.cmd_AT_reset())
    sock.bind(("", 9999))
    sock.setblocking(False)

    try:
        with open('triggers.json', 'r') as file:
            record = file.read()
            triggers = ujson.loads(record)
            # print("Loaded triggers: ", triggers)
    except OSError:
        print('Cannot open triggers.json file!')

    tim_con = Timer(-1)
    tim_con.init(period=10000, mode=Timer.PERIODIC, callback=check_connection)

    tim_accel = Timer(1)
    tim_accel.init(period=250, mode=Timer.PERIODIC, callback=check_rotation)

    while True:
        # print("Working...")
        if not accelerometer.initialized:
            try:
                accelerometer.init_device()
            except OSError:
                # print("Cannot initialize accelerometer!")
                pass

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

        time.sleep_ms(100)


if __name__ == '__main__':
    main()
