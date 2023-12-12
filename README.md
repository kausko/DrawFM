# Data Transmission over FM Radio

This project uses the Radio Data System (RDS) protocol to live-stream drawings over FM Radio.

## Hardware

Minimum requirements:
- Raspberry Pi 3+ (x2)
- Si4713 FM Radio Transmitter
- Si4703 FM Radio Receiver
- Antenna (x2) (Can be a wire, AUX cable, etc.)
- Cables to connect everything (HDMI, GPIO, power, etc.)

## Installation

Please see [https://pinout.xyz/](https://pinout.xyz/)

### Transmitter

Physical Pin Location|   GPIO Pin      |  si4703 Breakout
--------------- |   --------------- | ----------------
1 (Board 3.3V)  |   Board 3.3V      | VIN              
6 (Board GND)   |   Board GND       | GND  
3               |   GPIO 2 SDA (BCM)     | I2C SDA         
5               |   GPIO 3 SCL (BCM)     | I2C SCL
29              |   GPIO 5           | RST           

The Transmitter wiring has been adapted from [Adafruit's tutorial for si4713 on Arduino](https://learn.adafruit.com/adafruit-si4713-fm-radio-transmitter-with-rds-rdbs-support/test-and-usage)

### Receiver
Physical Pin Location|  GPIO Pin      |  si4703 Breakout
--------------- | --------------- | ----------------
1 (Board 3.3V)  | Board 3.3V      | 3.3V              
6 (Board GND)   | Board GND       | GND  
3               | GPIO 2 SDA (BCM)     | I2C SDA         
5               | GPIO 3 SCL (BCM)     | I2C SCL
29              | GPIO 5  (BCM)        | RST
35              | GPIO 19 (BCM)        | GPIO2

The Receiver wiring is from [https://github.com/ryedwards/si4703RaspberryPi#installation](https://github.com/ryedwards/si4703RaspberryPi#installation)

### Software

Assuming you have a fresh install of Raspbian, `python-smbus`, `i2c-tools` and `pyqt5` should be already installed. If not, run the following commands:

```bash
sudo apt-get update
sudo apt-get install python-smbus
sudo apt-get install i2c-tools
sudo apt-get install python3-pyqt5
```

You will also need to enable I2C and SPI in the Raspberry Pi configuration menu.

To install the dependencies for this project, run: `pip install -r requirements.txt` (Python 3.8 or higher is required).

## Usage

For running directly on the Raspberry Pi: `python <tx/rx>_qt.py`.

For running via SSH:
```bash
sudo chmod +x <tx/rx>_qt.py # Only needs to be run once
./run_<tx/rx>.sh
```

NOTE: Here, use `tx` for the transmitter and `rx` for the receiver.

### Simulator mode
The simulator mode allows you to run the transmitter and receiver code on the same computer. This is useful for testing the drawing code without needing the physical devices. To use simulator mode, set the `SIM` environment variable to `True`, and run `python sim_driver.py`. Check the `SIM_README.md` file for more details.

## Credits
- https://docs.circuitpython.org/projects/si4713/en/latest/# - Library for controlling the Si4713 FM Transmitter via I2C using Python on the Raspberry Pi
- https://github.com/ryedwards/si4703RaspberryPi - Library for controlling the Si4703 Receiver via I2C using Python on the Raspberry Pi.
- https://github.com/GrantTrebbin/si470x-RDS_Logger - Code for reading recieved RDS data from the Si4703.

## License

GPL
