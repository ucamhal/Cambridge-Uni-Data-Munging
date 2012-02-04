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
    keyfunc = lambda c: c[0].getTripos()
    return [Tripos(list(group)) for _, group in groupby(matchcodes, keyfunc)]

def build_tree(codes):
    matches = [(Code(code), name) for (code, name) in codes]
    
    triposes = partition_into_triposes(matches)
    return triposes 

class Code(object):
    def __init__(self, code):
        match = CODE_PATTERN.match(code)
        assert match
        self._tripos, self._part, self._subject = match.groups()
        assert self._tripos
    
    def getTripos(self): return self._tripos
    def getPart(self): return self._part
    def getSubject(self): return self._subject
    
    def getTriposPart(self):
        return self._tripos + (self._part or "")
    
    def __tojson__(self):
        return str(self)
    
    def __repr__(self):
        return self._tripos + (self._part or "") + (self._subject or "")

class Tripos(object):
    def __init__(self, tripos_bits):
        self._bits = tripos_bits
        self._parts = [Part(self, list(g)) for _,g 
                       in groupby(self._bits, lambda b: b[0].getPart())]
    
    def getName(self):
        # Temporary solution, can do better
        (_, name), = self._bits[0:1]
        if len(self._bits) == 1:
            return name
        return name.split(",")[0]
    
    def __tojson__(self):
        return orddict([
                ("name", self.getName()),
                ("parts", self._parts)])

class Part(object):
    def __init__(self, tripos, part_bits):
        self._tripos = tripos
        self._bits = part_bits
        self._subjects = [Subject(self, bit) for bit in self._bits 
                                             if bit[0].getSubject()]
    
    def getName(self):
        return self._bits[0][1]
    
    def getCode(self):
        return self._bits[0][0]
    
    def __tojson__(self):
        return orddict([
            ("name", self.getName()),
            ("code", self.getCode().getTriposPart()), 
            ("subjects", self._subjects)])

class Subject(object):
    def __init__(self, part, subject_bit):
        self._part = part
        (self._code, self._name) = subject_bit
    
    def __tojson__(self):
        return orddict([
                ("rawname", self._name),
                ("code", self._code)])

class Encoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, "__tojson__"):
            return o.__tojson__()
        return json.JSONEncoder.default(self, o)

if __name__ == "__main__":
    parser = ArgumentParser(description=DESCRIPTION, 
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("camsis_csv", type=FileType("r"), 
                        help="The camsiscodes.csv file from the CamSIS Coding "
                        "Manual website.")
    args = parser.parse_args()
    triposes = build_tree(extract_codes(args.camsis_csv))
    json.dump(triposes, sys.stdout, indent=4, cls=Encoder)