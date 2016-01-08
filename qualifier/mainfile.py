#!/usr/bin/env python

import subprocess, sys
from data_processor import DataProcessor

from optparse import OptionParser


def main(input_file_name, output_file_name):
    result = 0
    if not input_file_name:
        print >> sys.stderr, "input_file_name was not provided"
        result = 1
    if not output_file_name:
        print >> sys.stderr, "output_file_name was not provided"
        result = 1
    if result:
        return result
    DataProcessor(input_file_name, output_file_name).process()
    print("--------\ndata processed")
    return result

def parse_args():
    parser = OptionParser()
    parser.add_option("-i", "--input", dest = "input_file_name",
      help = "input FILE in .fastq or fastq.gz format", metavar = "FILE")
    parser.add_option("-o", "--output", dest = "output_file_name",
      help = "output FILE for saving the results", metavar = "FILE")
    (options, args) = parser.parse_args()
    result = main(options.input_file_name, options.output_file_name)
    if result:
        parser.print_help()

if __name__ == "__main__":
     parse_args()
