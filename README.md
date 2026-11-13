# Large-Scale Network Traffic Analysis for Attack Pattern Detection Using Hadoop

## 1. Project Overview

This project focuses on analyzing large-scale network traffic data using Apache Hadoop and MapReduce to identify suspicious network activities and potential cyberattacks.

The system processes network traffic records and identifies suspicious patterns such as:
- High traffic from a single source IP.
- Frequently targeted destination ports.
- Repeated connection requests.
- Unusual network service activity.
- Potential Denial-of-Service (DoS) patterns.

It also trains machine learning models (Logistic Regression with Apache Mahout and Random Forest with scikit-learn) to classify each network record as **normal** or **attack**.

## 2. Objectives

- Analyze network traffic records using Hadoop.
- Process large datasets using MapReduce.
- Identify suspicious source IP addresses.
- Analyze frequently targeted network services.
- Identify commonly attacked destination ports.
- Generate summarized attack analysis reports.
- Classify network traffic as normal or attack using machine learning.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Linux | Operating system |
| Apache Hadoop 3.3.6 | Distributed data processing |
| HDFS | Distributed file storage |
| MapReduce | Parallel data processing |
| Apache Mahout 0.13 | Machine learning (Logistic Regression, SGD) |
| scikit-learn | Random Forest classifier |
| Python 3 | Mapper / Reducer scripts and data preparation |
| Java 11 | Hadoop execution environment |
| UNSW-NB15 | Network intrusion detection dataset |

## 4. Project Structure

```text
network-attack-detection-hadoop-mahout/
│
├── dataset/
│   ├── NUSW-NB15_features.csv
│   └── network_traffic_sample.csv
│
├── dashboard/
│   ├── index.html
│   └── data.js
│
├── documentation/
│   └── screenshots/
│
├── models/
│   ├── random_forest_sample_sklearn.joblib
│   └── mahout_logistic.model              (created by run_mahout_logistic.sh)
│
├── results/
│   ├── attack_sources.txt
│   ├── attack_services.txt
│   ├── top_10_attack_sources.txt
│   ├── attack_destination_ports.txt
│   ├── traffic_summary_sample.txt
│   ├── random_forest_sample_evaluation.txt
│   └── mahout_logistic_evaluation.txt     (created by run_mahout_logistic.sh)
│
├── scripts/
│   ├── mapper.py
│   ├── reducer.py
│   ├── mapper_ip.py
│   ├── mapper_port.py
│   ├── mapper_service.py
│   ├── prepare_ml_data.py
│   ├── prepare_mahout_logistic.py
│   ├── run_mahout_logistic.sh
│   ├── train_local_random_forest.py
│   └── build_dashboard_data.py
│
└── README.md
```

## 5. Dataset Description

The project uses the UNSW-NB15 network intrusion detection dataset (UNSW Canberra Cyber).

The dataset contains network traffic information used for analyzing normal and suspicious network activities.

Important attributes include:
- Source IP address
- Destination IP address
- Source port
- Destination port
- Protocol
- Network service
- Packet information
- Traffic volume
- Attack category

## 6. Implementation

The project uses Hadoop MapReduce to process network traffic records.

### Mapper Phase

The mapper scripts read network traffic records and generate intermediate key-value pairs based on selected network attributes.

### Reducer Phase

The reducer receives intermediate key-value pairs, groups records by key, and calculates aggregated counts.

### Analysis

The project performs:
1. Source IP analysis.
2. Destination port analysis.
3. Network service analysis.
4. Top 10 suspicious source IP analysis.

## 7. Machine Learning

| Item | Details |
|---|---|
| ML problem type | Classification (binary: normal / attack) |
| Target column | `Label` (0 = normal, 1 = attack) |
| Models | Logistic Regression (Apache Mahout, SGD), Random Forest (scikit-learn) |
| Train / test split | 70% / 30% (random, seed 42) |
| Features | 41 (3 categorical + 38 numeric) |

### Features used

- Categorical: `proto`, `state`, `service`
- Numeric: duration, bytes, TTL values, packet loss, load, packet counts, TCP window and sequence values, mean packet size, jitter, inter-packet time, TCP round-trip times and the connection count features (`ct_*`).

Source/destination IPs, ports and timestamps are removed so the models learn traffic behaviour instead of memorising addresses. `attack_cat` is also removed because it directly gives away the label.

### Model 1: Logistic Regression with Apache Mahout

The lab cluster runs Mahout 0.13. `mahout describe` works there, but `buildforest` / `testforest` (Random Forest) are not part of that build, so the Mahout model uses `trainlogistic` / `runlogistic` (Logistic Regression trained with stochastic gradient descent).

