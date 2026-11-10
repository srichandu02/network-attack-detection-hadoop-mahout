#!/bin/bash
# Attack classification on UNSW-NB15 using Apache Mahout Random Forest
# Run from the scripts/ folder:  bash run_mahout_random_forest.sh

set -e

PROJECT_DIR=~/network_traffic_analysis
INPUT_CSV=$PROJECT_DIR/dataset/network_traffic.csv
LOCAL_ML_DIR=$PROJECT_DIR/dataset/ml_data
HDFS_DIR=/user/$USER/network_traffic_analysis/ml

NUM_TREES=50
FEATURES_PER_NODE=7      # about sqrt(41 features)

echo "===== Step 1: Preparing train and test data ====="
python3 prepare_ml_data.py $INPUT_CSV $LOCAL_ML_DIR 0.3

echo "===== Step 2: Uploading data to HDFS ====="
hdfs dfs -rm -r -f $HDFS_DIR
hdfs dfs -mkdir -p $HDFS_DIR
hdfs dfs -put $LOCAL_ML_DIR/train.csv $HDFS_DIR/train.csv
hdfs dfs -put $LOCAL_ML_DIR/test.csv $HDFS_DIR/test.csv
hdfs dfs -ls $HDFS_DIR

echo "===== Step 3: Describing dataset (3 categorical, 38 numeric, 1 label) ====="
mahout describe \
    -p $HDFS_DIR/train.csv \
    -f $HDFS_DIR/train.info \
    -d 3 C 38 N L

echo "===== Step 4: Training Random Forest ($NUM_TREES trees) ====="
mahout buildforest \
    -Dmapred.max.split.size=10000000 \
    -d $HDFS_DIR/train.csv \
    -ds $HDFS_DIR/train.info \
    -sl $FEATURES_PER_NODE \
    -p \
    -t $NUM_TREES \
    -o $HDFS_DIR/forest

echo "===== Step 5: Testing Random Forest ====="
mahout testforest \
    -i $HDFS_DIR/test.csv \
    -ds $HDFS_DIR/train.info \
    -m $HDFS_DIR/forest \
    -a \
    -mr \
    -o $HDFS_DIR/predictions 2>&1 | tee $PROJECT_DIR/results/random_forest_evaluation.txt

echo "===== Step 6: Saving model locally ====="
rm -rf $PROJECT_DIR/models/random_forest
hdfs dfs -get $HDFS_DIR/forest $PROJECT_DIR/models/random_forest
ls -l $PROJECT_DIR/models/random_forest

echo "Done. Accuracy and confusion matrix saved in results/random_forest_evaluation.txt"
