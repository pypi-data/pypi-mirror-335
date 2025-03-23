# Confluent Cloud for Apache Flink (CCAF) Housekeeping Python Library
The CCAF Housekeeping Python Library is a CI/CD support tool designed to automate the teardown of a Flink table and its associated Kafka resources—such as topics and schemas—along with any long-running statements linked to it. This robust automation guarantees that each deployment and test cycle is executed with exceptional consistency and reliability, paving the way for a dynamic and resilient application infrastructure.

> **Note:** _This library is in active development and is subject to change.  It covers only the methods I have needed so far.  If you need a method that is not covered, please feel free to open an issue or submit a pull request._

**Table of Contents**

<!-- toc -->
- [**1.0 Architecture**](#10-architecture)
    * [**1.1 Architecture Design Records (ADRs)**](#11-architecture-design-records-adrs)
- [**2.0 Installation**](#20-installation)
+ [**3.0 Resources**](#20-resources)
    * [**3.1 Managing Flink SQL Statements**](#31-managing-flink-sql-statements)
    * [**3.2 Other**](#32-other)
<!-- tocstop -->

## 1.0 Architecture

### 1.1 Architecture Design Records (ADRs)
* [001 Architectural Design Record (ADR):  CCAF Housekeeping Library](https://github.com/j3-signalroom/ccaf-housekeeping-python_lib/blob/main/.blog/adr_001.md)

## **2.0 Installation**
Install the Confluent Cloud for Apache Flink (CCAF) Housekeeping Python Library using **`pip`**:
```bash
pip install ccaf-housekeeping-python-lib
```

Or, using [**`uv`**](https://docs.astral.sh/uv/):
```bash
uv add ccaf-housekeeping-python-lib
```

## 3.0 Resources

### 3.1 Managing Flink SQL Statements
* [Monitor and Manage Flink SQL Statements in Confluent Cloud for Apache Flink](https://docs.confluent.io/cloud/current/flink/operate-and-deploy/monitor-statements.html#)
* [DROP TABLE Statement in Confluent Cloud for Apache Flink](https://docs.confluent.io/cloud/current/flink/reference/statements/drop-table.html#:~:text=Dropping%20a%20table%20permanently%20deletes,will%20transition%20to%20DEGRADED%20status._)

### 3.2 Other
* [Confluent Cloud Clients Python Library](https://github.com/j3-signalroom/cc-clients-python_lib)

