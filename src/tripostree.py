#!/usr/bin/env python
'''
@author: Hal Blackburn
'''

from argparse import ArgumentParser, FileType
import csv

# Each row in the camsis CSV file is prefixed with a code representing the type
# of data on that row. The subject/tripos-part rows are marked with this code.
TRIPOS_CODE_MARKER = "H01"

def extract_codes(csvfile):
    """Extracts what camsis call the the "subject" (tripos-part) codes and names
       from the camsis CSV file. A tuple of (subjectcode, subjectname) is 
       returned."""
    with csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        return [(line[1], line[2]) for line in reader 
                                   if line[0] == TRIPOS_CODE_MARKER]

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("camsis_csv", type=FileType("r"))
    args = parser.parse_args()
    print extract_codes(args.camsis_csv)