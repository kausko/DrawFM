## Simulator

### How it was made
I modified our existing files
- `drawing.py` --> `sim_rx_drawing.py` -> `rx_qt.py`
- `si4713_simpletest.py` --> `sim_tx_drawing.py` -> `tx_qt.py`

I took out the parts that had to do with the Hardware and Raspberry Pi modules, so that tx_qt.py and rx_qt.py can be tested standalone.
This will help us develop the drawing code without needing the physical devices. I've also modeled an unreliable communication channel so that we can learn how to deal with noise.

### Running TX and RX drawing code with Python Multiprocessing
I wrote `sim_driver.py` to launch both `tx_qt.py` and `rx_qt.py` concurrently.

To share information between processes, I used `multiprocessing` `ShareableList`.
I initialize the `ShareableList` with a list with a single element containing a large string at index `[0]`. This is our memory buffer.

I have `tx_qt.py` write to the `ShareableList` buffer at index `[0]` with the bytes it would have sent to the transmitter rds buffer.

`rx_qt.py` shares this buffer and reads that value (instead of reading from the receiver rds buffer).

### Simulating an unstable communication channel

To simulate an unstable communication channel, I created `CommunicationSimulator` in `comm_simulator.py`
It takes these parameters:
- `drop_rate`: the fraction of bytes to drop
  - This simulates dropped chars due to signal or checksum errors
- `bitflip_rate`: the fraction of bits to flip
  - This simulates bitflips that make it through the checksum check
  - It would be interesting to *actually* simulate the checksum bitflips / algorithm, but that's future work

`rx_qt.py` runs the shared input buffer through this `CommunicationSimulator` in order to get a value similar to what comes out of our receiver.

### Drawing Protocol Updates
I have updated the drawing protocol
- `x y d`: Draw line from `x, y` to previous coordinate
- `x y p`: Draw a point at `x, y`
- `clean`: Erase the screen