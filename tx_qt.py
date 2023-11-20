import sys
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt, QTime, QTimer
# from struct import *
from multiprocessing import shared_memory
from binascii import hexlify
from utils import my_memcpy
from bitstruct import *
import time

sim = True

if not sim:
    '''RASPBERRY PI: use below'''
    import board
    import digitalio
    import adafruit_si4713

    FREQUENCY_KHZ = 87700
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

DELAY = 300
# PACK_CODE = '>hhBB'
PACK_CODE = 'u10u10u6u6'

PACK_CODES = {
    'draw': 'u10u10u4u4u4',
    'color': 'u8u8u8u4u4',
    'size': 'u10u18u4'
}

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, shared_input_buffer_name: str):
        super().__init__()

        self.shared_input_buffer_name = shared_input_buffer_name
        self.shared_memory = shared_memory.SharedMemory(name=self.shared_input_buffer_name)

        menubar = self.addToolBar("toolbar")
        # menubar = self.menuBar()
        font = self.font()
        font.setPointSize(16)
        menubar.setFont(font)
        menubar.addAction("Clear").triggered.connect(self.clearEvent)
        menubar.addAction("Color").triggered.connect(self.colorChangeEvent)

        self.brushSize = 3

        self.mySlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.mySlider.setRange(1, 1023)
        self.mySlider.sliderReleased.connect(self.brushSizeChangeEvent)

        menubar = self.addToolBar("toolbar")
        menubar.addWidget(self.mySlider)
        # menubar.addAction("Brush Size").triggered.connect(self.brushSizeChangeEvent)

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(800, 600)
        canvas.fill(Qt.white)
        self.label.setPixmap(canvas)
        self.label.mouseMoveEvent = self._mouseMoveEvent
        self.label.mouseReleaseEvent = self._mouseReleaseEvent
        self.setCentralWidget(self.label)

        self.last_x, self.last_y, self.line_code = None, None, 0
        self.color = Qt.black
        self.color = QtWidgets.QColorDialog.getColor()
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
        return pack(PACK_CODES['color'], r, g, b, a, 15)

    def _mouseMoveEvent(self, e):
        x = int(e.localPos().x())
        y = int(e.localPos().y())

        if self.last_x is None: # First event.
            self.last_x = x
            self.last_y = y
            self.last_draw_time = time.time()

            self.coords.append(pack(PACK_CODES['draw'], x, y, self.line_code, 0, 0))
            return # Ignore the first time.

        if (x - self.last_x)**2 + (y - self.last_y)**2 > 100 or time.time() - self.last_draw_time > 0.1:

            canvas = self.label.pixmap()
            painter = QtGui.QPainter(canvas)
            painter.setPen(QtGui.QPen(self.color, self.brushSize))
            painter.drawLine(self.last_x, self.last_y, x, y)
            painter.end()
            self.label.setPixmap(canvas)

            # Update the origin for next time.
            self.last_x = x
            self.last_y = y
            self.last_draw_time = time.time()

            self.coords.append(pack(PACK_CODES['draw'], x, y, self.line_code, 0, 0))

    def _mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None
        self.line_code = 0 if self.line_code == 15 else 15
    
    def colorChangeEvent(self):
        self.color = QtWidgets.QColorDialog.getColor()
        self.coords.append(self._getColorMessage())
    
    def brushSizeChangeEvent(self):
        sliderPosition = self.mySlider.sliderPosition()
        self.brushSize = sliderPosition
        
        entry = pack(PACK_CODES['size'], self.brushSize, 0, 3)
        self.coords.append(entry)

    def clearEvent(self):
        canvas = self.label.pixmap()
        canvas.fill(Qt.white)
        self.label.setPixmap(canvas)
        # self.coords.append(bytes("clear", 'utf-8'))
        self.coords.append(pack(PACK_CODES['draw'], 0, 0, self.line_code, 15, 0))

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
        # it should be OK to leave this uncommented, even on Pi
        my_memcpy(self.shared_memory, coords)
        '''SIMULATOR: use above'''
        
        print(self.time.toString(), 's2', hexlify(coords))

def tx_qt_main_func(shared_input_buffer_name: str):
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(shared_input_buffer_name)
    window.show()
    app.exec()

if __name__ == '__main__':
    # it should be OK to leave this uncommented, even on Pi
    s1 = shared_memory.SharedMemory(name='s1', create=True, size=6)
    pack_data = pack(PACK_CODES['draw'], 255, 255, 15, 15, 0, 0)
    my_memcpy(s1, pack_data)
    print(s1.buf)
    # main function
    tx_qt_main_func(s1.name)