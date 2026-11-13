#!/usr/bin/env python3
"""
Local Random Forest run with scikit-learn on the train/test files made by
prepare_ml_data.py. Uses the same settings as the Mahout job (50 trees,
7 features per split, seed 42) so it can be checked without a Hadoop cluster.

Usage:
    python3 prepare_ml_data.py ../dataset/network_traffic_sample.csv ../dataset/ml_data_sample
    python3 train_local_random_forest.py ../dataset/ml_data_sample ../models ../results
"""

import os
import sys

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, classification_report,
                             cohen_kappa_score, confusion_matrix)

if len(sys.argv) < 4:
    print("Usage: python3 train_local_random_forest.py <ml_data_dir> <models_dir> <results_dir>")
    sys.exit(1)

data_dir, models_dir, results_dir = sys.argv[1], sys.argv[2], sys.argv[3]

CATEGORICAL = ["proto", "state", "service"]
NUMERIC = ["f%d" % i for i in range(38)]
COLUMNS = CATEGORICAL + NUMERIC + ["label"]

train = pd.read_csv(os.path.join(data_dir, "train.csv"), header=None, names=COLUMNS)
test = pd.read_csv(os.path.join(data_dir, "test.csv"), header=None, names=COLUMNS)

# one-hot encode categorical columns, test uses the same columns as train
X_train = pd.get_dummies(train.drop(columns="label"), columns=CATEGORICAL)
X_test = pd.get_dummies(test.drop(columns="label"), columns=CATEGORICAL)
X_test = X_test.reindex(columns=X_train.columns, fill_value=0)
y_train, y_test = train["label"], test["label"]

model = RandomForestClassifier(n_estimators=50, max_features=7, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)
pred = model.predict(X_test)

labels = ["normal", "attack"]
correct = int((pred == y_test).sum())
total = len(y_test)
accuracy = accuracy_score(y_test, pred) * 100
kappa = cohen_kappa_score(y_test, pred)
cm = confusion_matrix(y_test, pred, labels=labels)

lines = [
    "Random Forest - local scikit-learn run (sample data)",
    "====================================================",
    "Train records : %d" % len(train),
    "Test records  : %d" % total,
    "Trees: 50 | Features per split: 7 | Seed: 42",
    "",
    "Correctly Classified Instances   : %d   %.4f%%" % (correct, accuracy),
    "Incorrectly Classified Instances : %d   %.4f%%" % (total - correct, 100 - accuracy),
    "Kappa : %.4f" % kappa,
    "",
    "Confusion Matrix (rows = actual, columns = predicted)",
    "%-10s %10s %10s" % ("", "normal", "attack"),
    "%-10s %10d %10d" % ("normal", cm[0][0], cm[0][1]),
    "%-10s %10d %10d" % ("attack", cm[1][0], cm[1][1]),
    "",
    classification_report(y_test, pred, labels=labels, digits=4),
]
report = "\n".join(lines)
print(report)

os.makedirs(models_dir, exist_ok=True)
os.makedirs(results_dir, exist_ok=True)

model_path = os.path.join(models_dir, "random_forest_sample_sklearn.joblib")
joblib.dump({"model": model, "columns": list(X_train.columns)}, model_path, compress=3)

with open(os.path.join(results_dir, "random_forest_sample_evaluation.txt"), "w") as f:
    f.write(report + "\n")

print("Model saved  :", model_path)
