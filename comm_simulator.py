import numpy as np
from utils import bytes_to_ndarray_bool, ndarray_bool_to_bytes

class CommunicationSimulator():
    

    def __init__(self, drop_rate: float, bitflip_rate: float):
        self.in_buffer = ''.encode('utf-8')
        self.out_buffer = ''.encode('utf-8')
        self.drop_rate = drop_rate
        self.bitflip_rate = bitflip_rate
    

    def set_buffer(self, new_buffer: bytes):
        self.in_buffer = new_buffer

    def get_buffer(self):
        # convert bytes to ndarray of 1 and 0 (True and False)

        # print('self.in_buffer:', self.in_buffer)

        ndarray_bool = bytes_to_ndarray_bool(self.in_buffer)
        # print(ndarray_bool)

        bitmask = np.random.choice([True, False], size=len(ndarray_bool), p=[self.bitflip_rate, 1 - self.bitflip_rate])

        # xor to bitflip
        ndarray_bool = ndarray_bool ^ bitmask
        # print(ndarray_bool)

        # drop entire bytes
        msg_bytes = ndarray_bool_to_bytes(ndarray_bool)
        # print('msg_bytes', msg_bytes)

        new_msg = bytearray()
        for byte in msg_bytes:
            if np.random.random() > self.drop_rate:
                new_msg.append(byte)

        # convert back to bytes
        self.out_buffer = bytes(new_msg)
        return self.out_buffer