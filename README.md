# Streaming Database Prototype

## Overview
A streaming database is designed to handle real-time event-driven data, allowing continuous queries over live streams. Unlike traditional databases, which operate on batch-based data models, a streaming database processes incoming data in real-time, updating query results dynamically as new events arrive. 

### **How Our Streaming Database Differs from Existing Approaches**
Many current streaming solutions, such as Apache Kafka Streams, Apache Flink, and Materialize, focus on stream processing but often lack native queryability similar to traditional databases. Our streaming database is designed to bridge the gap between real-time event processing and relational-style querying, making it easier for users to work with streaming data using familiar SQL-like syntax. Unlike existing approaches, our system provides:
- **Native support for continuous queries**: Queries are executed in real-time and continuously updated as new data arrives.
- **Optimized event-driven storage**: Log-based, append-only architecture designed for high throughput.
- **Seamless integration with existing data pipelines**: Supports Kafka, WebSockets, and CDC logs while maintaining low latency.
- **Streaming joins and windowing functions**: Efficient real-time joins and aggregations without the need for batch recomputation.

### **Advantages Over Traditional Databases**
Traditional relational databases (e.g., PostgreSQL, MySQL) are designed for transactional consistency and batch analytics but struggle with real-time data workloads. Our streaming database offers several key advantages:

| Feature | Traditional Databases | Streaming Database |
|---------|----------------------|--------------------|
| **Query Execution** | Static, point-in-time queries | Continuous, real-time queries |
| **Data Processing** | Batch-oriented | Event-driven, real-time |
| **Performance** | Optimized for ACID transactions | Optimized for high-throughput, low-latency workloads |
| **Indexing** | Static indexes on stored data | Streaming indexes that update dynamically |
| **Joins** | Expensive batch-based joins | Efficient stream-stream joins |
| **Windowing** | Limited to historical aggregations | Native support for tumbling, sliding, and session windows |

By combining the best aspects of real-time stream processing and traditional relational querying, our streaming database enables businesses to make instant decisions based on live data rather than relying on delayed batch reports. 

## Core Features
- **Continuous Queries:** SQL-like queries that update dynamically as new data flows in.
- **Streaming Joins:** Ability to join multiple live data streams efficiently.
- **Event-Driven Storage:** Uses log-based architecture rather than batch inserts.
- **Time-Based Windowing:** Supports sliding, tumbling, and session windows.
- **Queryable State:** Queries can be executed on active streams without requiring full storage.
- **High Throughput:** Optimized for handling millions of events per second.
- **SQL Interface:** Uses familiar SQL syntax for querying.

## System Architecture
### 1. Ingestion Layer
- Accepts real-time data from sources like Kafka, WebSockets, CDC logs, and APIs.
- Converts raw data into structured event streams.
- Ensures fault tolerance with event replay mechanisms.

### 2. Storage Layer
- Uses **Log-Structured Merge Trees (LSM Trees)** for high-speed inserts.
- Stores **hot data in memory** (e.g., RocksDB for fast lookups).
- Persists **cold data in columnar storage** (e.g., Apache Parquet for analytics).

### 3. Query Engine
- Implements **continuous queries** over streaming data.
- Supports **stream-stream joins** and **time-based aggregations**.
- Uses **windowing functions** to allow computations over fixed intervals.

### 4. Execution Engine
- Uses **vectorized execution** to process thousands of events per second.
- Implements **parallel query execution** with actor-based concurrency.
- Optimizes query performance with **streaming indexes (Bloom Filters, LSM-trees).**

### 5. API & Query Interface
- **SQL Query Interface**: Supports PostgreSQL-style queries.
- **WebSocket & REST API**: Allows real-time querying via HTTP/WebSocket connections.
- **GraphQL Support**: Enables structured data access for applications.

## Database Schema Examples
### Events Table
```sql
CREATE TABLE events (
    event_id UUID PRIMARY KEY,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    event_time TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Sensor Data Stream
```sql
CREATE TABLE sensor_data (
    sensor_id UUID PRIMARY KEY,
    temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    pressure FLOAT NOT NULL,
    recorded_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### dbt Generator for Automated Schema Management
To facilitate the automation of staging and fact table generation, our streaming database integrates a **dbt generator**. This tool:
- **Scaffolds dbt projects** based on the pipeline schema.
- **Generates staging and fact models** to ensure proper data normalization.
- **Supports incremental processing**, reducing redundant computation and storage costs.

#### **Generating a Baseline dbt Project**
Once the streaming pipeline has ingested data, you can generate a dbt project using:
```sh
dlt dbt generate <pipeline-name>
```
This command creates a structured dbt project with:
- Staging models (`stg_<table>.sql`)
- Dimensional models (`dim_<table>.sql`)
- Fact models (`fact_<table>.sql`)

#### **Defining Relationships for Fact Tables**
Relationships between tables can be explicitly defined using:
```python
from dlt_plus.dbt_generator.utils import table_reference_adapter

table_reference_adapter(
    pipeline,
    "orders",
    references=[
        {"referenced_table": "customers", "columns": ["customer_id"], "referenced_columns": ["id"]},
    ],
)
```
This enables automatic foreign key recognition and improved query performance.

#### **Running the dbt Project**
Once generated, the dbt transformations can be executed using:
```sh
python run_<pipeline_name>_dbt.py
```
This runs incremental transformations, ensuring that only new records are processed, improving efficiency and speed.

## MVP Plan
### Goal
Create a minimal streaming database that ingests real-time data, processes queries continuously, and updates results dynamically.

### MVP Features
1. **Basic ingestion from Kafka/WebSockets.**
2. **Storage of latest 1M records in memory using RocksDB.**
3. **Basic SQL querying (e.g., `SELECT * FROM stream WHERE temp > 100`).**
4. **Continuously updating query results.**
5. **Return query results via WebSocket API.**
6. **Automated schema management with dbt generator.**

## Next Steps
1. **Finalize Tech Stack & Architecture Decisions.**
2. **Prototype MVP with Basic Continuous Query Execution.**
3. **Test Initial Performance Benchmarks.**
4. **Iterate and Open-Source the Project.**

---
### Final Thoughts
This streaming database has the potential to revolutionize real-time analytics. With built-in **dbt-based schema automation**, we make real-time transformations easier, faster, and more cost-efficient. An open-source approach ensures flexibility, making this a powerful alternative to traditional databases and streaming engines. 🚀

