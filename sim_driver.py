import multiprocessing
from multiprocessing import shared_memory
from rx_qt import rx_qt_main_func
# from sim_tx_drawing import tx_drawing
from tx_qt import tx_qt_main_func
from comm_simulator import CommunicationSimulator
from time import sleep
from struct import pack
from utils import my_memcpy

PACK_CODE = ">hhBB"

if __name__ == "__main__":

    # initialize shared memory
    # NOTE: the size is the number of bytes
    # if we ever increase/decrease the number of bytes, we need to change this here & in the if __name__ == "main" functions
    s1 = shared_memory.SharedMemory(name='s1', create=True, size=6)
    
    # s1.buf = pack(PACK_CODE, 255, 255, 255, 255)
    pack_data = pack(PACK_CODE, 255, 255, 255, 255)
    my_memcpy(s1, pack_data)
    print(s1.buf)

    # sh_output_buffer = shared_memory.SharedMemory(create=True, size=10)

    # input_buffer_value = Value(ctypes.c_wchar_p, lock=False)
    # input_buffer_value.value = "102 102"


    # communication_simulator = CommunicationSimulator(drop_rate=0.005, bitflip_rate=0.001)
    # communication_simulator = CommunicationSimulator(drop_rate=0.1, bitflip_rate=0.1)
    communication_simulator = CommunicationSimulator(drop_rate=0.0, bitflip_rate=0.0)
    # communication_simulator.set_buffer("101 101".encode('utf-8'))


    print('Shared memory s1 name:', s1)

    p2 = multiprocessing.Process(target=tx_qt_main_func, args=(s1.name,))
    p2.start()

    p1 = multiprocessing.Process(target=rx_qt_main_func, args=(s1.name, communication_simulator,))
    p1.start()