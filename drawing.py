import pygame
import random
from si4703Library import si4703Radio

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

def main():
    radio = si4703Radio(0x10, 5, 19)
    radio.si4703Init()
    radio.si4703SetChannel(877)
    radio.si4703SetVolume(5)
    print(str(radio.si4703GetChannel()))
    print(str(radio.si4703GetVolume()))

    running = True
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            if mock:
                mock_draw()
            else:
                rds = radio.si4703getRDS()
                # rds is a stringified tuple (x, y), destructure it
                # stripped = rds[1:-1].split(", ")
                stripped = rds.rstrip("\x00").split(" ")
                try:
                    x, y = int(stripped[0]), int(stripped[1])
                    coords.append([x, y])
                    if len(coords) > 1:
                        pygame.draw.lines(screen, (255, 255, 255), False, coords)
                        coords.pop(0)
                    # pygame.draw.lines(screen, (255, 255, 255), False, (int(coords[0]), int(coords[1])))
                    # screen.set_at((int(coords[0]), int(coords[1])), (255, 255, 255))
                except Exception as e:
                    print(e)
                    print("RDS:", rds, "is not a valid coordinate pair")
                    pass

            pygame.display.flip()
            clock.tick(60)
                
    except KeyboardInterrupt:
        print("Exiting program")

    print("Shutting down radio")
    radio.si4703ShutDown()

    print("Shutting down pygame")
    pygame.quit()

if __name__ == "__main__":
    main()