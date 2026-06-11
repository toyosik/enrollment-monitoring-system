# High-Throughput Automated Enrollment Monitoring System

A decoupled, multi-language data pipeline designed to ingest, process, and broadcast real-time course availability metrics at scale.

## ⚙️ Architecture & Technology Stack
- **Orchestration (Bash):** Handles cron scheduling, manages data buffers, and handles basic pipeline error routing.
- **Ingestion & Processing (Python):** Parses JSON API payloads, performs delta state evaluations against historical data, and handles database transactions.
- **Storage Layer (SQL/SQLite):** Relational schema optimized with indexing strategies on high-frequency transaction logs.
- **Real-Time Broadcasting (JavaScript/Node.js):** Lightweight event-driven server utilizing Server-Sent Events (SSE) to push instant seat alerts to client dashboards.

## 📊 Scale Performance
- **Daily Ingestion Capability:** Designed to process **50,000+ API records daily**.
- **Real-Time Latency:** Processes delta updates and dispatches broadcast alerts in **< 500ms** from ingestion notice.
