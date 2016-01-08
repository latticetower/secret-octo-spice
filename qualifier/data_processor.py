#!/usr/bin/env python

from readfq import readfq, FastqRecord
from itertools import imap
import math

import gzip, re
import matplotlib.pyplot as plt
import numpy as np
import gzip
from contextlib import contextmanager
import os.path

@contextmanager
def open_gz_or_fastq(filename):
    extension = os.path.splitext(filename)[1]
    if extension == ".fastq":
        f = open(filename, 'rb')
        try:
            yield f
        finally:
            f.close()
    if extension == ".gz":
        f = gzip.open(filename, 'rb')
        try:
            yield f
        finally:
            f.close()

class DataProcessor():
    def __init__(self, input_file_name, output_file_name):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name

    def process(self):
        print("ff")
        records = {}
        regex = re.compile("([^: ]+)")
        with open_gz_or_fastq(self.input_file_name) as input_file:
            for name, seq, qual in readfq(input_file):
                name_parts = regex.findall(name)
                if not (name_parts[4] in records):
                    records[name_parts[4]] = []
                #print qual
                record = tuple(map(ord, qual))
                records[name_parts[4]].append(record)
        processed_records = {}
        processed_counts = {}
        for k in records:
            v = records[k]
            processed_records[k] = list(imap(lambda *x: float(sum(x)), *v))
            processed_counts[k] = list(imap(lambda *x: len(x), *v))
            #print list(processed_records[k])
        total_sums = list(imap(lambda *x: sum(x), *processed_records.values()))
        total_counts = list(imap(lambda *x: max(sum(x), 1), *processed_counts.values()))
        total_means = list(imap(lambda x, y: x / y, total_sums, total_counts))
        processed_means = np.array([ list(imap(lambda x, y, c: max(x / max(y, 1) - c, 0), processed_records[k], processed_counts[k], total_means))for k in processed_records.keys()])
        #print processed_means
        print total_means
        #print(len(total_means))
        plt.pcolor(processed_means)
        plt.xticks(xrange(1,len(total_means)+1))
        plt.yticks(xrange(len(processed_records.keys())), map(int, processed_records.keys()))
        plt.show()
