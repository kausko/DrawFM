import multiprocessing
from multiprocessing import shared_memory
from sim_rx_drawing import rx_drawing
from sim_tx_drawing import tx_drawing
from comm_simulator import CommunicationSimulator
from time import sleep

if __name__ == "__main__":

    # initialize shared memory list
    s1 = shared_memory.ShareableList(["large buffer for our strings".encode('utf-8')])

    # sh_output_buffer = shared_memory.SharedMemory(create=True, size=10)

    # input_buffer_value = Value(ctypes.c_wchar_p, lock=False)
    # input_buffer_value.value = "102 102"


    communication_simulator = CommunicationSimulator(drop_rate=0.005, bitflip_rate=0.001)
    # communication_simulator = CommunicationSimulator(drop_rate=0.00, bitflip_rate=0.00)
    communication_simulator.set_buffer("101 101".encode('utf-8'))


    print('Shared memory s1 name:', s1.shm.name)

    p2 = multiprocessing.Process(target=tx_drawing, args=(s1.shm.name,))
    p2.start()

    p1 = multiprocessing.Process(target=rx_drawing, args=(s1.shm.name, communication_simulator,))
    p1.start()