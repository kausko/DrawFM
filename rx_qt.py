import sys
import typing
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt, QTime, QTimer
from multiprocessing import shared_memory
from binascii import hexlify
from PyQt5.QtWidgets import QWidget
from comm_simulator import CommunicationSimulator
from utils import DEFAULT_BG_COLOR, DEFAULT_BRUSH_SIZE, DEFAULT_PEN_COLOR, my_memcpy, PACK_CODE, PACK_CODES, MSG_CODES, pack_draw
from bitstruct import *
from os import getenv
from dotenv import load_dotenv
load_dotenv()
sim = getenv("SIM") == "True"


if not sim:
    '''RASPBERRY PI: use below'''
    from si4703Library import si4703Radio
    '''RASPBERRY PI: use above'''

TICK = 40

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, shared_input_buffer_name: str, communications_simulator: CommunicationSimulator):
        super().__init__()

        self.shared_input_buffer_name = shared_input_buffer_name
        self.shared_memory = shared_memory.SharedMemory(name=self.shared_input_buffer_name)
        self.communications_simulator = communications_simulator

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(800, 600)
        canvas.fill(DEFAULT_BG_COLOR)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)

        self.last_x, self.last_y, self.last_rds, self.line_code = None, None, None, 0
        self.color = QtGui.QColor(DEFAULT_PEN_COLOR)
        self.brushSize = DEFAULT_BRUSH_SIZE

        if not sim:
            '''RASPBERRY PI: use below'''
            self.radio = si4703Radio(0x10, 5, 19)
            self.radio.si4703Init()
            self.radio.si4703SetChannel(int(getenv("FREQ")))
            self.radio.si4703SetVolume(5)
            
            print(str(self.radio.si4703GetChannel()))
            print(str(self.radio.si4703GetVolume()))
            '''RASPBERRY PI: use above'''

        self.time = QTime(0, 0, 0, 0)
        timer = QTimer(self)
        timer.timeout.connect(self.process_rds)
        timer.start(TICK)
    
    def process_rds(self):
        self.time = self.time.addMSecs(TICK)
        rds = None
        try:
            if not sim:
                '''RASPBERRY PI: use below'''
                # if the below function isn't implemented, you need to add it to the si4703 library
                # I've included the function commented out at the bottom of this file.
                # Just copy and paste it to the same file where the radio.si4703getRDS() function is
                rds = self.radio.si4703getRDSBytes()
                '''RASPBERRY PI: use above'''
            else:
                '''SIMULATOR: use below'''
                '''NOTE: you need to comment this out when running on hardware, as it overwrites the rds variable'''
                s2 = shared_memory.SharedMemory(name=self.shared_input_buffer_name)
                tx_buffer = s2.buf
                self.communications_simulator.set_buffer(tx_buffer)
                rds = self.communications_simulator.get_buffer()
                '''SIMULATOR: use above'''

            if rds == self.last_rds:
                return
            self.last_rds = rds

            msg, _ = unpack(PACK_CODE, rds[:4])
            
            if msg == MSG_CODES['draw']:
                _, x, y, draw_line, __ = unpack(PACK_CODES['draw'], rds)
                if self.last_x is None or self.last_y is None or draw_line != self.line_code:
                    self.last_x, self.last_y, self.line_code = x, y, draw_line
                    return
                
                canvas = self.label.pixmap()
                painter = QtGui.QPainter(canvas)
                pen = QtGui.QPen(self.color, self.brushSize)
                pen.setCapStyle(QtCore.Qt.RoundCap)
                painter.setPen(pen)
                painter.drawLine(self.last_x, self.last_y, x, y)
                painter.end()
                self.label.setPixmap(canvas)

                self.last_x, self.last_y = x, y

            elif msg == MSG_CODES['color']:
                _, r, g, b, a = unpack(PACK_CODES['color'], rds[:4])
                # very transparent colors were getting truncated to zero
                if a == 0:
                    a = 1
                self.color = QtGui.QColor(r, g, b, (a)*16)

            elif msg == MSG_CODES['size']:
                _, size, __ = unpack(PACK_CODES['size'], rds[:4])
                self.brushSize = size

            elif msg == MSG_CODES['clear']:
                pass
                # canvas = QtGui.QPixmap(800, 600)
                # canvas.fill(Qt.white)
                # self.label.setPixmap(canvas)

            print({
                'time': self.time.toString("hh:mm:ss.zzz"),
                'msg': msg,
                'last_x': self.last_x,
                'last_y': self.last_y,
                'line_code': self.line_code,
                'color': str(self.color.red()) + "," + str(self.color.green()) + "," + str(self.color.blue()) + "," + str(self.color.alpha()),
                'brushSize': self.brushSize
            })


        except Exception as e:
            print(e)
            print("RDS:", rds, "is not a valid coordinate pair")
            pass


def rx_qt_main_func(shared_input_buffer_name: str, communications_simulator: CommunicationSimulator):
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(shared_input_buffer_name, communications_simulator)
    window.show()
    app.exec_()

if __name__ == '__main__':
    s1 = shared_memory.SharedMemory(name='s1', create=True, size=6)
    pack_data = pack_draw(255, 255, 15)
    my_memcpy(s1, pack_data)
    communication_simulator = CommunicationSimulator(drop_rate=0.01, bitflip_rate=0.01)
    rx_qt_main_func(shared_input_buffer_name=s1.name, communications_simulator=communication_simulator)