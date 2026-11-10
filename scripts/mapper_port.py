#!/usr/bin/env python3
import sys
import csv

for row in csv.reader(sys.stdin):

    if len(row) != 49:
        continue

    dstport = row[3].strip()
    label = row[48].strip()

    if label == "1" and dstport:
        print(f"ATTACK_DEST_PORT,{dstport}\t1")

