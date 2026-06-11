#!/bin/bash

# Configuration environment variables
DB_NAME="enrollment.db"
SQL_SCHEMA="schema.sql"
PYTHON_ENGINE="fetch_and_process.py"
LOG_FILE="pipeline.log"

echo "==========================================================" >> "$LOG_FILE"
echo "[$(date)] Launching Automated Monitoring Pipeline" >> "$LOG_FILE"

# Step 1: Ensure database structure exists
if [ ! -f "$DB_NAME" ]; then
    echo "[*] Database not detected. Initializing schema..." >> "$LOG_FILE"
    sqlite3 "$DB_NAME" < "$SQL_SCHEMA"
fi

# Step 2: Generate mock high-volume API data streaming buffer (Simulating 50,000+ bulk items)
# For this script runnable demo, we'll write a dynamic batch of course records to a local JSON payload.
cat <<EOF > data_buffer.json
{
  "records": [
    {"course_id": "CS-101", "course_name": "Intro to Computer Science", "total_seats": 100, "unassigned_seats": 2},
    {"course_id": "CS-202", "course_name": "Data Structures & Algorithms", "total_seats": 60, "unassigned_seats": 0},
    {"course_id": "CS-305", "course_name": "Operating Systems", "total_seats": 45, "unassigned_seats": 5}
  ]
}
EOF

# Step 3: Pipe the data buffer payload into the Python engine
if [ -f "data_buffer.json" ]; then
    python3 "$PYTHON_ENGINE" < data_buffer.json >> "$LOG_FILE" 2>&1
    
    # Check execution success status
    if [ $? -eq 0 ]; then
        echo "[+] Pipeline execution sync successful." >> "$LOG_FILE"
    else
        echo "[-] Critical processing error detected in pipeline execution." >> "$LOG_FILE"
    fi
    
    # Cleanup transaction temporary files
    rm data_buffer.json
else
    echo "[-] Critical Error: Data ingestion source missing." >> "$LOG_FILE"
fi
