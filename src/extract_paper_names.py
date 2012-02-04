#!/usr/bin/env python2.7
HELP=\
"""Reads the Exam Papers SQL dump, extracting a CSV list of ID,PaperName.
There is an example of such a dump in this repository at 
data/exam-papers-dump.sql

Example:

$ src/extract_paper_names.py data/exam-papers-dump.sql | head -n 5
1,England Before The Norman Conquest
2,Scandinavian History In The Viking Age
3,The Brittonic-Speaking Peoples From the Fourth Century To The Twelfth
4,The Gaelic-speaking peoples from the Fourth century to the Twelfth
5,Old English language and literature
"""

from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter
import csv, sys, errno

PREFIX = "INSERT INTO `ref_paper` VALUES("

def is_data_line(line):
    return line.startswith(PREFIX)

def extract_data(line):
    return line[len(PREFIX):-3]

def parse_input(file):
    lines = [extract_data(line) for line in file if is_data_line(line)]
    csv.register_dialect('sequel', quotechar="'", delimiter=",", 
                         skipinitialspace=True)
    return [(line[0], line[4]) for line in csv.reader(lines, 'sequel')]
    
def write_output(parsed_lines):
    map(csv.writer(sys.stdout).writerow, parsed_lines)

def parse_args():
    parser = ArgumentParser(description=HELP, 
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("infile", type=FileType("r"), help="e.g. data/exam-papers-dump.sql")
    return parser.parse_args()

if __name__ == "__main__":
    data = parse_input(parse_args().infile)
    try:
        write_output(data)
    except IOError, e:
        if e.errno == errno.EPIPE:
            exit(0)
        raise
