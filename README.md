# csv-datetime-grapher

# Time Histogram Generator

The Time Histogram Generator is a Python script that reads a CSV file containing timestamps, processes the data, and generates a time histogram. The script allows you to specify various parameters like the column containing time data, bucket size, start time, and end time.

## Requirements

To run this script, you need to have the following libraries installed:

- `pandas`: Data manipulation and analysis library.
- `numpy`: Library for numerical computations.
- `matplotlib`: Plotting library.
- `pytz`: Timezone library.
- `dateutil`: Provides extensions to the standard datetime module.

You can install these libraries using `pip`. For example:

```
pip install pandas numpy matplotlib pytz python-dateutil
```

# Usage

To use the Time Histogram Generator script, follow these steps:

### 1. Clone the Repository:

Clone this GitHub repository to your local machine or download the script.

### 2. Run the Script:

Execute the script with the following command:

```
python time-histogram.py -f input.csv -c timestamp_column -b bucket_size -s start_time -e end_time [-a]
```

Replace the following placeholders:
- input.csv: The path to your CSV file.
- timestamp_column: The name of the column containing the timestamp data.
- bucket_size: The desired bucket size in minutes.
- start_time: The start time in the format '%Y-%m-%d %H:%M:%S'.
- end_time: The end time in the format '%Y-%m-%d %H:%M:%S'.
- You can include the -a option to handle timestamps with timezone information in the format '%Y-%m-%d %H:%M:%S %Z', otherwise timestamps will be of the format '%Y-%m-%d %H:%M:%S.%f'.


### 3. View the Histogram:

The script will display a histogram plot and save the histogram data in a CSV file named hist.csv.

# Example

Here's an example command to run the script:

```
python time-histogram.py -f autopsy_deleted_files.csv -c "Access Time" -b 60 -s "2023-01-01 00:00:00" -e "2023-01-02 00:00:00" -a
```

This will generate a time histogram for the "timestamp" column in the "data.csv" file, with a bucket size of 30 minutes, covering the date range from January 1, 2023, to January 2, 2023, considering timestamps with timezone information.

# License

This script is provided under the MIT License. See the LICENSE file for details.















