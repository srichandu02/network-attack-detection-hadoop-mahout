#!/usr/bin/env python3
"""
Turns the train.csv / test.csv made by prepare_ml_data.py into the format
Mahout trainlogistic / runlogistic expects:

- adds a header row (Mahout picks predictors by column name)
- applies log(1 + x) and min-max scaling to numeric columns using the
  training data only, because SGD logistic regression is sensitive to
  large values like bytes and TCP sequence numbers

Usage:
    python3 prepare_mahout_logistic.py <ml_data_dir> <output_dir>
"""

import sys
import os
import csv
import math

if len(sys.argv) < 3:
    print("Usage: python3 prepare_mahout_logistic.py <ml_data_dir> <output_dir>")
    sys.exit(1)

data_dir, output_dir = sys.argv[1], sys.argv[2]

HEADER = [
    "proto", "state", "service",
    "dur", "sbytes", "dbytes", "sttl", "dttl", "sloss", "dloss",
    "sload", "dload", "spkts", "dpkts", "swin", "dwin", "stcpb", "dtcpb",
    "smeansz", "dmeansz", "trans_depth", "res_bdy_len", "sjit", "djit",
    "sintpkt", "dintpkt", "tcprtt", "synack", "ackdat", "is_sm_ips_ports",
    "ct_state_ttl", "ct_flw_http_mthd", "is_ftp_login", "ct_ftp_cmd",
    "ct_srv_src", "ct_srv_dst", "ct_dst_ltm", "ct_src_ltm",
    "ct_src_dport_ltm", "ct_dst_sport_ltm", "ct_dst_src_ltm",
    "label",
]
NUM_START, NUM_END = 3, 41          # numeric columns are 3..40


def log_value(text):
    try:
        return math.log1p(max(float(text), 0.0))
    except ValueError:
        return 0.0


# pass 1: min and max of every numeric column in the training data
mins = [float("inf")] * len(HEADER)
maxs = [float("-inf")] * len(HEADER)
with open(os.path.join(data_dir, "train.csv")) as f:
    for row in csv.reader(f):
        for i in range(NUM_START, NUM_END):
            v = log_value(row[i])
            if v < mins[i]:
                mins[i] = v
            if v > maxs[i]:
                maxs[i] = v


def convert(src, dst):
    count = 0
    with open(src) as fin, open(dst, "w", newline="") as fout:
        writer = csv.writer(fout)
        writer.writerow(HEADER)
        for row in csv.reader(fin):
            out = row[:NUM_START]
            for i in range(NUM_START, NUM_END):
                spread = maxs[i] - mins[i]
                v = (log_value(row[i]) - mins[i]) / spread if spread > 0 else 0.0
                out.append("%.6f" % min(max(v, 0.0), 1.0))
            out.append(row[-1])
            writer.writerow(out)
            count += 1
    return count


os.makedirs(output_dir, exist_ok=True)
n_train = convert(os.path.join(data_dir, "train.csv"), os.path.join(output_dir, "train_logistic.csv"))
n_test = convert(os.path.join(data_dir, "test.csv"), os.path.join(output_dir, "test_logistic.csv"))

print("train_logistic.csv :", n_train, "records")
print("test_logistic.csv  :", n_test, "records")
