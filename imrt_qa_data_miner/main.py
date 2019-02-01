#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
main program for IMRT QA PDF report parser
Created on Wed Apr 18 2018
@author: Dan Cutright, PhD
"""

from imrt_qa_data_miner.qa_parser import pdf_to_qa_result
import os
import sys
from datetime import datetime


def process_data(init_directory, results_file):

    with open(results_file, "w") as csv:
        columns = ['Patient Name',
                   'Patient ID',
                   'Plan Date',
                   'Dose Type',
                   'Difference (%)',
                   'Distance (mm)',
                   'Threshold (%)',
                   'Meas Uncertainty',
                   'Use VanDyk',
                   'Analysis Type',
                   'Total Points',
                   'Passed',
                   'Failed',
                   '% Passed',
                   'Min',
                   'Max',
                   'Average',
                   'Std Dev',
                   'X offset (mm)',
                   'Y offset (mm)\n']
        csv.write(','.join(columns))

    for dirName, subdirList, fileList in os.walk(init_directory):
        for fname in fileList:
            if os.path.splitext(fname)[1].lower() == '.pdf':
                try:
                    row = pdf_to_qa_result(os.path.join(dirName, fname))
                    if row:
                        with open(results_file, "a") as csv:
                            csv.write(row + '\n')
                        print("Processed: %s" % os.path.join(dirName, fname))
                    else:
                        print("Non-compatible PDF detected: %s" % os.path.join(dirName, fname))
                except:
                    print("Non-compatible PDF detected: %s" % os.path.join(dirName, fname))


def main():

    if len(sys.argv) > 3:
        print("Too many arguments provided.")
        return

    if len(sys.argv) < 2:
        print("Please include an initial directory for scanning when calling.")
        return

    if not os.path.isdir(sys.argv[1]):
        print("Invalid directory: %s" % sys.argv[1])
        return

    init_directory = sys.argv[1]

    if len(sys.argv) == 3:
        output_file = sys.argv[2]
    else:
        output_file = "results_%s.txt" % str(datetime.now()).replace(':', '-').replace('.', '-')

    process_data(init_directory, output_file)


if __name__ == '__main__':
    main()
