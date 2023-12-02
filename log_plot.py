import matplotlib.pyplot as plt
# import pandas as pd
from datetime import datetime
import json
import os

cwd = os.getcwd()
rx_logfile_name = 'logs_rx/2023-11-29 01:55:41.005135-rx.log'
rx_log_rec = open(os.path.join(cwd, rx_logfile_name), 'r')
 
# print(rx_log_rec.read())

rx_log_rec_str = rx_log_rec.read()

rx_log_rec = '[' + rx_log_rec_str[:-2] + ']'

rec_json = json.loads(rx_log_rec)


# bin_str = rec_json[1]['binary']
# int_val = int(bin_str[2:-1],16)
# print(int_val)

# date_time_object = datetime.strptime(rec_json[1]['datetime'], '%Y-%m-%d %H:%M:%S.%f')
# print(date_time_object.timestamp())

time_val = []
data = []

for obj in rec_json:
    bin_str = obj['binary']
    int_val = int(bin_str[2:-1],16)

    data.append(int_val)

    date_time_object = datetime.strptime(obj['datetime'], '%Y-%m-%d %H:%M:%S.%f')

    time_val.append(date_time_object.timestamp())

plt.plot(time_val, data, marker='o')

# Label the axes
plt.xlabel('Time (Unix Timestamp)')
plt.ylabel('Integer Values')

# Show the plot
plt.show()
    


tx_logfile_name = '2023-11-29 01:55:41.005135-rx.log'
tx_log_rec = os.path.join(cwd, rx_logfile_name)







