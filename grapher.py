import argparse
import pandas as pd
import pytz
import matplotlib.pyplot as plt
import re
import warnings
from datetime import datetime, timedelta
import numpy as np
import statistics

def plot_access_time_count(csv_file, column_name, num_buckets, bucket_size):
    # Suppress warnings related to unused columns
    warnings.filterwarnings("ignore", message="Columns.*not found in file")

    # Read the CSV data from the specified file, selecting only the specified column
    df = pd.read_csv(csv_file, usecols=[column_name])

    # Define a regular expression pattern for the expected format
    valid_time_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [A-Za-z]+"

    # Filter out rows with invalid "Access Time" format
    df = df[df[column_name].str.match(valid_time_pattern, na=False)]

    # Define a function to convert time to UTC
    def convert_to_utc(access_time_str):
        # Extract the time zone part from the string
        time_zone_str = access_time_str.split()[-1]

        # Create a dictionary to map time zone abbreviations to pytz time zones
        time_zone_mapping = {
            'PST': 'US/Pacific',
            'PDT': 'US/Pacific',
            'MST': 'US/Mountain',
            'UTC': 'UTC'  # You can add more time zones as needed
        }

        # Use the time zone mapping or, if not found, use the provided time zone directly
        tz = pytz.timezone(time_zone_mapping.get(time_zone_str, time_zone_str))

        # Extract the date and time part (excluding the time zone)
        datetime_str = ' '.join(access_time_str.split()[:-1])

        # Convert datetime string to datetime object and handle ambiguous times
        dt = pd.to_datetime(datetime_str)
        try:
            utc_time = dt.tz_localize(tz, ambiguous='raise').tz_convert('UTC')
        except pytz.exceptions.AmbiguousTimeError:
            utc_time = dt.tz_localize(tz, ambiguous='NaT').tz_convert('UTC')
        return utc_time

    # Apply the conversion function to the specified column
    df['UTC Time'] = df[column_name].apply(convert_to_utc)

    # Create a line graph
    bucket_delta = timedelta(hours=bucket_size)

    # Calculate the maximum time in the DataFrame
    max_time = df['UTC Time'].max()

    if max_time is pd.NaT:
        print("No valid 'Access Time' data found.")
        return

    # Calculate the date before the maximum time based on the number of buckets and bucket size
    days_ago_date = max_time - timedelta(hours=num_buckets * bucket_size)

    # Filter the DataFrame to include only the data within the specified number of buckets
    df = df[df['UTC Time'] >= days_ago_date]

    # Initialize lists to store data
    buckets = []
    counts = []

    # Iterate through time buckets
    bucket_end = max_time
    while bucket_end >= days_ago_date:
        bucket_start = bucket_end - bucket_delta
        bucket_data = df[(df['UTC Time'] >= bucket_start) & (df['UTC Time'] <= bucket_end)]
        count = len(bucket_data)
        if count > 0:
            buckets.append(bucket_start)
            counts.append(count)
        bucket_end = bucket_start

    buckets.reverse()
    counts.reverse()

    # Convert counts to regular Python integers for standard deviation calculation
    counts = [int(count) for count in counts]

    # Calculate the mean and standard deviation of counts
    mean_count = statistics.mean(counts)
    std_deviation = statistics.stdev(counts)

    # Calculate the spike threshold
    spike_threshold = mean_count + std_deviation

    # Find the last Access Time bucket with a Count value greater than 0
    last_positive_count_index = None
    for i, count in enumerate(counts):
        if count > 0:
            last_positive_count_index = i

    # Create the line graph
    plt.plot(buckets, counts, marker='o', linestyle='-')
    plt.xlabel('Time')
    plt.ylabel('Count')
    plt.title(f'Time Grouping Count ({column_name})')
    
    # Format x-axis labels vertically with the format "%m-%d %H:%M:%S"
    plt.xticks(rotation=90)
    plt.grid(True)

    # Add count values as labels near the data points that are at least 1 std deviation above the mean
    for i, (x, y) in enumerate(zip(buckets, counts)):
        if y >= spike_threshold or i == last_positive_count_index:
            plt.annotate(y, (x, y), textcoords="offset points", xytext=(0, 5), ha='center')

    plt.show()


def main():
    parser = argparse.ArgumentParser(description='Generate a line graph of Access Time data from a CSV file.')
    parser.add_argument('-f', '--file', required=True, help='CSV file name')
    parser.add_argument('-c', '--column', required=True, help='Column name for Access Time data')
    parser.add_argument('-n', '--num_buckets', type=int, default=30, help='Number of buckets')
    parser.add_argument('-s', '--bucket_size', type=int, default=24, help='Bucket size in hours')
    args = parser.parse_args()
    
    plot_access_time_count(args.file, args.column, args.num_buckets, args.bucket_size)

if __name__ == '__main__':
    main()
