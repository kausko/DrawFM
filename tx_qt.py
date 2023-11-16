import sys
import board
import digitalio
import adafruit_si4713

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTime, QTimer
from struct import *

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

DELAY = 300
PACK_CODE = '>hhBB'

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        menubar = self.menuBar()
        font = self.font()
        font.setPointSize(16)
        menubar.setFont(font)
        menubar.addAction("Clear").triggered.connect(self.clearEvent)
        menubar.addAction("Color").triggered.connect(self.colorChangeEvent)

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(800, 600)
        canvas.fill(Qt.white)
        self.label.setPixmap(canvas)
        self.label.mouseMoveEvent = self._mouseMoveEvent
        self.label.mouseReleaseEvent = self._mouseReleaseEvent
        self.setCentralWidget(self.label)

        self.last_x, self.last_y, self.line_code = None, None, 0
        self.color = Qt.black
        self.coords = []

        self.time = QTime(0, 0, 0, 0)
        timer = QTimer(self)
        timer.timeout.connect(self.send_coords)
        timer.start(DELAY)

    def _mouseMoveEvent(self, e):
        x = int(e.localPos().x())
        y = int(e.localPos().y())

        if self.last_x is None: # First event.
            self.last_x = x
            self.last_y = y

            # self.coords.append(bytes(f"{x} {y} p", 'utf-8'))
            self.coords.append(pack(PACK_CODE, x, y, self.line_code, 0))
            return # Ignore the first time.

        canvas = self.label.pixmap()
        painter = QtGui.QPainter(canvas)
        painter.setPen(QtGui.QPen(self.color))
        painter.drawLine(self.last_x, self.last_y, x, y)
        painter.end()
        self.label.setPixmap(canvas)

        # Update the origin for next time.
        self.last_x = x
        self.last_y = y

        # self.coords.append(bytes(f"{x} {y} d", 'utf-8'))
        self.coords.append(pack(PACK_CODE, x, y, self.line_code, 0))

    def _mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None
        self.line_code = 0 if self.line_code == 255 else 255
    
    def colorChangeEvent(self):
        self.color = QtWidgets.QColorDialog.getColor()

    def clearEvent(self):
        canvas = self.label.pixmap()
        canvas.fill(Qt.white)
        self.label.setPixmap(canvas)
        # self.coords.append(bytes("clear", 'utf-8'))
        self.coords.append(pack(PACK_CODE, 0, 0, self.line_code, 255))

    def send_coords(self):
        self.time = self.time.addMSecs(DELAY)
        if (not len(self.coords)):
            return
        coords = self.coords.pop(0)
        print(self.time.toString(), unpack(PACK_CODE, coords))
        si4713._set_rds_buffer(coords)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()