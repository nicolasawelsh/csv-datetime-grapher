import argparse
import pandas as pd
import pytz
import matplotlib.pyplot as plt
import re
import warnings
from datetime import datetime, timedelta
import numpy as np
import statistics

def plot_access_time_count(csv_file, column_name, num_buckets, bucket_size, csv_file2=None):
    # Suppress warnings related to unused columns
    warnings.filterwarnings("ignore", message="Columns.*not found in file")

    # Read the first CSV data from the specified file, selecting only the specified column
    df1 = pd.read_csv(csv_file, usecols=[column_name])

    # Define a regular expression pattern for the expected format
    valid_time_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [A-Za-z]+"

    # Filter out rows with invalid "Access Time" format
    df1 = df1[df1[column_name].str.match(valid_time_pattern, na=False)]

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
    df1['UTC Time'] = df1[column_name].apply(convert_to_utc)

    # Create a line graph for the first CSV data
    bucket_delta = timedelta(hours=bucket_size)

    # Calculate the maximum time in the DataFrame
    max_time = df1['UTC Time'].max()

    if max_time is pd.NaT:
        print("No valid 'Access Time' data found for the first CSV file.")
        return

    # Calculate the date before the maximum time based on the number of buckets and bucket size
    days_ago_date = max_time - timedelta(hours=num_buckets * bucket_size)

    # Filter the DataFrame to include only the data within the specified number of buckets
    df1 = df1[df1['UTC Time'] >= days_ago_date]

    # Initialize lists to store data for the first CSV
    buckets1 = []
    counts1 = []

    # Iterate through time buckets for the first CSV
    bucket_end = max_time
    while bucket_end >= days_ago_date:
        bucket_start = bucket_end - bucket_delta
        bucket_data = df1[(df1['UTC Time'] >= bucket_start) & (df1['UTC Time'] <= bucket_end)]
        count = len(bucket_data)
        if count > 0:
            buckets1.append(bucket_start)
            counts1.append(count)
        bucket_end = bucket_start

    buckets1.reverse()
    counts1.reverse()

    # Convert counts to regular Python integers for standard deviation calculation
    counts1 = [int(count) for count in counts1]

    # Calculate the mean and standard deviation of counts for the first CSV
    mean_count1 = statistics.mean(counts1)
    std_deviation1 = statistics.stdev(counts1)

    # Calculate the spike threshold for the first CSV
    spike_threshold1 = mean_count1 + std_deviation1

    # Find the last Access Time bucket with a Count value greater than 0 for the first CSV
    last_positive_count_index1 = None
    for i, count in enumerate(counts1):
        if count > 0:
            last_positive_count_index1 = i

    # Create the line graph for the first CSV data
    plt.plot(buckets1, counts1, marker='o', linestyle='-', label='File 1')
    
    if csv_file2:
        # Read the second CSV data from the specified file, selecting only the specified column
        df2 = pd.read_csv(csv_file2, usecols=[column_name])

        # Filter out rows with invalid "Access Time" format for the second CSV
        df2 = df2[df2[column_name].str.match(valid_time_pattern, na=False)]

        # Apply the conversion function to the specified column for the second CSV
        df2['UTC Time'] = df2[column_name].apply(convert_to_utc)

        # Calculate the maximum time in the DataFrame for the second CSV
        max_time2 = df2['UTC Time'].max()

        if max_time2 is pd.NaT:
            print("No valid 'Access Time' data found for the second CSV file.")
        else:
            # Calculate the date before the maximum time based on the number of buckets and bucket size for the second CSV
            days_ago_date2 = max_time2 - timedelta(hours=num_buckets * bucket_size)

            # Filter the DataFrame to include only the data within the specified number of buckets for the second CSV
            df2 = df2[df2['UTC Time'] >= days_ago_date2]

            # Initialize lists to store data for the second CSV
            buckets2 = []
            counts2 = []

            # Iterate through time buckets for the second CSV
            bucket_end = max_time2
            while bucket_end >= days_ago_date2:
                bucket_start = bucket_end - bucket_delta
                bucket_data = df2[(df2['UTC Time'] >= bucket_start) & (df2['UTC Time'] <= bucket_end)]
                count = len(bucket_data)
                if count > 0:
                    buckets2.append(bucket_start)
                    counts2.append(count)
                bucket_end = bucket_start

            buckets2.reverse()
            counts2.reverse()

            # Convert counts to regular Python integers for standard deviation calculation for the second CSV
            counts2 = [int(count) for count in counts2]

            # Calculate the mean and standard deviation of counts for the second CSV
            mean_count2 = statistics.mean(counts2)
            std_deviation2 = statistics.stdev(counts2)

            # Calculate the spike threshold for the second CSV
            spike_threshold2 = mean_count2 + std_deviation2

            # Find the last Access Time bucket with a Count value greater than 0 for the second CSV
            last_positive_count_index2 = None
            for i, count in enumerate(counts2):
                if count > 0:
                    last_positive_count_index2 = i

            # Create the line graph for the second CSV data
            plt.plot(buckets2, counts2, marker='o', linestyle='-', label='File 2')

    plt.xlabel('Time')
    plt.ylabel('Count')
    plt.title(f'Time Grouping Count ({column_name})')
    
    # Format x-axis labels vertically with the format "%m-%d %H:%M:%S"
    plt.xticks(rotation=90)
    plt.grid(True)

    # Add count values as labels near the data points that are at least 1 std deviation above the mean for the first CSV
    for i, (x, y) in enumerate(zip(buckets1, counts1)):
        if y >= spike_threshold1 or i == last_positive_count_index1:
            plt.annotate(y, (x, y), textcoords="offset points", xytext=(0, 5), ha='center')

    # Add count values as labels near the data points that are at least 1 std deviation above the mean for the second CSV
    if csv_file2:
        for i, (x, y) in enumerate(zip(buckets2, counts2)):
            if y >= spike_threshold2 or i == last_positive_count_index2:
                plt.annotate(y, (x, y), textcoords="offset points", xytext=(0, 5), ha='center')

    plt.legend()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Generate a line graph of Access Time data from CSV files.')
    parser.add_argument('-f', '--file', required=True, help='First CSV file name')
    parser.add_argument('-f2', '--file2', help='Second CSV file name')
    parser.add_argument('-c', '--column', required=True, help='Column name for Access Time data')
    parser.add_argument('-n', '--num_buckets', type=int, default=30, help='Number of buckets')
    parser.add_argument('-s', '--bucket_size', type=int, default=24, help='Bucket size in hours')
    args = parser.parse_args()
    
    plot_access_time_count(args.file, args.column, args.num_buckets, args.bucket_size, args.file2)

if __name__ == '__main__':
    main()
