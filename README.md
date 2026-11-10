# Large-Scale Network Traffic Analysis for Attack Pattern Detection Using Hadoop

## 1. Project Overview

This project focuses on analyzing large-scale network traffic data using Apache Hadoop and MapReduce to identify suspicious network activities and potential cyberattacks.

The system processes network traffic records and identifies suspicious patterns such as:
- High traffic from a single source IP.
- Frequently targeted destination ports.
- Repeated connection requests.
- Unusual network service activity.
- Potential Denial-of-Service (DoS) patterns.

It also trains a machine learning model (Random Forest using Apache Mahout) to classify each network record as **normal** or **attack**.

## 2. Objectives

- Analyze network traffic records using Hadoop.
- Process large datasets using MapReduce.
- Identify suspicious source IP addresses.
- Analyze frequently targeted network services.
- Identify commonly attacked destination ports.
- Generate summarized attack analysis reports.
- Classify network traffic as normal or attack using Mahout Random Forest.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Linux | Operating system |
| Apache Hadoop 3.3.6 | Distributed data processing |
| HDFS | Distributed file storage |
| MapReduce | Parallel data processing |
| Apache Mahout | Machine learning (Random Forest classifier) |
| Python 3 | Mapper and Reducer scripts |
| Java 11 | Hadoop execution environment |
| UNSW-NB15 | Network intrusion detection dataset |

## 4. Project Structure

```text
network_traffic_analysis_github/
│
├── dataset/
│   ├── NUSW-NB15_features.csv
│   └── network_traffic_sample.csv
│
├── documentation/
│   └── screenshots/
│
├── models/
│   └── random_forest/        (saved after running the model)
│
├── results/
│   ├── attack_sources.txt
│   ├── attack_services.txt
│   ├── top_10_attack_sources.txt
│   ├── attack_destination_ports.txt
│   └── random_forest_evaluation.txt   (created after running the model)
│
├── scripts/
│   ├── mapper.py
│   ├── reducer.py
│   ├── mapper_ip.py
│   ├── mapper_port.py
│   ├── mapper_service.py
│   ├── prepare_ml_data.py
│   └── run_mahout_random_forest.sh
│
└── README.md
```

## 5. Dataset Description

The project uses the UNSW-NB15 network intrusion detection dataset.

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

## 7. Machine Learning using Apache Mahout

| Item | Details |
|---|---|
| ML problem type | Classification (binary: normal / attack) |
| Target column | `Label` (0 = normal, 1 = attack) |
| ML model used | Random Forest (Apache Mahout, MapReduce) |
| Best performing model | Random Forest |
| Train / test split | 70% / 30% (random, seed 42) |
| Number of trees | 50 |
| Features | 41 (3 categorical + 38 numeric) |

### Features used

- Categorical: `proto`, `state`, `service`
- Numeric: duration, bytes, TTL values, packet loss, load, packet counts, TCP window and sequence values, mean packet size, jitter, inter-packet time, TCP round-trip times and the connection count features (`ct_*`).

Source/destination IPs, ports and timestamps are removed so the model learns traffic behaviour instead of memorising addresses. `attack_cat` is also removed because it directly gives away the label.

### Steps

1. `prepare_ml_data.py` cleans the records, converts the label to `normal` / `attack` and splits the data into `train.csv` and `test.csv`.
2. Train and test files are uploaded to HDFS.
3. `mahout describe` creates the dataset descriptor (`3 C 38 N L`).
4. `mahout buildforest` trains a 50-tree Random Forest using the partial (MapReduce) implementation.
5. `mahout testforest` predicts the test data and prints accuracy, the confusion matrix and the Kappa value.
6. The trained forest is copied to `models/random_forest/`.

### How to run

```bash
cd ~/network_traffic_analysis/scripts
bash run_mahout_random_forest.sh
```

The evaluation output is saved in `results/random_forest_evaluation.txt`.

## 8. Results

The project generates the following output files:

| Output File | Description |
|---|---|
| attack_sources.txt | Source IP analysis |
| attack_services.txt | Network service analysis |
| top_10_attack_sources.txt | Top 10 source IPs |
| attack_destination_ports.txt | Destination port analysis |
| random_forest_evaluation.txt | Random Forest accuracy and confusion matrix |

## 9. Screenshots

Execution screenshots and result demonstrations are available in:

`documentation/screenshots/`

## 10. Conclusion

This project demonstrates how Apache Hadoop and MapReduce can be used to analyze network traffic data at scale.

By aggregating network traffic information based on source IP addresses, destination ports, and services, the system helps identify potentially suspicious network activity and supports basic network security analysis. The Mahout Random Forest model extends this by automatically classifying network records as normal or attack traffic.

## 11. Future Enhancements

- Real-time network traffic monitoring.
- Multi-class classification of attack categories (DoS, Exploits, Fuzzers, etc.).
- Interactive network security dashboard.
- Automated suspicious activity alerts.
- Integration with additional intrusion detection datasets.
