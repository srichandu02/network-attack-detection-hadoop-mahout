#!/usr/bin/env python3
import sys
import csv

for row in csv.reader(sys.stdin):

    if len(row) != 49:
        continue

    service = row[13].strip()
    label = row[48].strip()

    if label == "1":
        if not service or service == "-":
            service = "unknown"

        print(f"ATTACK_SERVICE,{service}\t1")
