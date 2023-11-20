import pygame
import random
from comm_simulator import CommunicationSimulator
from multiprocessing import shared_memory
from time import sleep
from struct import *
from binascii import hexlify
import time
from utils import my_memcpy

'''uncomment if on pi'''
# from si4703Library import si4703Radio

def rx_drawing(shared_input_buffer_name: str, communications_simulator: CommunicationSimulator):

    # IF USING HARDWARE, USE THIS
    # radio = si4703Radio(0x10, 5, 19)
    # radio.si4703Init()
    # radio.si4703SetChannel(877)
    # radio.si4703SetVolume(5)
    # print(str(radio.si4703GetChannel()))
    # print(str(radio.si4703GetVolume()))

    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    screen.fill((0, 0, 0))
    clock = pygame.time.Clock()

    # mock setup
    mock = False
    coords = []
    if mock:
        coords = [[random.randint(0, 1280), random.randint(0, 720)]]
    def mock_draw():
        # draw pixel at coords
        screen.set_at(coords, (255, 255, 255))
        # update coords
        coords[0][0] += random.randint(-1, 1)
        coords[0][1] += random.randint(-1, 1)



    running = True
    try:
        last_rds = None
        last_data_line = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            if mock:
                mock_draw()
            else:
                # try:
                # rds = "100 100"



                # IF USING HARDWARE, USE THIS
                # rds = radio.si4703getRDSBytes()

                # rds is a stringified tuple (x, y), destructure it
                # stripped = rds[1:-1].split(", ")
                
                try:
                    # rds = radio.si4703getRDS()

                    '''for binary data (struct packing)'''
                    # rds = radio.si4703getRDSBytes()

                    # IF SIMULATOR MODE, USE THIS
                    # rds = str(communications_simulator.in_buffer.decode())
                    s2 = shared_memory.SharedMemory(name=shared_input_buffer_name)
                    tx_buffer = s2.buf
                    communications_simulator.set_buffer(tx_buffer)
                    rds = communications_simulator.get_buffer()


                    # print('rds:', hexlify(rds))
                    # rds = rds.decode()

                    x = 0
                    y = 0
                    data_line = 0
                    data_clean = 0

                    # invalid = 1
                    invalid = 0

                    # print(rds)
                    # print(bytes(rds, 'utf-8'))
                    # have to select first number of bytes we want, becuse rds reader will give us extra zero bytes at end because
                    (x, y, data_line, data_clean) = unpack('>hhBB', rds[:6])

                    # print(x, y, data_line, data_clean, time.time())

                    # x += 128

                    # stripped = rds.rstrip("\x00").split(" ")
                   
                    
                    # if len(stripped) == 1:
                    #     if stripped[0] == "clear":
                    #         data_clean = 1
                    #         # clear canvas or something
                    #         screen.fill((0, 0, 0))
                    #         coords = []
                    # else:
                    #     x, y = int(stripped[0]), int(stripped[1])
                    #     coords.append([x, y])

                    # if len(stripped) == 3:
                    #     if stripped[2] == 'd':
                    #         data_line = 1
                    #         invalid = 0
                    #     elif stripped[2] == 'p':
                    #         invalid = 0
                    
                    

                    if rds != last_rds:
                        print(x, y, data_line, data_clean, time.time())
                        coords.append([x, y])
                        print('coords len:', len(coords))
                        
                        
                        if data_clean == 255:
                            # clear canvas or something
                            screen.fill((0, 0, 0))
                            coords = []
                        elif True:
                            # print(coords)
                            if data_line == 255 or data_line == 0:
                                print('data_line', data_line, 'last_data_line', last_data_line)
                                if data_line != last_data_line:
                                    # pygame.draw.lines(screen, (255, 255, 255), False, coords[:-1])
                                    coords = [coords[-1]]
                                    
                                else:
                                    pygame.draw.lines(screen, (255, 255, 255), False, [coords[-1], coords[-2]])
                                    print(len(coords))
                                # pygame.draw.lines(screen, (255, 255, 255), False, coords[:-2])
                                
                                last_data_line = data_line
                                print('data_line2', data_line, 'last_data_line2', last_data_line)
                                # coords = coords[-1]
                            # else:
                                # pygame.draw.ellipse(screen, (255, 255, 255), pygame.Rect(x, y, 4, 4), 2)
                                
                            #     # coords.pop(0)
                            #     coords = [[x, y]]
                    
                    last_rds = rds

                except Exception as e:
                    print(e)
                    print("RDS:", rds, "is not a valid coordinate pair")
                    pass
                # except Exception as e:
                #     print(e)

            pygame.display.flip()
            clock.tick(60)
            # sleep(0.1)
                
    except KeyboardInterrupt:
        print("Exiting program")


    print("Shutting down pygame")
    pygame.quit()

