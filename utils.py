import numpy as np

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