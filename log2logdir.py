#!/usr/bin/python

# logconvert.py
# convert monolithic irssi irclogs into directory/date based logs
#
# Author: josh <josh@kaiju.net>

from datetime import datetime
import argparse
import re
import os
import sys

def recursive_mkdir(path):
    """ utility to recursively mkdir a full path """
    try:
        os.mkdir(path)
    except OSError as err:
        if err.errno is 2:
            recursive_mkdir('/'.join(path.split('/')[0:len(path.split('/'))-1]))
            recursive_mkdir(path)

def daily_log_file(directory, date):
    """ creates or appends an existing daily log file """

    if isinstance(date, datetime) == False:
        raise Exception('date should be an instance of datetime')

    basename = os.path.basename(directory)

    print "Starting new log for " + basename + " at " + date.strftime('%m-%d-%Y')

    recursive_mkdir(directory)

    log_filename = directory+'/'+date.strftime('%m-%d-%Y')+'.log'

    if os.path.isfile(log_filename) == False:
        log_file = open(log_filename, 'w')
    else:
        log_file = open(log_filename, 'r+')
        log_file.seek(0)

    return log_file

def log_to_logdir(log_file, save_path):
    """ parse an existing monolithic log and split it up into seperate daily files """

    log = open(log_file, 'r')

    date = None
    new_log = None

    print "Parsing " + log_file

    for line in log:
        dashmatch = re.match('--- (.*)', line)
        if dashmatch:

            log_opened = re.match('Log opened (.*)', dashmatch.group(1))
            if log_opened:
                opened_date = datetime.strptime(log_opened.group(1), '%a %b %d %H:%M:%S %Y')
                if date == None or date.date().isoformat() != opened_date.date().isoformat():
                    date = opened_date
                    new_log = daily_log_file(save_path, date)

            day_changed = re.match('Day changed (.*)', dashmatch.group(1))
            if day_changed:
                date = datetime.strptime(day_changed.group(1), '%a %b %d %Y')
                new_log = daily_log_file(save_path, date)

        if isinstance(new_log, file):
            new_log.write(line)

    new_log.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Convert a directory of typical monolithic irssi logs to directory/date based structure. ex: log_path/network/channel.log -> save_path/network/channel/(date).log")

    parser.add_argument('logs_path', type=str, help="Path containing monolithic log files to be converted")

    parser.add_argument('save_path', type=str, help="Path to save new log files to")

    args = parser.parse_args()

    for directory, sub_directory, log_files in os.walk(args.logs_path):
        for log_file in log_files:
            basename, ext = os.path.splitext(log_file)
            if ext == '.log':
                log_file_path = os.path.join(directory, log_file)
                save_directory = os.path.join(args.save_path, directory.replace(args.logs_path, ''), basename)
                log_to_logdir(log_file_path, save_directory)
