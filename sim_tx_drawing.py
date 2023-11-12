# SPDX-FileCopyrightText: 2018 Tony DiCola for Adafruit Industries

# SPDX-License-Identifier: MIT


# Simple demo of using the SI4743 RDS FM transmitter.


import time

import pygame
from comm_simulator import CommunicationSimulator
from multiprocessing import Value, shared_memory
from multiprocessing.managers import SharedMemoryManager
import numpy as np

def tx_drawing(shared_input_buffer_name: str): 

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Paint Capture")

    

    # Define the red square's properties
    square_color = (255, 0, 0)  # Red color
    square_size = 50
    square_x = 750  # Top right corner
    square_y = 0

    clean_screen = False

    drawing = False
    drawing_start = time.time()
    drawing_end = time.time()
    drawing_final = time.time()
    time_of_last_drawing = time.time()
    time_of_last_last_drawing = time_of_last_drawing
    last_down = False
    points = []
    disp_points= []

    counter = 0

    while True:

        x = None
        y = None

        timestamp = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                drawing_start = timestamp
                points.append(event.pos)
                x, y = event.pos
                # Check if the mouse click is inside the square
                if square_x <= x <= square_x + square_size and square_y <= y <= square_y + square_size:
                    clean_screen = True
            elif event.type == pygame.MOUSEMOTION:
                if drawing:
                    drawing_end = timestamp
                    points.append(event.pos)
                    x, y = event.pos
                    # print(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                drawing_end = timestamp
                drawing_final = timestamp
                x, y = event.pos
                disp_points.append(points[:])
                points.clear()
                # print(disp_points)
            
            if drawing:
                time_of_last_drawing = time.time()
                
    

        screen.fill((255, 255, 255))  # Fill the screen with white
        
        # Draw the red square
        pygame.draw.rect(screen, square_color, (square_x, square_y, square_size, square_size))
        
        if(clean_screen):
            disp_points.clear()

        # Draw the points
        if len(points) > 1:
            pygame.draw.lines(screen, (255, 0, 0), False, points)
        #for point in points:
            #pygame.draw.circle(screen, (0,0,0), point, 10)
        for pt in disp_points:
            if len(pt) > 1:
                pygame.draw.lines(screen, (0, 255, 0), False, pt)


        pygame.display.update()


        #print(x,y)

        if x!= None:

            # print(drawing_end - drawing_start, drawing_final - drawing_start)

            if drawing_end - drawing_start > 0:
                my_str = "{x} {y} d".format(x=x, y=y)
            else:
                my_str = "{x} {y} p".format(x=x, y=y)

            

            if clean_screen:
                my_str = "clean"
                clean_screen = False

            print(my_str)

            # si4713._set_rds_buffer(bytes(my_str, 'utf-8'))

            # print(communications_simulator)
            s2 = shared_memory.ShareableList(name=shared_input_buffer_name)
            # print(s2)
            s2[0] = my_str.encode('utf-8')


        # si4713._set_rds_buffer(b'(11,11), (12,12), (13,13), (14,14), (15,15), (16,16), (17,17), (18,18), (19,19), (20,20)')
        # si4713._set_rds_buffer(b'alpha bravo charlie delta echo foxtrot golf hotel igloo ')
        # si4713._set_rds_station(bytes(counter))
        # counter += 1
        time.sleep(0.15)

if __name__ == "__main__":
    s1 = shared_memory.ShareableList(["large buffer for our strings"])
    s1[0] = "100 100 p".encode('utf-8')

    tx_drawing(shared_input_buffer_name=s1.shm.name)