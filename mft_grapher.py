import argparse
import pandas as pd
import matplotlib.pyplot as plt
import re
import warnings
from datetime import datetime, timedelta
import numpy as np
import statistics
import os
import pytz

from datetime import datetime, timedelta
import pytz  # Import the pytz library for timezone handling



def convert_datetime_format(input_datetime_string, output_timezone="UTC"):
    time_zone_mapping = {
    'PST': 'US/Pacific',
    'PDT': 'US/Pacific',
    'MST': 'US/Mountain',
    'UTC': 'UTC'
    }
   
    try:
        # Parse the input datetime string and extract the %Z component
        input_format = "%Y-%m-%d %H:%M:%S %Z"
        dt = datetime.strptime(input_datetime_string, input_format)
        input_timezone_abbreviation = dt.strftime("%Z")

        print(input_datetime_string)

        # Map the %Z component to the input timezone
        if input_timezone_abbreviation in time_zone_mapping:
            input_timezone = time_zone_mapping[input_timezone_abbreviation]
        else:
            # Default to UTC if the mapping is not found
            input_timezone = "UTC"

        # Convert it to the desired output timezone
        input_tz = pytz.timezone(input_timezone)
        output_tz = pytz.timezone(output_timezone)
        dt = input_tz.localize(dt)
        dt = dt.astimezone(output_tz)

        # Convert it to the desired format
        output_format = "%Y-%m-%d %H:%M:%S.%f"
        converted_datetime_string = dt.strftime(output_format)

        return converted_datetime_string

    except ValueError:
        # Handle invalid datetime strings
        return None


def process_csv_files_in_directory(directory, column_name, num_buckets, bucket_size, mft, autopsy_deleted):
    data_frames = []
    legend_labels = []

    if mft:
        valid_time_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d+"

    elif autopsy_deleted:
        valid_time_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [A-Za-z]+"

    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            warnings.filterwarnings("ignore", message="Columns.*not found in file")
            df = pd.read_csv(file_path, usecols=[column_name])
            df = df[df[column_name].str.match(valid_time_pattern, na=False)]
            if not df.empty:
                if mft:
                    df[column_name] = pd.to_datetime(df[column_name], format="%Y-%m-%d %H:%M:%S.%f")
                elif autopsy_deleted:
                    df[column_name] = df[column_name].apply(convert_datetime_format)
                data_frames.append(df)
                legend_labels.append(filename)

    if not data_frames:
        print("No valid time data found in any CSV file in the directory.")
        return None, None

    return data_frames, legend_labels


