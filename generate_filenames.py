import os
import datetime
import time
import sys

"""
This script auto-updates history filenames.
    Usage: $python generate_filenames.py [pair] [path]
        i.e python generate_filenames.py btcusd /home/kiwi/history/btcusd/

    Note: does not handle row jumps!

    - read every csv file in given directory
    - call head to extract the first and second line 
        - first line used as history start date
        - first and second lines used to determine the history interval
    - call tail extract the last line
        - last line used as history end date
    - rename
"""

def create_datetime(row):
    """
    Extract datetime from given row.

    row - is a csv row
    returns datetime object
    """
    date_with_time = row.split(',')
    return datetime.datetime.strptime(date_with_time[0] + ' ' + date_with_time[1], '%Y.%m.%d %H:%M')

def generate_filenames(pair, path):
    """
    With given directory path, this function will iterate over
    each of the CSV files in that directory and will
    do the following:
        - determine history interval, 1-minute? 1-hour? etc.
        - find history range date
        - will rename the file according to the previous two steps
    """
    
    # interval in seconds and their names
    # month not included here, special case.
    # cant exactly represent month in seconds (29-31)
    intervals = {
        60: 'M1',
        300: 'M5',
        900: 'M15',
        1800: 'M30',
        3600: 'H1',
        14400: 'H4',
        86400: 'D',
        604800: 'W'
    }
    
    # get all file names
    file_list = os.listdir(path)
    
    # iterate over each file name
    for filename in file_list:
        # process only csv files
        if filename.endswith('csv'):
            # head & tail to find last and first lines of a file 
            full_path = os.path.join(path, filename)
            (first_row, second_row) = os.popen('head -n 2 {filename}'.format(filename=full_path)).read().split()
            last_row = os.popen('tail -n 1 {filename}'.format(filename=full_path)).read().strip()
            
            # create datetime objects
            first_line_date = create_datetime(first_row)
            second_line_date = create_datetime(second_row)
            last_line_date = create_datetime(last_row)

            # calculate interval by subtracting first record
            # from the second record
            interval_in_seconds = int((second_line_date - first_line_date).total_seconds())
            
            # history from and until dates
            start_date = first_line_date.strftime('%Y-%m-%d')
            end_date = last_line_date.strftime('%Y-%m-%d')
            
            # get interval name
            interval_name = ''
            if interval_in_seconds in intervals:
                interval_name = intervals[interval_in_seconds]
            else:
                # special case
                # it's 1-month interval
                interval_name = 'MN'
            
            # generate name
            pair = pair.upper()
            fnew_name = "{pair}-{interval}-{from_date}--{to_date}.csv".format(
            pair=pair,
            interval=interval_name,
            from_date=start_date,
            to_date=end_date
            )
            
            # rename file
            os.rename(full_path, os.path.join(path,fnew_name))
            
            timenow = datetime.datetime.now()
            print "{date}\n Renamed: {previous_filename} to {new_filename}. interval:{interval_name}".format(
            date=timenow, 
            previous_filename=filename, 
            new_filename=fnew_name,
            interval_name=interval_name
            )

if __name__ == '__main__':
    pair = sys.argv[1]
    path = sys.argv[2]

    generate_filenames(pair, path)