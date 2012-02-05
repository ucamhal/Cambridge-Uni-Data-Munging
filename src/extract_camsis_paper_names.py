#!/usr/bin/env python

import cmdline, argparse, csv, sys

EXAM_PAPER_CODES = "H03"

def apply(func, iterable):
    for i in iterable: func(i)

class ExtractCamsisPaperNames(cmdline.CmdLineApp):
    
    def define_arguments(self, parser):
        parser.add_argument("infile", metavar="CAMSIS_CSV_FILE", 
                            type=argparse.FileType("r"))
    
    @staticmethod
    def is_paper_row(line):
        return line[0] == EXAM_PAPER_CODES

    def main(self, args):
        apply(csv.writer(sys.stdout, "excel").writerow, 
            [(line[1], line[3]) for line in csv.reader(args.infile, "excel") 
                                if self.is_paper_row(line)]) 
ExtractCamsisPaperNames(ignore_broken_pipe=True)