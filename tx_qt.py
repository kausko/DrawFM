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
from os import getenv
from dotenv import load_dotenv
load_dotenv()
sim = getenv("SIM") == "True"
LOG_DATA = getenv("LOG_DATA") == "True"

if not sim:
    '''RASPBERRY PI: use below'''
    import board
    import digitalio
    import adafruit_si4713

    FREQUENCY_KHZ = int(getenv("FREQ") + "00")
    i2c = board.I2C()
    si_reset = digitalio.DigitalInOut(board.D5)

    print("initializing si4713 instance")
    si4713 = adafruit_si4713.SI4713(i2c, reset=si_reset, timeout_s=0.5)
    print("done")

    noise = si4713.received_noise_level(FREQUENCY_KHZ)
    print("Noise at {0:0.3f} mhz: {1} dBuV".format(FREQUENCY_KHZ / 1000.0, noise))

    si4713.tx_frequency_khz = FREQUENCY_KHZ
    si4713.tx_power = 115

    print("Transmitting at {0:0.3f} mhz".format(si4713.tx_frequency_khz / 1000.0))
    print("Transmitter power: {0} dBuV".format(si4713.tx_power))
    print(
        "Transmitter antenna capacitance: {0:0.2} pF".format(si4713.tx_antenna_capacitance)
    )

    si4713.gpio_control(gpio1=True, gpio2=True)
    print("Broadcasting...")

    si4713.configure_rds(0xADAF, station=bytes('(1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (9,9), (10,10)', 'utf-8'), rds_buffer=bytes('(1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (9,9), (10,10)', 'utf-8'))
    '''RASPBERRY PI: use above'''

DELAY = 50

class SliderProxyStyle(QtWidgets.QProxyStyle):
    def pixelMetric(self, metric, option, widget):
        if metric == QtWidgets.QStyle.PM_SliderThickness:
            return 40
        elif metric == QtWidgets.QStyle.PM_SliderLength:
            return 40
        return super().pixelMetric(metric, option, widget)

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, shared_input_buffer_name: str):
        super().__init__()

        self.shared_input_buffer_name = shared_input_buffer_name
        self.shared_memory = None
        if self.shared_input_buffer_name is not None:
            self.shared_memory = shared_memory.SharedMemory(name=self.shared_input_buffer_name)

        self.log_filename = None
        self.log_file = None

        if LOG_DATA:
            self.log_filename = os.path.join(LOG_FOLDER, str(datetime.now()) + '-tx.log')
            self.log_file = open(self.log_filename, 'w+')

        menubar = self.addToolBar("toolbar")
        font = self.font()
        font.setPointSize(16)
        menubar.setFont(font)
        menubar.addAction("Clear").triggered.connect(self.clearEvent)
        menubar.addAction("Color").triggered.connect(self.colorChangeEvent)

        self.brushSize = DEFAULT_BRUSH_SIZE

        self.mySlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.mySlider.setRange(1, 100)
        self.mySlider.setStyle(SliderProxyStyle(self.mySlider.style()))
        self.mySlider.sliderReleased.connect(self.brushSizeChangeEvent)

        menubar = self.addToolBar("toolbar")
        menubar.addWidget(self.mySlider)

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(800, 600)
        canvas.fill(DEFAULT_BG_COLOR)
        self.label.setPixmap(canvas)
        self.label.mouseMoveEvent = self._mouseMoveEvent
        self.label.mouseReleaseEvent = self._mouseReleaseEvent
        self.setCentralWidget(self.label)

        self.last_x, self.last_y, self.line_code = None, None, 0
        self.color = QtGui.QColor(DEFAULT_PEN_COLOR)
        self.coords = []

        # send initial color message
        self.coords.append(self._getColorMessage())

        self.time = QTime(0, 0, 0, 0)
        timer = QTimer(self)
        timer.timeout.connect(self.send_coords)
        timer.start(DELAY)
    
    def _getColorMessage(self):
        (r, g, b, a) = self.color.getRgb()
        a = a // 16
        print('COLOR', r, g, b, a)
        return pack_color(r, g, b, a)

    def _mouseMoveEvent(self, e):
        x = int(e.localPos().x())
        y = int(e.localPos().y())

        if self.last_x is None: # First event.
            self.last_x = x
            self.last_y = y
            # self.last_draw_time = time.time()

            self.coords.append(pack_draw(x, y, self.line_code))
            return # Ignore the first time.

        # if (x - self.last_x)**2 + (y - self.last_y)**2 > 200 or time.time() - self.last_draw_time > 0.3:

        canvas = self.label.pixmap()
        painter = QtGui.QPainter(canvas)
        pen = QtGui.QPen(self.color, self.brushSize)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        painter.drawLine(self.last_x, self.last_y, x, y)
        painter.end()
        self.label.setPixmap(canvas)

        # Update the origin for next time.
        self.last_x = x
        self.last_y = y
        # self.last_draw_time = time.time()

        self.coords.append(pack_draw(x, y, self.line_code))

    def _mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None
        self.line_code = 0 if self.line_code == 15 else 15
    
    def colorChangeEvent(self):
        self.color = QtWidgets.QColorDialog.getColor(options=QtWidgets.QColorDialog.ShowAlphaChannel)
        self.coords.append(self._getColorMessage())
    
    def brushSizeChangeEvent(self):
        sliderPosition = self.mySlider.sliderPosition()
        self.brushSize = sliderPosition
        entry = pack_size(self.brushSize)
        for i in range(3):
            self.coords.append(entry)

    def clearEvent(self):
        canvas = self.label.pixmap()
        canvas.fill(Qt.white)
        self.label.setPixmap(canvas)
        clear_msg = pack_clear()
        for i in range(3):
            self.coords.append(clear_msg)

    def send_coords(self):
        self.time = self.time.addMSecs(DELAY)
        if (not len(self.coords)):
            return
        coords = self.coords.pop(0)

        '''PI: use below'''
        if not sim:
            si4713._set_rds_buffer(coords)
        '''PI: use above'''

        '''SIMULATOR: use below'''
        if sim:
            my_memcpy(self.shared_memory, coords)
        '''SIMULATOR: use above'''

        print_dictionary = {
            'time': self.time.toString("hh:mm:ss.zzz"),
            'datetime': str(datetime.now()),
            'binary': str(hexlify(coords)),
            # 'msg': msg,
            'last_x': self.last_x,
            'last_y': self.last_y,
            'line_code': self.line_code,
            'color': str(self.color.red()) + "," + str(self.color.green()) + "," + str(self.color.blue()) + "," + str(self.color.alpha()),
            'brushSize': self.brushSize
        }

        # logging
        if LOG_DATA:
            self.log_file.write(json.dumps(print_dictionary) + ',\n')
        
        print(print_dictionary)

def tx_qt_main_func(shared_input_buffer_name: str):
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(shared_input_buffer_name)
    window.show()
    app.exec()

if __name__ == '__main__':
    shared_memory_name = None
    if sim:
        s1 = shared_memory.SharedMemory(name='s1', create=True, size=6)
        pack_data = pack_draw(255, 255, 15)
        my_memcpy(s1, pack_data)
        print(s1.buf)
        shared_memory_name = s1.name
        # main function
    tx_qt_main_func(shared_memory_name)