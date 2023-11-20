import pygame
import random
from comm_simulator import CommunicationSimulator
from multiprocessing import shared_memory
from time import sleep
# from struct import *
from bitstruct import *
from binascii import hexlify
import time
from utils import my_memcpy
from os import getenv
from dotenv import load_dotenv
load_dotenv()
sim = getenv("SIM") == "True"

if not sim:
    '''RASPBERRY PI: use below'''
    from si4703Library import si4703Radio
    '''RASPBERRY PI: use above'''

PACK_CODE = 'u10u10u6u6'

PACK_CODES = {
    'draw': 'u10u10u4u4u4', # x, y, draw_line, draw_clear, msg_type
    'color': 'u8u8u8u4u4',  # r, g, b, a (scaled 0-16), msg_type
    'size': 'u10u18u4'  # size (0-1023), unused, msg_type
}

def rx_drawing(shared_input_buffer_name: str, communications_simulator: CommunicationSimulator):
    
    if not sim:
        '''RASPBERRY PI: use below'''
        radio = si4703Radio(0x10, 5, 19)
        radio.si4703Init()
        radio.si4703SetChannel(877)
        radio.si4703SetVolume(5)
        print(str(radio.si4703GetChannel()))
        print(str(radio.si4703GetVolume()))
        '''RASPBERRY PI: use above'''

    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((1024, 1024))
    screen.fill((255, 255, 255))
    clock = pygame.time.Clock()

    # mock setup
    mock = False
    coords = []
    if mock:
        coords = [[random.randint(0, 812), random.randint(0, 720)]]
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
        r, g, b, = (0, 0, 0)
        a = 255
        brush_size = 3
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            if mock:
                mock_draw()
            else:
                try:
                    if not sim:
                        '''RASPBERRY PI: use below'''
                        # if the below function isn't implemented, you need to add it to the si4703 library
                        # I've included the function commented out at the bottom of this file.
                        # Just copy and paste it to the same file where the radio.si4703getRDS() function is
                        rds = radio.si4703getRDSBytes()
                        '''RASPBERRY PI: use above'''
                    else:
                        '''SIMULATOR: use below'''
                        '''NOTE: you need to comment this out when running on hardware, as it overwrites the rds variable'''
                        s2 = shared_memory.SharedMemory(name=shared_input_buffer_name)
                        tx_buffer = s2.buf
                        communications_simulator.set_buffer(tx_buffer)
                        rds = communications_simulator.get_buffer()
                        '''SIMULATOR: use above'''


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
                    
                    (x, y, data_line, data_clean) = unpack(PACK_CODE, rds[:4])

                    for key, pack_code in PACK_CODES.items():
                        if key == 'draw':
                            (x, y, data_line, data_clean, msg_type) = unpack(pack_code, rds[:4])
                        elif key == 'color':
                            (msg_r, msg_g, msg_b, msg_a, msg_type) = unpack(pack_code, rds[:4])
                            msg_a = msg_a * 16  # using 4-bit value for alpha, so scale by 2^4
                        elif key == 'size':
                            msg_brush_size, msg_dontcare, msg_type = unpack(pack_code, rds[:4])
                                

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
                        print(r, g, b, a, time.time())
                        if msg_type != 15 and msg_type != 3 and msg_type == 0:
                            # not a change color message, not a size change message
                            # and is a 0 for draw message
                            coords.append([x, y])
                        print('coords len:', len(coords))
                        
                        if msg_type == 15:
                            # change color message
                            r = msg_r
                            g = msg_g
                            b = msg_b
                            a = msg_a
                        elif msg_type == 3:
                            # change size message
                            brush_size = msg_brush_size
                        elif data_clean == 15:
                            # clear canvas or something
                            screen.fill((255, 255, 255))
                            coords = []
                        elif True:
                            # print(coords)
                            if data_line == 15 or data_line == 0:
                                # print('data_line', data_line, 'last_data_line', last_data_line)
                                if data_line != last_data_line:
                                    # pygame.draw.lines(screen, (255, 255, 255), False, coords[:-1])
                                    coords = [coords[-1]]
                                    
                                else:
                                    # pygame.draw.lines(screen, (r, g, b, a), False, [coords[-1], coords[-2]], width=brush_size)
                                    pygame.draw.line(screen, (r, g, b, a), coords[-1], coords[-2], width=brush_size)
                                    pygame.draw.ellipse(screen, (r, g, b, a), pygame.Rect(x - brush_size // 2, y - brush_size // 2, brush_size, brush_size), brush_size)

                                # pygame.draw.lines(screen, (255, 255, 255), False, coords[:-2])
                                
                                last_data_line = data_line

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
    s1 = shared_memory.SharedMemory(name='s1', create=True, size=6)
    pack_data = pack(PACK_CODES['draw'], 255, 255, 15, 15, 0)
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