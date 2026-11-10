#!/usr/bin/env python3

import sys
import csv

for row in csv.reader(sys.stdin):

    if len(row) != 49:
        continue

    srcip = row[0].strip()
    label = row[48].strip()

    if label == "1" and srcip:
        print(f"ATTACK_SOURCE,{srcip}\t1")
