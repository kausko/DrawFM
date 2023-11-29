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

### Transmitter
<!--TODO-->

### Receiver
  GPIO Pin      |  si4703 Breakout
--------------- | ----------------
2 SDA (BCM)     | I2C SDA         
3 SCL (BCM)     | I2C SCL
5  (BCM)        | RST
19 (BCM)        | GPIO2              
1 (Board 3.3v)  | 3.3V              
6 (Board Gnd)   | GND             

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

## Credits

- https://github.com/ryedwards/si4703RaspberryPi - Library for controlling the Si4703 via I2C using Python on the Raspberry Pi.
- https://github.com/GrantTrebbin/si470x-RDS_Logger - Code for reading the RDS data from the Si4703.

## License

GPL
