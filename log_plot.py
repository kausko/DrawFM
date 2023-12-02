import matplotlib.pyplot as plt
# import pandas as pd
from datetime import datetime
import json
import os

cwd = os.getcwd()
# rx_logfile_name = 'logs_rx/2023-11-29 01:55:41.005135-rx.log'
# rx_logfile_name = os.path.join('logs_rx', '2023-11-29 17:56:26.168711-rx_1m_50ms.log')
# tx_logfile_name = os.path.join('logs_tx', '2023-11-29 17:56:33.472757-tx_1m_50ms.log')

rx_logfile_name = os.path.join('logs_rx', '2023-11-29 18:34:28.631674-rx_1m_200ms.log')
tx_logfile_name = os.path.join('logs_tx', '2023-11-29 18:34:30.524326-tx_1m_200ms.log')



rx_log_rec = open(os.path.join(cwd, rx_logfile_name), 'r')
tx_log_rec = open(os.path.join(cwd, tx_logfile_name), 'r')
 
def parse_log_file(log_file, is_tx=False):


    log_rec_lines = log_file.readlines()
    # print(log_rec_str)

    if is_tx:
        # skip first 5 lines
        log_rec_lines = log_rec_lines[5:]
    
    log_rec_str = '\n'.join(log_rec_lines)

    # remove trailing comma and surround with []
    log_rec = '[' + log_rec_str[:-2] + ']'   

    rec_json = json.loads(log_rec)

    time_val = []
    data = []

    for obj in rec_json:
        bin_str = obj['binary']
        int_val = int(bin_str[2:-1],16)

        date_string = obj['datetime']

        if '.' not in date_string:
            date_string = date_string + '.0'

        date_time_object = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')
        data.append(int_val)
        time_val.append(date_time_object.timestamp())

    
    return time_val, data

rx_time_val, rx_data = parse_log_file(rx_log_rec)
print(len(rx_time_val), len(rx_data))
tx_time_val, tx_data = parse_log_file(tx_log_rec, is_tx=True)

plt.scatter(rx_time_val, rx_data, marker='o', s=1)
plt.scatter(tx_time_val, tx_data, marker='s', s=1)

# Label the axes
plt.xlabel('Time (Unix Timestamp)')
plt.ylabel('Integer Values')

# set ylim to the range of tx data
# (prevents spurious data from rx from affecting our scale)
plt.ylim(0, max(tx_data))

# Show the plot
plt.show()
