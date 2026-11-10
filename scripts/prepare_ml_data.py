#!/usr/bin/env python3
"""
Prepare UNSW-NB15 records for Mahout Random Forest.

- keeps protocol, state, service as categorical features
- keeps the numeric traffic features
- drops IPs, ports, timestamps and attack_cat (attack_cat would leak the answer)
- converts Label 0/1 to normal/attack
- splits data into train and test files

Usage:
    python3 prepare_ml_data.py <input.csv> <output_dir> [test_ratio]
"""

import sys
import csv
import os
import random

if len(sys.argv) < 3:
    print("Usage: python3 prepare_ml_data.py <input.csv> <output_dir> [test_ratio]")
    sys.exit(1)

input_file = sys.argv[1]
output_dir = sys.argv[2]
test_ratio = float(sys.argv[3]) if len(sys.argv) > 3 else 0.3

# column positions in the original 49 column file
CATEGORICAL_COLS = [4, 5, 13]                    # proto, state, service
NUMERIC_COLS = (list(range(6, 13))               # dur .. dloss
                + list(range(14, 28))            # Sload .. Djit
                + list(range(30, 47)))           # Sintpkt .. ct_dst_src_ltm
LABEL_COL = 48

random.seed(42)
os.makedirs(output_dir, exist_ok=True)

train_out = open(os.path.join(output_dir, "train.csv"), "w", newline="")
test_out = open(os.path.join(output_dir, "test.csv"), "w", newline="")
train_writer = csv.writer(train_out)
test_writer = csv.writer(test_out)

counts = {"train": 0, "test": 0, "skipped": 0, "normal": 0, "attack": 0}


def to_number(value):
    value = value.strip()
    if value == "" or value == "-":
        return "0"
    try:
        float(value)
        return value
    except ValueError:
        return "0"


with open(input_file, encoding="utf-8-sig", errors="ignore") as f:
    for row in csv.reader(f):

        if len(row) != 49:
            counts["skipped"] += 1
            continue

        label = row[LABEL_COL].strip()
        if label not in ("0", "1"):
            counts["skipped"] += 1
            continue

        record = []
        for c in CATEGORICAL_COLS:
            value = row[c].strip().lower()
            record.append(value if value else "-")

        for c in NUMERIC_COLS:
            record.append(to_number(row[c]))

        if label == "1":
            record.append("attack")
            counts["attack"] += 1
        else:
            record.append("normal")
            counts["normal"] += 1

        if random.random() < test_ratio:
            test_writer.writerow(record)
            counts["test"] += 1
        else:
            train_writer.writerow(record)
            counts["train"] += 1

train_out.close()
test_out.close()

print("Normal records  :", counts["normal"])
print("Attack records  :", counts["attack"])
print("Train records   :", counts["train"])
print("Test records    :", counts["test"])
print("Skipped rows    :", counts["skipped"])
print("Features        :", len(CATEGORICAL_COLS), "categorical +", len(NUMERIC_COLS), "numeric")
print("Mahout descriptor: %d C %d N L" % (len(CATEGORICAL_COLS), len(NUMERIC_COLS)))
