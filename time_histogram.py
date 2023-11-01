import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil import parser
import re

def is_pst_pdt_format(time_str):
    pst_pdt_pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [A-Za-z]+")
    return bool(pst_pdt_pattern.match(time_str))

def convert_to_utc(time_str):
    print("Converting to UTC")

    if "PST" in time_str:
        offset = -8
    elif "PDT" in time_str:
        offset = -7
    elif "GMT" in time_str:
        offset = 0
    else:
        raise ValueError("Invalid timezone")
    time_obj = datetime.strptime(re.sub(r'[A-Za-z]+$', '', time_str), "%Y-%m-%d %H:%M:%S")
    return time_obj - timedelta(hours=offset)

def parse_datetime(time_str):
    try:
        return parser.parse(time_str)
    except ValueError:
        # Handle invalid or unexpected timestamp format
        return None


def generate_histogram(data, start_time, end_time, bucket_size):
    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    num_buckets = int((end_time - start_time).total_seconds() / (bucket_size * 60))
    bins = [start_time + timedelta(minutes=i * bucket_size) for i in range(num_buckets + 1)]
    
    hist, bins = np.histogram(data, bins)
    return hist, bins

def main():
    parser = argparse.ArgumentParser(description="Generate a time histogram from a CSV file.")
    parser.add_argument("-f", "--file", help="Path to the CSV file", required=True)
    parser.add_argument("-c", "--column", help="Name of the column containing time data", required=True)
    parser.add_argument("-b", "--bucket_size", help="Bucket size in minutes", type=int, required=True)
    parser.add_argument("-s", "--start_time", help="Start time in the format '%Y-%m-%d %H:%M:%S'", required=True)
    parser.add_argument("-e", "--end_time", help="End time in the format '%Y-%m-%d %H:%M:%S'", required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.file, usecols=[args.column])
    time_data = df[args.column].tolist()

    time_data = [convert_to_utc(time_str) if is_pst_pdt_format(time_str) else parse_datetime(time_str) for time_str in time_data]
    #print(time_data)
    time_data = [time for time in time_data if time is not None]
    #print(time_data)
    hist, bins = generate_histogram(time_data, args.start_time, args.end_time, args.bucket_size)

    plt.hist(bins[:-1], bins, weights=hist)
    plt.xlabel("Time")
    plt.ylabel("Count")
    plt.title(f'{args.column} Histogram For {args.file}')
    plt.xticks(rotation=45)
    plt.show()

if __name__ == "__main__":
    main()
