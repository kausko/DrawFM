import pygame
import random
from comm_simulator import CommunicationSimulator
from multiprocessing import shared_memory
from time import sleep

def rx_drawing(shared_input_buffer_name: str, communications_simulator: CommunicationSimulator):

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
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            if mock:
                mock_draw()
            else:
                try:
                    rds = "100 100"
                    # rds = communications_simulator.get_buffer().decode()
                    # rds = str(communications_simulator.in_buffer.decode())
                    s2 = shared_memory.ShareableList(name=shared_input_buffer_name)
                    tx_buffer = s2[0]
                    # tx_buffer = tx_buffer.encode('utf-8')
                    communications_simulator.set_buffer(tx_buffer)
                    rds = communications_simulator.get_buffer()
                    print('rds:', rds)
                    # rds is a stringified tuple (x, y), destructure it
                    # stripped = rds[1:-1].split(", ")
                    
                    try:
                        rds = rds.decode()
                        stripped = rds.rstrip("\x00").split(" ")
                        if len(stripped) == 1:
                            if stripped[0] == "clean":
                                # clear canvas or something
                                screen.fill((0, 0, 0))
                        else:
                            x, y = int(stripped[0]), int(stripped[1])
                            coords.append([x, y])
                            if len(coords) > 1:
                                if len(stripped) > 2:
                                    if stripped[2] == 'd':
                                        pygame.draw.lines(screen, (255, 255, 255), False, coords)
                                    else:
                                        pygame.draw.ellipse(screen, (255, 255, 255), pygame.Rect(x, y, 4, 4), 2)
                                
                                coords.pop(0)

                    except Exception as e:
                        print(e)
                        print("RDS:", rds, "is not a valid coordinate pair")
                        pass
                except Exception as e:
                    print(e)

            pygame.display.flip()
            clock.tick(60)
            sleep(0.05)
                
    except KeyboardInterrupt:
        print("Exiting program")


    print("Shutting down pygame")
    pygame.quit()

if __name__ == "__main__":
    s1 = shared_memory.ShareableList(["large buffer for our strings"])
    s1[0] = "100 100 p".encode('utf-8')
    communication_simulator = CommunicationSimulator(drop_rate=0.01, bitflip_rate=0.01)
    rx_drawing(shared_input_buffer_name=s1.shm.name, communications_simulator=communication_simulator)