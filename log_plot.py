import matplotlib.pyplot as plt
# import pandas as pd
from datetime import datetime
import json
import os
import glob
from collections import defaultdict
import pandas as pd
import numpy as np

cwd = os.getcwd()

rx_log_dir = os.path.join('logs_rx')
tx_log_dir = os.path.join('logs_tx')

log_comparisons = defaultdict(dict)

rx_log_list = [each for each in os.listdir(rx_log_dir) if each.endswith('.log') and '_' in each]
tx_log_list = [each for each in os.listdir(tx_log_dir) if each.endswith('.log') and '_' in each]

for rx_file in rx_log_list:
    experiment_distance = rx_file.split('_')[1]
    experiment_delay = rx_file.split('_')[2].split('.')[0]

    experiment_tag = experiment_distance + '_' + experiment_delay
    print(experiment_tag)

    log_comparisons[experiment_tag]['rx_filename'] = os.path.join(rx_log_dir, rx_file)

for tx_file in tx_log_list:
    experiment_distance = tx_file.split('_')[1]
    experiment_delay = tx_file.split('_')[2].split('.')[0]

    experiment_tag = experiment_distance + '_' + experiment_delay
    print(experiment_tag)

    log_comparisons[experiment_tag]['tx_filename'] = os.path.join(tx_log_dir, tx_file)

print(json.dumps(log_comparisons, indent=2))

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

    
    return pd.DataFrame({'time_val': time_val, 'data': data})

def plot_logs(rx_log_rec, tx_log_rec, experiment_tag):

    rx_df = parse_log_file(rx_log_rec)
    # rx_df = remove_dup(rx_log_rec)
    tx_df = parse_log_file(tx_log_rec, is_tx=True)

    print(rx_df)

    tx_start_time = tx_df['time_val'].min()
    tx_df['time_val'] -= tx_start_time
    rx_df['time_val'] -= tx_start_time

    plt.scatter(rx_df['time_val'], rx_df['data'], marker='o', s=1)
    plt.scatter(tx_df['time_val'], tx_df['data'], marker='s', s=1)

    # Label the axes
    plt.xlabel('Time (seconds after tx start)')
    plt.ylabel('Sequence Number (integer)')
    
    plt.title(experiment_tag)

    # set ylim to the range of tx data
    # (prevents spurious data from rx from affecting our scale)
    plt.ylim(0, max(tx_df['data']))

    # Show the plot
    plt.show()

def remove_dup(rx_log_rec):

    rx_df = parse_log_file(rx_log_rec)

    # Find and remove duplicate rows based on the 'data' column
    rx_df_clean = rx_df.drop_duplicates(subset='data', keep='first')

    # Print the dropped rows
    dropped_rows = rx_df[rx_df.duplicated(subset='data', keep='first')]
    print("\nDropped Rows:")
    print(dropped_rows)
    print("\n blah")

    return rx_df_clean

def plot_cdf(rx_log_rec, tx_log_rec, experiment_tag):

    rx_df = remove_dup(rx_log_rec)
    tx_df = parse_log_file(tx_log_rec, is_tx=True)

    # Merge the DataFrames on the 'data' field
    merged_df = pd.merge(rx_df, tx_df, on='data', suffixes=('_rx', '_tx'))

    # Calculate the difference in 'time_val' for each row
    merged_df['time_val_diff'] = merged_df['time_val_rx'] - merged_df['time_val_tx']

    # Display the result
    print(merged_df[['data', 'time_val_rx', 'time_val_tx', 'time_val_diff']])

    hist, bin_edges = np.histogram(merged_df['time_val_diff'], bins=50, density=True)

    # Find the PDF of the histogram   
    pdf = hist / sum(hist)

    # Calculate the CDF
    cdf = np.cumsum(pdf)

    # Plot CDF
    plt.figure(figsize=(8, 6))
    plt.plot(bin_edges[1:], cdf, label='CDF')
    plt.title(experiment_tag)
    plt.xlabel('time_val_diff')
    plt.ylabel('CDF')
    plt.legend()
    plt.grid(True)
    plt.show()

for experiment_tag in sorted(log_comparisons.keys()):
    rx_log_filepath = log_comparisons[experiment_tag]['rx_filename']
    tx_log_filepath = log_comparisons[experiment_tag]['tx_filename']

    rx_log_rec = open(os.path.join(rx_log_filepath), 'r')
    tx_log_rec = open(os.path.join(tx_log_filepath), 'r')

    plot_logs(rx_log_rec, tx_log_rec, experiment_tag)
    rx_log_rec.seek(0)
    tx_log_rec.seek(0)
    plot_cdf(rx_log_rec, tx_log_rec, experiment_tag)
    rx_log_rec.close()
    tx_log_rec.close()

