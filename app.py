from kafka import KafkaConsumer
import rocksdb
import json
from fastapi import FastAPI, WebSocket
import threading
import uvicorn
import duckdb

# Initialize RocksDB storage with optimized options
db = rocksdb.DB("streaming_db", rocksdb.Options(create_if_missing=True, compression=rocksdb.SnappyCompression, optimize_for_point_lookup=True))

# Initialize DuckDB for complex queries
duckdb_conn = duckdb.connect(database=':memory:')
duckdb_conn.execute("""
CREATE TABLE sensor_data (
    sensor_id UUID PRIMARY KEY,
    temperature FLOAT,
    humidity FLOAT,
    pressure FLOAT,
    recorded_at TIMESTAMP
);
""")

# Kafka Consumer setup with auto-offset reset
consumer = KafkaConsumer(
    'sensor_data', 
    bootstrap_servers='localhost:9092', 
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest'
)

# Streaming Index Implementation
class StreamingIndex:
    def __init__(self, db):
        self.db = db
    
    def store_event(self, key, value):
        indexed_value = {
            "data": value,
            "timestamp": value.get("timestamp", "unknown")
        }
        self.db.put(key.encode(), json.dumps(indexed_value).encode())
        
        # Insert into DuckDB for analytical queries
        duckdb_conn.execute(
            "INSERT INTO sensor_data VALUES (?, ?, ?, ?, ?)", 
            (key, value.get("temperature"), value.get("humidity"), value.get("pressure"), value.get("timestamp"))
        )
    
    def query_events(self, timestamp_threshold):
        results = []
        it = self.db.iterator()
        for key, value in it:
            record = json.loads(value.decode())
            if record["timestamp"] >= timestamp_threshold:
                results.append(record)
        return results
    
    def aggregate_metrics(self):
        return duckdb_conn.execute(
            """
            SELECT sensor_id, AVG(temperature) AS avg_temp, AVG(humidity) AS avg_humidity, AVG(pressure) AS avg_pressure, 
            date_trunc('minute', recorded_at) AS time_bucket
            FROM sensor_data
            GROUP BY sensor_id, time_bucket;
            """
        ).fetchall()

# Initialize Streaming Index
stream_index = StreamingIndex(db)

def consume_stream():
    for message in consumer:
        stream_index.store_event(str(message.key), message.value)

# FastAPI for querying
db_app = FastAPI()

@db_app.get("/query")
def query_data(timestamp_threshold: str):
    return stream_index.query_events(timestamp_threshold)

@db_app.get("/aggregated_metrics")
def get_aggregated_metrics():
    return stream_index.aggregate_metrics()

# WebSocket-based live query results
@db_app.websocket("/live_query")
async def websocket_query(websocket: WebSocket):
    await websocket.accept()
    it = db.iterator()
    for key, value in it:
        record = json.loads(value.decode())
        await websocket.send_json(record)

if __name__ == "__main__":
    # Start Kafka consumer in a separate thread
    threading.Thread(target=consume_stream, daemon=True).start()
    
    # Run FastAPI server
    uvicorn.run(db_app, host="0.0.0.0", port=8000)
