#!/usr/bin/python3

import argparse
import re


def shortestString(x):
    f = float(x)
    if abs(f) <  0.00001:
        return("0")
    else:
        return(str(f))

parser = argparse.ArgumentParser(
        description='shorten bvh file and change z coordinate of root')
parser.add_argument('-z', default=0.0, type=float, help='change of z coordinate (negative => down)')
parser.add_argument('inputfile', type=str, help='unchanged bvh-file')
parser.add_argument('outputfile', type=str, help='changed bvh-file')

args = parser.parse_args()

with open(args.inputfile) as f:
    try:
        out= open(args.outputfile, "w")
    except:
        print ("Cannot write:" + args.outputfile)
        exit (20)
    #
    # handle HIERARCHY
    #
    for line in f:
        out.write(line)
        m=re.search("^\s*MOTION", line)
        if m:
            break

    for line in f:
        m=re.search("^\s*Frame", line)
        if m:
            out.write(line)
            continue

        columns = [shortestString(x) for x in line.split()]
        if args.z != 0.0:
            columns[2] = "{z:.5f}".format(z=float(columns[2]) + args.z)
        newline = ' '.join(columns) + "\n"
        out.write(newline)

    out.close()
    exit(0)