Steps (`scripts/run_mahout_logistic.sh`):

1. `prepare_ml_data.py` cleans the records, converts the label to `normal` / `attack` and splits the data into train and test sets.
2. `prepare_mahout_logistic.py` adds a header row and scales the numeric columns (log + min-max, using training data only).
3. The prepared files are stored in HDFS.
4. `mahout trainlogistic` trains the model (5 passes, 200 hashed features).
5. `mahout runlogistic` tests the model and prints AUC and the confusion matrix.
6. The dashboard data is refreshed.

```bash
cd ~/network-attack-detection-hadoop-mahout
bash scripts/run_mahout_logistic.sh                    # full dataset
bash scripts/run_mahout_logistic.sh dataset/network_traffic_sample.csv   # sample
```

Output: `results/mahout_logistic_evaluation.txt`, model: `models/mahout_logistic.model`.

#### Results (sample data, Mahout 0.13 local mode)

Mahout `trainlogistic` / `runlogistic` were run in local mode (Mahout 0.13.0 job jar, Java 11) on `network_traffic_sample.csv`, same 70/30 split:

| Metric | Value |
|---|---|
| Test records | 1,492 |
| Accuracy | 99.06% (1,478 correct, 14 wrong) |
| AUC | 1.00 |
| Attacks detected | 57 / 61 (93.4% recall) |
| Normal records flagged as attack | 10 / 1,431 |

Report: `results/mahout_logistic_evaluation.txt` · Training output with learned weights: `results/mahout_logistic_training.txt`

### Model comparison

| Model | Platform | Accuracy | Attack recall |
|---|---|---|---|
| **Random Forest** | scikit-learn | **99.93%** | **100%** |
| Logistic Regression | Apache Mahout (SGD) | 99.06% | 93.4% |

**Best performing model: Random Forest.** Both models were tested on the same 1,492 sample records.

### Model 2: Random Forest with scikit-learn (sample data)

Random Forest with 50 trees and 7 features per split, run on `network_traffic_sample.csv` (5,000 records):

```bash
cd scripts
python3 prepare_ml_data.py ../dataset/network_traffic_sample.csv ../dataset/ml_data_sample
python3 train_local_random_forest.py ../dataset/ml_data_sample ../models ../results
```

| Metric | Value |
|---|---|
| Test records | 1,492 |
| Accuracy | 99.93% (1,491 correct, 1 wrong) |
| Kappa | 0.9915 |
| Attack recall | 100% (61 / 61) |
| Attack precision | 98.39% |

Model: `models/random_forest_sample_sklearn.joblib` · Report: `results/random_forest_sample_evaluation.txt`

## 8. Results

| Output File | Description |
|---|---|
| attack_sources.txt | Source IP analysis |
| attack_services.txt | Network service analysis |
| top_10_attack_sources.txt | Top 10 source IPs |
| attack_destination_ports.txt | Destination port analysis |
| traffic_summary_sample.txt | Normal/attack, attack category and protocol counts (`mapper.py` + `reducer.py` on the sample) |
| random_forest_sample_evaluation.txt | Random Forest results on the 5,000-record sample |
| mahout_logistic_evaluation.txt | Mahout Logistic Regression AUC and confusion matrix |
| mahout_logistic_training.txt | Mahout Logistic Regression training output and learned weights |

### Dashboard

An interactive dashboard (`dashboard/index.html`) shows the result files: attacked ports, services, source IP frequency, traffic summary, model comparison and a searchable results explorer with CSV download.

```bash
# refresh dashboard data after adding new result files
python3 scripts/build_dashboard_data.py
```

Open `dashboard/index.html` in a browser, or enable GitHub Pages for the repository and open `/dashboard/`.

## 9. Screenshots

Execution screenshots (Hadoop jobs, HDFS directories, Mahout runs) are available in:

`documentation/screenshots/`

## 10. Conclusion

This project demonstrates how Apache Hadoop and MapReduce can be used to analyze network traffic data at scale.

By aggregating network traffic information based on source IP addresses, destination ports, and services, the system helps identify potentially suspicious network activity and supports basic network security analysis. The machine learning models extend this by automatically classifying network records as normal or attack traffic.

## 11. Future Enhancements

- Real-time network traffic monitoring.
- Multi-class classification of attack categories (DoS, Exploits, Fuzzers, etc.).
- Detection of unusual request bursts using time-window analysis.
- Automated suspicious activity alerts.
- Integration with additional intrusion detection datasets.