if __name__ == "__main__":
    PACK_CODE = '>hhBB'

    s1 = shared_memory.SharedMemory(name='s1', create=True, size=6)
    pack_data = pack(PACK_CODE, 255, 255, 255, 0)
    my_memcpy(s1, pack_data)
    communication_simulator = CommunicationSimulator(drop_rate=0.01, bitflip_rate=0.01)
    rx_drawing(shared_input_buffer_name=s1.name, communications_simulator=communication_simulator)

    '''this is for the library function'''
    # def si4703getRDSBytes(self):        
    #     z = "000000000000000"
    #     msg = {}
    #     mi = 0
    #     h2 = ""
    #     h3 = ""
    #     h4 = ""
    #     wc = 0
    #     RDSB = self.SI4703_RDSB
    #     RDSC = self.SI4703_RDSC
    #     RDSD = self.SI4703_RDSD
    #     reset = False
    #     while 1:
    #         if reset:
    #             msg = {}
    #             mi = 0
    #             h2 = ""
    #             h3 = ""
    #             h4 = ""
    #             wc = 0
    #             reset = False

    #         self.si4703ReadRegisters()
    #         reg = self.si4703_registers
    #         if reg[self.SI4703_STATUSRSSI] & (1 << 15):
    #             r2 = z[:16 - len(bin(reg[RDSB])[2:])] + bin(reg[RDSB])[2:]
    #             r3 = z[:16 - len(bin(reg[RDSC])[2:])] + bin(reg[RDSC])[2:]
    #             r4 = z[:16 - len(bin(reg[RDSD])[2:])] + bin(reg[RDSD])[2:]
    #             if h2 != r2 or h3 != r3 or h4 != r4:
    #                 wc += 1
    #                 h2 = r2
    #                 h3 = r3
    #                 h4 = r4
    #                 value = int(r2[:4],2)
    #                 value2 = int(r2[5:-5],2)
    #                 if value2 == 0:
    #                     type = "A"
    #                 else:
    #                     type = "B"
    #                 code =  str(value) + type
    #                 # print("Code", code)
    #                 if code == "2B" or code == "2A":
    #                     # chars = [bitstring_to_bytes(r3[:8]), bitstring_to_bytes(r3[9:]), bitstring_to_bytes(r4[:8]), bitstring_to_bytes(r4[9:])]
    #                     # chars = [int(r3[:8], 2), int(r3[9:], 2), int(r4[:8], 2), int(r4[9:], 2)]

    #                     string_chars = [r3[:8], r3[8:], r4[:8], r4[8:]]
    #                     print('r3', r3, 'r4', r4)
    #                     print('string_chars:', string_chars)

    #                     chars = []
    #                     for c in string_chars:
    #                         chars.append(int(c, 2))

    #                     index = int(r2[12:],2)
    #                     print(index, chars)
    #                     # print(str(index) + '-' +  str(chars))
                        
    #                     if index == 0 and mi != 0:
    #                         # return ''.join(dict(sorted(msg.items())).values())
    #                         dict_values = dict(sorted(msg.items())).values()
    #                         # print('dict_values:', dict_values)
    #                         byte_list = []
    #                         for msg in dict_values:
    #                             for entry in msg:
    #                                 byte_list.append(entry)
    #                         print('byte_list:', byte_list)
    #                         return bytearray(byte_list)
    #                         # print()
    #                         # print("RDS MSG = " + ''.join(dict(sorted(msg.items())).values()))
    #                         # print()
    #                         # reset = True
    #                         # break
    #                     msg[index] = chars
    #                     if index == mi:
    #                         # msg += chars
    #                         mi += 1