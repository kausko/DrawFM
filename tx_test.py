import sys
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt, QTime, QTimer
from multiprocessing import shared_memory
from binascii import hexlify
from utils import LOG_FOLDER, DEFAULT_BG_COLOR, DEFAULT_BRUSH_SIZE, DEFAULT_PEN_COLOR, my_memcpy, pack_draw, pack_color, pack_size, pack_clear
from bitstruct import *
import time
from datetime import datetime
import os
import json
import logging
from os import getenv
from dotenv import load_dotenv
import board
import digitalio
import adafruit_si4713

load_dotenv()
sim = getenv("SIM") == "True"
LOG_DATA = getenv("LOG_DATA") == "True"

DELAY = 50
logging.basicConfig(filename=f"{LOG_FOLDER}/tx_test_every_{DELAY}_ms_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log", level=logging.DEBUG)

FREQUENCY_KHZ = int(getenv("FREQ") + "00")
i2c = board.I2C()
si_reset = digitalio.DigitalInOut(board.D5)

si4713 = adafruit_si4713.SI4713(i2c, reset=si_reset, timeout_s=0.5)

noise = si4713.received_noise_level(FREQUENCY_KHZ)
logging.info("Noise: {0} dBuV".format(noise))

si4713.tx_frequency_khz = FREQUENCY_KHZ
# si4713.tx_power = 115

logging.info("Frequency: {0:0.3f} mhz".format(si4713.tx_frequency_khz / 1000.0))
logging.info("Transmitter power: {0} dBuV".format(si4713.tx_power))
logging.info(
    "Transmitter antenna capacitance: {0:0.2} pF".format(si4713.tx_antenna_capacitance)
)

si4713.gpio_control(gpio1=True, gpio2=True)

si4713.configure_rds(0xADAF, station=bytes('(1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (9,9), (10,10)', 'utf-8'), rds_buffer=bytes('(1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (9,9), (10,10)', 'utf-8'))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(800, 600)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)

        self.counter = 0

        self.time = QTime(0, 0, 0, 0)
        timer = QTimer(self)
        timer.timeout.connect(self.timerEvent)
        timer.start(DELAY)

    def timerEvent(self):
        si4713._set_rds_buffer(bytes(str(self.counter), 'utf-8'))
        logging.info({
            "datetime": str(datetime.now()),
            "counter": bytes(str(self.counter), 'utf-8')
        })
        self.counter += 1
        self.time = self.time.addMSecs(DELAY)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()