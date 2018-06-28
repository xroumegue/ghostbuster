#! /usr/bin/env python3
from os import scandir, linesep
from os.path import join, basename, splitext

from argparse import ArgumentParser, FileType

argparser = ArgumentParser(
    description='Scikit learn SVM spectre attack seeker')

argparser.add_argument(
    '-r',
    '--rootdir',
    type=str,
    default='reports',
    required=True,
    help='Folder collecting the reports')


args = argparser.parse_args()

csv_sep = ','

CYCLES="r11"

#
# perf stat CSV fields:
# counter value
# unit of the counter value or empty
# event name
# run time of counter
# percentage of the measurement time the counter was running
# optional variance if multiple values are collected with -r
# optional metric value
# optional unit of metric
#

dataset = {}
keys = ["timestamp", "counter", "unit", "event", "run time", "percentage", "metric", "unit metric", "NA"]
events = {}

def scan_file(filename):
    report_name = splitext(basename(filename))[0]
    print("Parsing {}".format(report_name))
    data = {}

    timestamp = None
    with open(filename, "r") as f:
        for line in f.readlines():
            if line.strip().startswith('#'):
                continue
            values = line.split(csv_sep)

            if len(values) < (len(keys) - 1):
                continue

            if timestamp and timestamp != values[0]:
                # New item
                dataset[report_name].append(data)
                data = {}

            timestamp = values[0]
            dataline = {}
            for (key, value) in (list(zip(keys,values))):
                dataline[key] = value
            if dataset.get(report_name) is None:
                dataset[report_name] = []
            data[dataline['event']] = dataline
            events[dataline["event"]] = 1
        if len(data):
            dataset[report_name].append(data)



def scandir_for_report(directory):
    print("Scanning {} for csv".format(directory))
    for item in scandir(directory):
        print("Looking at {}".format(item.name))
        if item.is_file() and item.name.endswith('.csv'):
            scan_file(item.path)
            continue
        if item.is_dir():
                scandir_for_report(item.path)

scandir_for_report(args.rootdir)

filename_out = 'dataset.txt'
fout = open(filename_out, 'w')

events_export = sorted(events)
print("Events used: {}".format(events_export))
events_export.remove(CYCLES)

fout.write("attack,"+','.join(events_export)+linesep)
for report in dataset:
    attack = "0"
    if "Spectre" in report:
        attack = "1"
    for item in dataset.get(report):
        data = []
        data.append(attack)
        cycles = int(item[CYCLES]['counter'])
        for key in events_export:
            event = item[key]
            counter = int(event['counter'])
            ratio = counter / cycles
            data.append(ratio)

        fout.write(','.join(map(str, data))+linesep)
        data = []
        data.append(attack)

