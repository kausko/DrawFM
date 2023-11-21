import numpy as np
from bitstruct import pack
from PyQt5.QtCore import Qt

# memcpy
def my_memcpy(shared_memory, data):
    for index, byte in enumerate(data):
        # print(shared_memory.buf, index, byte)
        shared_memory.buf[index] = byte

def bitstring_to_bytes(s):
    int_list = []
    for i in range(0, len(s), 8):
        int_list.append(int(s[i:i+8], 2))
    return bytearray(int_list)

def ndarray_bool_to_bytes(ndarray_bool: np.ndarray):

    ndarray_bytes = ndarray_bool.tobytes()
    new_bytes_str = ''

    for byte in ndarray_bytes:
        if byte:
            new_bytes_str += '1'
        else:
            new_bytes_str += '0'

    # print(new_bytes_str)
    return bitstring_to_bytes(new_bytes_str)

def bytes_to_ndarray_bool(msg: bytes):

    # print(bytearray(msg))
    # bit_string = ['{0:08b}'.format(x, 'b') for x in msg]
    bit_list = bytearray()
    for m in msg:
        bits = bytes('{0:08b}'.format(m, 'b'), 'utf-8')
        bits_arr = bytearray(bits)
        # print(bits, bits_arr)
        bit_list += bits_arr
    # print(bit_list)
    # print(bytes(bit_list))

    np_arr = np.array(bit_list, dtype=int)
    np_arr = np_arr - 48  # subtracting code for zero (48). 1 is 49, so this works on my machine...
    # print(np_arr)
    np_bits = np.array(np_arr, dtype=bool)
    # print(np_bits)

    return np_bits


PACK_CODE = 'u4u28'

PACK_CODES = {
    'draw': 'u4u10u10u4u4', # msg_type, x, y, draw_line, unused
    'color': 'u4u8u8u8u4', # msg_type, r, g, b, a
    'size': 'u4u10u18', # msg_type, size (0-1023), unused
    'clear': 'u4u28' # msg_type, unused
}

MSG_CODES = {
    'draw': 0,
    'color': 15,
    'size': 3,
    'clear': 9
}

def pack_draw(x: int, y: int, draw_line: int):
    return pack(PACK_CODES['draw'], MSG_CODES['draw'], x, y, draw_line, 0)

def pack_color(r: int, g: int, b: int, a: int):
    return pack(PACK_CODES['color'], MSG_CODES['color'], r, g, b, a)

def pack_size(size: int):
    return pack(PACK_CODES['size'], MSG_CODES['size'], size, 0)

def pack_clear():
    return pack(PACK_CODES['clear'], MSG_CODES['clear'], 0)

# reference: https://doc.qt.io/qt-6/qt.html
DEFAULT_BG_COLOR = Qt.white
DEFAULT_PEN_COLOR = Qt.black
DEFAULT_BRUSH_SIZE = 3
DEFAULT_BRUSH_STYLE = Qt.SolidPattern
DEFAULT_PEN_STYLE = Qt.SolidLine
DEFAULT_PEN_CAP_STYLE = Qt.RoundCap
DEFAULT_PEN_JOIN_STYLE = Qt.RoundJoin