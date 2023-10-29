import argparse
import pandas as pd
import pytz
import matplotlib.pyplot as plt
import re
import warnings
from datetime import datetime, timedelta

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

    # Find the maximum time in the DataFrame
    max_time = df['UTC Time'].max()

    # Calculate the date before the maximum time based on the number of buckets and bucket size
    days_ago_date = max_time - timedelta(hours=num_buckets * bucket_size)

    # Filter the DataFrame to include only the data within the specified number of buckets
    df = df[df['UTC Time'] >= days_ago_date]

    # Create a line graph
    bucket_delta = timedelta(hours=bucket_size)
    bucket_end = max_time
    bucket_start = bucket_end - bucket_delta

    buckets = []
    counts = []

    while bucket_start >= days_ago_date:
        counts.append(((df['UTC Time'] >= bucket_start) & (df['UTC Time'] <= bucket_end)).sum())
        buckets.append(bucket_start)
        bucket_end = bucket_start
        bucket_start -= bucket_delta

    buckets.reverse()
    counts.reverse()

    # Create the line graph
    plt.plot(buckets, counts, marker='o', linestyle='-')
    plt.xlabel('Time')
    plt.ylabel('Count')
    plt.title(f'Access Time Count ({column_name})')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
    plt.grid(True)

    # Add count values as labels near the data points
    for x, y in zip(buckets, counts):
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
