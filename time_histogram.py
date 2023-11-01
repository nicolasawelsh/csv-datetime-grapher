import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
from dateutil import parser
import csv
import pytz
import re


# Custom tzinfos dict
tzinfos = {
    "PST": pytz.FixedOffset(-8*60),  # UTC-8 for PST
    "PDT": pytz.FixedOffset(-7*60),  # UTC-7 for PDT
    "MST": pytz.FixedOffset(-7*60),  # UTC-7 for MST
    "GMT": pytz.UTC,                 # UTC for GMT
    "UTC": pytz.UTC,                 # UTC for UTC
}


def parse_datetime(time_str, autopsy_deleted):
    if re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d+", time_str) or re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [A-Za-z]+", time_str):
        try:
            parsed_time = parser.parse(time_str, tzinfos=tzinfos)
            if autopsy_deleted:
                # Check if the parsed datetime is offset-naive (no timezone info)
                if not parsed_time.tzinfo:
                    parsed_time = parsed_time.replace(tzinfo=pytz.UTC)
                else:
                    parsed_time = parsed_time.astimezone(pytz.UTC)
            return parsed_time
        except ValueError:
            # Handle invalid or unexpected timestamp format
            return None
    else:
        return None


def generate_histogram(data, start_time, end_time, bucket_size, autopsy_deleted):
    if autopsy_deleted:
        start_time = parser.parse(start_time, tzinfos=tzinfos).astimezone(pytz.UTC)
        end_time = parser.parse(end_time, tzinfos=tzinfos).astimezone(pytz.UTC)
    else:
        start_time = parser.parse(start_time)
        end_time = parser.parse(end_time)
    num_buckets = int((end_time - start_time).total_seconds() / (bucket_size * 60))
    bins = [start_time + timedelta(minutes=i * bucket_size) for i in range(num_buckets + 1)]
    
    hist, bins = np.histogram(data, bins)

    return hist, bins


def save_to_csv(hist, bins, file_name):
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Bucket Start", "Bucket End", "Count"])
        for i in range(len(bins) - 1):
            writer.writerow([bins[i], bins[i + 1], hist[i]])


def main():
    parser = argparse.ArgumentParser(description="Generate a time histogram from a CSV file.")
    parser.add_argument("-f", "--file", help="Path to the CSV file", required=True)
    parser.add_argument("-c", "--column", help="Name of the column containing time data", required=True)
    parser.add_argument("-b", "--bucket_size", help="Bucket size in minutes", type=int, required=True)
    parser.add_argument("-s", "--start_time", help="Start time in the format '%Y-%m-%d %H:%M:%S'", required=True)
    parser.add_argument("-e", "--end_time", help="End time in the format '%Y-%m-%d %H:%M:%S'", required=True)
    parser.add_argument("-a", "--autopsy_deleted", action='store_true')
    args = parser.parse_args()

    df = pd.read_csv(args.file, usecols=[args.column])
    time_data = df[args.column].tolist()

    time_data = [parse_datetime(time_str, args.autopsy_deleted) if isinstance(time_str, str) else None for time_str in time_data]
    #print(time_data)
    time_data = [time for time in time_data if time is not None]
    hist, bins = generate_histogram(time_data, args.start_time, args.end_time, args.bucket_size, args.autopsy_deleted)

    # Save histogram data to CSV file
    save_to_csv(hist, bins, "hist.csv")

    plt.hist(bins[:-1], bins, weights=hist)
    plt.xlabel("Time")
    plt.ylabel("Count")
    plt.title(f'{args.column} Histogram For {args.file}')
    plt.xticks(rotation=45)
    plt.show()

if __name__ == "__main__":
    main()
