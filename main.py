'''
Created on 24.03.2018

@author: Adam Skorek
'''

from machine import Pin, I2C, Timer, ADC
import time
import network
import usocket as socket
import ParserAT

led = Pin(2, Pin.OUT)
ssid = 'TestSSID'
password = 'TestPassword'
wlan = network.WLAN(network.STA_IF)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = socket.getaddrinfo("192.168.1.40", 9999)[0][-1]
adc = ADC(0)


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


def read_battery(t):
    battery_nominal_voltage = 3.7
    current_voltage = (adc.read() * battery_nominal_voltage) / 1024
    print("Battery: {}V".format(current_voltage))
    sock.sendto("+BAT={}V\r\n".format(current_voltage).encode("utf-8"), addr)


def main():
    led(1)
    do_connect()
    led(0)
    parser = ParserAT.ParserAT()
    parser.add_command("LED", led_cmd)
    print("Will send to:", addr)
    sock.bind(("", 9999))
    sock.setblocking(False)

    timCon = Timer(-1)
    timCon.init(period=10000, mode=Timer.PERIODIC, callback=check_connection)
    timBat = Timer(1)
    timBat.init(period=5000, mode=Timer.PERIODIC, callback=read_battery)

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
