#!/usr/bin/env python2.7
# tripostree.py : Attempts to build a Tripos hierarchy from CamSIS data.
# 
# Copyright (C) 2012  CARET, University of Cambridge
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import OrderedDict as orddict
from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter
from operator import itemgetter
from itertools import groupby
import csv, re, json, sys

DESCRIPTION='''
Attempts to build a Tripos hierachy from the CamSIS Coding Manual data csv file.

See: http://www.admin.cam.ac.uk/offices/students/codes/
'''

# Each row in the camsis CSV file is prefixed with a code representing the type
# of data on that row. The subject/tripos-part rows are marked with this code.
TRIPOS_CODE_MARKER = "H01"

# Accept codes like: AAA, AAA00, AAA00AA (e.g. DIGIT [ NUM [ DIGIT ]] ) 
CODE_PATTERN = re.compile(r'^([A-Z]+)(?:([0-9]+)([A-Z]+)?)?$')

def extract_codes(csvfile):
    """Extracts what camsis call the the "subject" (tripos-part) codes and names
       from the camsis CSV file. A tuple of (subjectcode, subjectname) is 
       returned."""
    with csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        codes = [(line[1], line[2]) for line in reader 
                                    if line[0] == TRIPOS_CODE_MARKER]
        return sorted(codes, key=itemgetter(0))

def partition_into_triposes(matchcodes):
    return [list(group) for _, group in groupby(matchcodes, lambda x: x[0][0])]

def guess_tripos_name(bits):
    # Temporary solution, can do better
    ((_,_,_), name), = bits[0:1]
    if len(bits) == 1:
        return name
    return name.split(",")[0]

def assemble_parts(bits):
    # Partition bits by value of tripos part value
    parts = [list(g) for k, g in groupby(bits, lambda b: b[0][1])]
    
    return [assemble_part(part) for part in parts]

def assemble_part(part_bits):
    ((pref, num, suf), name) = part_bits[0]
    subjects = part_bits[1:] if suf == None else part_bits
    return orddict([
            ("name", guess_part_name(part_bits)),
            ("code", pref + (num or "")), 
            ("subjects", [assemble_subject(subject) for subject in subjects])])

def guess_part_name(bits):
    # Temporary soloution, can do better
    ((_,_,suf), name), = bits[0:1]
    if suf == None:
        return name
    return name.split(":")[0]

def assemble_subject(((pref, num, suf), name)):
    return orddict([
            ("name", guess_subject_name(name)),
            ("code", pref + num + suf)])

def guess_subject_name(name):
    return name.split(":")[1].strip() if ":" in name else name

def assemble_tripos(bits):
    assert len(bits) > 0
    return orddict([
            ("name", guess_tripos_name(bits)), 
            ("parts", assemble_parts(bits))])

def build_tree(codes):
    matches = [(code, CODE_PATTERN.match(code), name) for (code, name) in codes]
    check_for_bad_codes(matches)
    expansion = [(match.groups(), name) for (_, match, name) in matches]
    
    triposes = partition_into_triposes(expansion)
    return [assemble_tripos(tripos_bits) for tripos_bits in triposes] 
    
def check_for_bad_codes(matches):
    bad_codes = [code for (code, match,_) in matches if not match]
    if(len(bad_codes) > 0):
        raise Exception("The following codes have an unexpected format: {}"\
                        .format(bad_codes))

if __name__ == "__main__":
    parser = ArgumentParser(description=DESCRIPTION, 
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("camsis_csv", type=FileType("r"), 
                        help="The camsiscodes.csv file from the CamSIS Coding "
                        "Manual website.")
    args = parser.parse_args()
    json.dump(build_tree(extract_codes(args.camsis_csv)), sys.stdout, indent=4)