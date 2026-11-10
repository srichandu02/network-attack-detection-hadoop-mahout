#!/usr/bin/env python3

import sys
import csv

for row in csv.reader(sys.stdin):

    if len(row) != 49:
        continue

    srcip = row[0]
    protocol = row[4]
    attack_cat = row[47].strip()
    label = row[48].strip()

    # Classify normal and attack traffic
    if label == "0":
        print("LABEL,Normal\t1")

    elif label == "1":
        print("LABEL,Attack\t1")

        if attack_cat and attack_cat != "-":
            print(f"ATTACK_CATEGORY,{attack_cat}\t1")
        else:
            print("ATTACK_CATEGORY,Unknown\t1")

    # Count network protocols
    if protocol:
        print(f"PROTOCOL,{protocol}\t1")
