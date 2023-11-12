import numpy as np

# https://stackoverflow.com/a/32676625
def bitstring_to_bytes(s):
    # print('s:', s)
    v = int(s, 2)
    b = bytearray()
    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytes(b[::-1])

def ndarray_bool_to_bytes(ndarray_bool: np.ndarray):

    ndarray_bytes = ndarray_bool.tobytes()
    new_bytes_str = ''

    for byte in ndarray_bytes:
        if byte:
            new_bytes_str += '1'
        else:
            new_bytes_str += '0'

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