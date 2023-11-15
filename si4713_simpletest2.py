# SPDX-FileCopyrightText: 2018 Tony DiCola for Adafruit Industries

# SPDX-License-Identifier: MIT


# Simple demo of using the SI4743 RDS FM transmitter.


import time

import board

import digitalio

import adafruit_si4713

import pygame

 

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
points = []
disp_points= []


# Specify the FM frequency to transmit on in kilohertz.  As the datasheet

# mentions you can only specify 50khz steps!

FREQUENCY_KHZ = 87700  # 102.300mhz


# Initialize I2C bus.

i2c = board.I2C()  # uses board.SCL and board.SDA

# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller


# Initialize SI4713.

# si4713 = adafruit_si4713.SI4713(i2c)


# Alternatively you can specify the I2C address of the device if it changed:

# si4713 = adafruit_si4713.SI4713(i2c, address=0x11)


# If you hooked up the reset line you should specify that too.  Make sure

# to pass in a DigitalInOut instance.  You will need the reset pin with the

# Raspberry Pi, and probably other devices:

si_reset = digitalio.DigitalInOut(board.D5)


print("initializing si4713 instance")

si4713 = adafruit_si4713.SI4713(i2c, reset=si_reset, timeout_s=0.5)

print("done")


# Measure the noise level for the transmit frequency (this assumes automatic

# antenna capacitance setting, but see below to adjust to a specific value).

noise = si4713.received_noise_level(FREQUENCY_KHZ)

# Alternatively measure with a specific frequency and antenna capacitance.

# This is not common but you can specify antenna capacitance as a value in pF

# from 0.25 to 47.75 (will use 0.25 steps internally).  If you aren't sure

# about this value, stick with the default automatic capacitance above!

# noise = si4713.received_noise_level(FREQUENCY_KHZ, 0.25)

print("Noise at {0:0.3f} mhz: {1} dBuV".format(FREQUENCY_KHZ / 1000.0, noise))


# Tune to transmit with 115 dBuV power (max) and automatic antenna tuning

# capacitance (default, what you probably want).

si4713.tx_frequency_khz = FREQUENCY_KHZ

si4713.tx_power = 115


# Configure RDS broadcast with program ID 0xADAF (a 16-bit value you specify).

# You can also set the broadcast station name (up to 96 bytes long) and

# broadcast buffer/song information (up to 106 bytes long).  Setting these is

# optional and you can later update them by setting the rds_station and

# rds_buffer property respectively.  Be sure to explicitly specify station

# and buffer as byte strings so the character encoding is clear.

# si4713.configure_rds(0xADAF, station=b"FCCPleaseDontReadFoulLanguage", rds_buffer=b"the brown fox jumps over the lazy dog. im a ramblin reck from georgia tech and i am using low power radio")


# Print out some transmitter state:

print("Transmitting at {0:0.3f} mhz".format(si4713.tx_frequency_khz / 1000.0))

print("Transmitter power: {0} dBuV".format(si4713.tx_power))

print(

    "Transmitter antenna capacitance: {0:0.2} pF".format(si4713.tx_antenna_capacitance)

)


# Set GPIO1 and GPIO2 to actively driven outputs.

si4713.gpio_control(gpio1=True, gpio2=True)


# Main loop will print input audio level and state and blink the GPIOs.

print("Broadcasting...")

# rds_message = 'a message with like 30 chars the quick brown fox jumps over the lazy dog'

# print(len(rds_message))

si4713.configure_rds(0xADAF, station=bytes('(1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (9,9), (10,10)', 'utf-8'), rds_buffer=bytes('(1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (9,9), (10,10)', 'utf-8'))

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
    # if counter % 2 == 0:
    #     si4713._set_rds_buffer(b'(1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (9,9), (10,10)')
    # else:
    #     si4713._set_rds_buffer(b'(11,11), (12,12), (13,13), (14,14), (15,15), (16,16), (17,17)')

    # if counter % 10 == 0:
    #     counter = 0
    
    # my_str = '({},{})'.format(counter, counter)
    # print(my_str)

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

        si4713._set_rds_buffer(bytes(my_str, 'utf-8'))

    # si4713._set_rds_buffer(b'(11,11), (12,12), (13,13), (14,14), (15,15), (16,16), (17,17), (18,18), (19,19), (20,20)')
    # si4713._set_rds_buffer(b'alpha bravo charlie delta echo foxtrot golf hotel igloo ')
    # si4713._set_rds_station(bytes(counter))
    # counter += 1
    time.sleep(0.15)

# counter = 0

# while True:

#     # Print input audio level and state.

    print("Input level: {0} dBfs".format(si4713.input_level))

    print("ASQ status: 0x{0:02x}".format(si4713.audio_signal_status))

#     # if counter % 20 < 10:
#     #     rds_message += '*'
#     # else:
#     #     rds_message += '_'
#     # rds_message = rds_message[1:]
#     # counter = counter + 1

#     # print(rds_message)

#     # si4713.configure_rds(0xADAF, station=bytes(rds_message, 'utf-8'), rds_buffer=bytes(rds_message, 'utf-8'))


#     # 'Blink' GPIO1 and GPIO2 alternatively on and off.

#     si4713.gpio_set(gpio1=True, gpio2=False)  # GPIO1 high, GPIO2 low

#     time.sleep(0.5)

#     si4713.gpio_set(gpio1=False, gpio2=True)  # GPIO1 low, GPIO2 high

#     time.sleep(0.5)