import argparse
import pandas as pd
import pytz
import matplotlib.pyplot as plt
import re
import warnings
from datetime import datetime, timedelta

def plot_access_time_count(csv_file, column_name, days_ago):
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

    # Calculate the date before the maximum time based on the specified number of days
    days_ago_date = max_time - timedelta(days=days_ago)

    # Filter the DataFrame to include only the data from the specified number of days ago
    df = df[df['UTC Time'] >= days_ago_date]

    # Create a bar graph
    day_buckets = df['UTC Time'].dt.date
    day_counts = day_buckets.value_counts().sort_index()

    # Create the bar graph
    plt.bar(day_counts.index, day_counts.values)
    plt.xlabel('Day')
    plt.ylabel('Count')
    plt.title(f'Access Time Count for the Last {days_ago} Days ({column_name})')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility

    # Add count values as labels on top of each bar
    for x, y in zip(day_counts.index, day_counts.values):
        plt.text(x, y, str(y), ha='center', va='bottom')

    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Generate a bar graph of Access Time data from a CSV file.')
    parser.add_argument('-f', '--file', required=True, help='CSV file name')
    parser.add_argument('-c', '--column', required=True, help='Column name for Access Time data')
    parser.add_argument('-d', '--days', type=int, default=30, help='Number of days before the maximum time')
    args = parser.parse_args()
    
    plot_access_time_count(args.file, args.column, args.days)

if __name__ == '__main__':
    main()
