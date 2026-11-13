#!/bin/bash
# Normal vs attack classification on UNSW-NB15 with Apache Mahout
# Logistic Regression (SGD).
#
# Mahout 0.13 on the lab cluster does not include buildforest/testforest
# (Random Forest), so the trainlogistic / runlogistic programs are used.
#
# Usage (from anywhere):
#   bash scripts/run_mahout_logistic.sh [input_csv]
# Default input is the full dataset, falls back to the 5,000 row sample.

set -e
set -o pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_DIR=$(dirname "$SCRIPT_DIR")

INPUT_CSV=${1:-$HOME/network_traffic_analysis/dataset/network_traffic.csv}
if [ ! -f "$INPUT_CSV" ]; then
    echo "Full dataset not found, using sample data"
    INPUT_CSV=$PROJECT_DIR/dataset/network_traffic_sample.csv
fi

ML_DIR=$PROJECT_DIR/dataset/ml_data
MODEL_FILE=$PROJECT_DIR/models/mahout_logistic.model
RESULT_FILE=$PROJECT_DIR/results/mahout_logistic_evaluation.txt
HDFS_DIR=/user/$USER/network_traffic_analysis/ml

PREDICTORS="proto state service dur sbytes dbytes sttl dttl sloss dloss \
sload dload spkts dpkts swin dwin stcpb dtcpb smeansz dmeansz trans_depth \
res_bdy_len sjit djit sintpkt dintpkt tcprtt synack ackdat is_sm_ips_ports \
ct_state_ttl ct_flw_http_mthd is_ftp_login ct_ftp_cmd ct_srv_src ct_srv_dst \
ct_dst_ltm ct_src_ltm ct_src_dport_ltm ct_dst_sport_ltm ct_dst_src_ltm"

mkdir -p "$PROJECT_DIR/models" "$PROJECT_DIR/results"
cd "$SCRIPT_DIR"

echo "===== Step 1: Preparing train and test data ====="
echo "Input: $INPUT_CSV"
python3 prepare_ml_data.py "$INPUT_CSV" "$ML_DIR" 0.3
python3 prepare_mahout_logistic.py "$ML_DIR" "$ML_DIR"

echo "===== Step 2: Storing ML data in HDFS ====="
hdfs dfs -mkdir -p $HDFS_DIR
hdfs dfs -put -f "$ML_DIR/train_logistic.csv" $HDFS_DIR/
hdfs dfs -put -f "$ML_DIR/test_logistic.csv" $HDFS_DIR/
hdfs dfs -ls $HDFS_DIR

echo "===== Step 3: Training Mahout Logistic Regression ====="
# proto, state, service are words (w), the remaining 38 columns are numeric (n)
mahout trainlogistic \
    --input "$ML_DIR/train_logistic.csv" \
    --output "$MODEL_FILE" \
    --target label \
    --categories 2 \
    --predictors $PREDICTORS \
    --types w w w n \
    --features 200 \
    --passes 5 \
    --rate 50 \
    --lambda 0.0001 2>&1 | tee "$PROJECT_DIR/results/mahout_logistic_training.txt"

echo "===== Step 4: Testing the model ====="
{
    echo "Mahout Logistic Regression (SGD) - evaluation"
    echo "Input data   : $INPUT_CSV"
    echo "Test records : $(($(wc -l < "$ML_DIR/test_logistic.csv") - 1))"
    echo
    mahout runlogistic \
        --input "$ML_DIR/test_logistic.csv" \
        --model "$MODEL_FILE" \
        --auc \
        --confusion 2>&1
} | tee "$RESULT_FILE"

echo "===== Step 5: Updating dashboard data ====="
python3 build_dashboard_data.py

ls -l "$MODEL_FILE"
echo "Done. Results saved in results/mahout_logistic_evaluation.txt"
