import pandas as pd
import pytz
import matplotlib.pyplot as plt
import re
import warnings
from datetime import datetime, timedelta

# Suppress warnings related to unused columns
warnings.filterwarnings("ignore", message="Columns.*not found in file")

# Read the CSV data from a file, selecting only the "Access Time" column
df = pd.read_csv("003_all_deleted.csv", usecols=["Access Time"])

# Define a regular expression pattern for the expected format
valid_time_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [A-Za-z]+"

# Filter out rows with invalid "Access Time" format
df = df[df['Access Time'].str.match(valid_time_pattern, na=False)]

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

# Apply the conversion function to the 'Access Time' column
df['UTC Time'] = df['Access Time'].apply(convert_to_utc)

# Find the maximum "Access Time" in the DataFrame
max_access_time = df['UTC Time'].max()

# Calculate the date 30 days before the maximum "Access Time"
thirty_days_ago = max_access_time - timedelta(days=30)

# Filter the DataFrame to include only the data from the last 30 days
df = df[df['UTC Time'] >= thirty_days_ago]

# Create a bar graph
day_buckets = df['UTC Time'].dt.date
day_counts = day_buckets.value_counts().sort_index()

# Create the bar graph
plt.bar(day_counts.index, day_counts.values)
plt.xlabel('Day')
plt.ylabel('Count')
plt.title('Access Time Count for the Last 30 Days')
plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility

# Add count values as labels on top of each bar
for x, y in zip(day_counts.index, day_counts.values):
    plt.text(x, y, str(y), ha='center', va='bottom')

plt.show()