def plot_access_time_count(data_frames, column_name, num_buckets, bucket_size, legend_labels):
    # Create a line graph for the combined data
    bucket_delta = timedelta(hours=bucket_size)

    plt.figure(figsize=(10, 6))
    for i in range(len(data_frames)):
        df = data_frames[i]
        label = legend_labels[i]

        # Calculate the maximum time in the DataFrame
        max_time = df[column_name].max()

        if pd.isna(max_time):
            print("No valid time data found in the data.")
            return

        # Calculate the date before the maximum time based on the number of buckets and bucket size
        days_ago_date = max_time - timedelta(hours=num_buckets * bucket_size)

        # Filter the DataFrame to include only the data within the specified number of buckets
        df = df[df[column_name] >= days_ago_date]

        # Initialize lists to store data
        buckets = []
        counts = []

        # Iterate through time buckets
        bucket_end = max_time
        while bucket_end >= days_ago_date:
            bucket_start = bucket_end - bucket_delta
            bucket_data = df[(df[column_name] >= bucket_start) & (df[column_name] <= bucket_end)]
            count = len(bucket_data)
            if count > 0:
                buckets.append(bucket_start)
                counts.append(count)
            else:
                buckets.append(bucket_start)  # To keep the same number of buckets
                counts.append(0)
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

        # Find the last time bucket with a Count value greater than 0
        last_positive_count_index = None
        for i, count in enumerate(counts):
            if count > 0:
                last_positive_count_index = i

        # Print the label of the CSV file
        print("CSV File Label:", label)

        # Track start and end times of spikes
        spike_start_time = None
        spike_end_time = None

        for i, (x, y) in enumerate(zip(buckets, counts)):
            if y >= spike_threshold:
                if spike_start_time is None:
                    spike_start_time = x
                spike_end_time = x
            elif i == last_positive_count_index:
                # Print the start and end time of the spike
                if spike_start_time is not None:
                    print("Spike Start Time:", spike_start_time)
                    print("Spike End Time:", spike_end_time)
                spike_start_time = None
                spike_end_time = None

        # Plot data for the current CSV file
        plt.plot(buckets, counts, marker='o', linestyle='-', label=label)

        plt.xlabel('Time')
        plt.ylabel('Count')
        plt.title(f'Time Grouping vs Count ({column_name})')

        # Format x-axis labels vertically with the format "%Y-%m-%d %H:%M:%S.%f"
        plt.xticks(rotation=90)
        plt.grid(True)
        plt.legend()

        # Add count values as labels near the data points that are at least 1 std deviation above the mean
        for i, (x, y) in enumerate(zip(buckets, counts)):
            if y >= spike_threshold or i == last_positive_count_index:
                plt.annotate(y, (x, y), textcoords="offset points", xytext=(0, 5), ha='center')

    # Create a line graph for the combined data
    bucket_delta = timedelta(hours=bucket_size)

    plt.figure(figsize=(10, 6))
    for i in range(len(data_frames)):
        df = data_frames[i]
        label = legend_labels[i]

        # Calculate the maximum time in the DataFrame
        max_time = df[column_name].max()

        if pd.isna(max_time):
            print("No valid time data found in the data.")
            return

        # Calculate the date before the maximum time based on the number of buckets and bucket size
        days_ago_date = max_time - timedelta(hours=num_buckets * bucket_size)

        # Filter the DataFrame to include only the data within the specified number of buckets
        df = df[df[column_name] >= days_ago_date]

        # Initialize lists to store data
        buckets = []
        counts = []

        # Iterate through time buckets
        bucket_end = max_time
        while bucket_end >= days_ago_date:
            bucket_start = bucket_end - bucket_delta
            bucket_data = df[(df[column_name] >= bucket_start) & (df[column_name] <= bucket_end)]
            count = len(bucket_data)
            if count > 0:
                buckets.append(bucket_start)
                counts.append(count)
            else:
                buckets.append(bucket_start)  # To keep the same number of buckets
                counts.append(0)
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

        # Find the last time bucket with a Count value greater than 0
        last_positive_count_index = None
        for i, count in enumerate(counts):
            if count > 0:
                last_positive_count_index = i

        # Plot data for the current CSV file
        plt.plot(buckets, counts, marker='o', linestyle='-', label=label)

        plt.xlabel('Time')
        plt.ylabel('Count')
        plt.title(f'Time Grouping vs Count ({column_name})')

        # Format x-axis labels vertically with the format "%Y-%m-%d %H:%M:%S.%f"
        plt.xticks(rotation=90)
        plt.grid(True)
        plt.legend()

        # Add count values as labels near the data points that are at least 1 std deviation above the mean
        for i, (x, y) in enumerate(zip(buckets, counts)):
            if y >= spike_threshold or i == last_positive_count_index:
                plt.annotate(y, (x, y), textcoords="offset points", xytext=(0, 5), ha='center')

    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Generate a line graph of time data from CSV files in a directory.')
    parser.add_argument('-d', '--directory', required=True, help='Directory containing CSV files')
    parser.add_argument('-c', '--column', required=True, help='Column name for time data')
    parser.add_argument('-n', '--num_buckets', type=int, default=30, help='Number of buckets')
    parser.add_argument('-s', '--bucket_size', type=int, default=24, help='Bucket size in hours')
    parser.add_argument('-m', '--mft', action='store_true')
    parser.add_argument('-a', '--autopsy_deleted', action='store_true')
    args = parser.parse_args()

    if args.directory:
        data_frames, legend_labels = process_csv_files_in_directory(args.directory, args.column, args.num_buckets, args.bucket_size, args.mft, args.autopsy_deleted)
        if data_frames and legend_labels:
            plot_access_time_count(data_frames, args.column, args.num_buckets, args.bucket_size, legend_labels)
    else:
        print("Please provide a directory with -d.")

if __name__ == '__main__':
    main()
