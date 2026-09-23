# BiForge (TraceForge)

A forensic-grade, high-throughput log ingestion and parsing pipeline designed for NTRO-level network security. BiForge utilizes a dynamic three-tier processing architecture to ingest, categorize, normalize (OCSF), and analyze high-velocity telemetry data using deterministic regex, statistical machine learning, and AI-driven fallback mechanisms.

---

## Core Architecture & Pipeline Logic

BiForge operates on a highly decoupled microservices architecture utilizing **Redpanda** for message brokering, **MongoDB** for raw data persistence, and **OpenSearch** for OCSF-normalized visualization. 

The pipeline categorizes telemetry into three distinct confidence tiers:

1. **Tier 1: Fast-Path (High Confidence):** Immediate deterministic parsing via strict Regular Expressions (e.g., standard JSON, RFC3164 Syslog, Fortigate clean logs) in `tier0_parsers.py`.
2. **Tier 2: Statistical Reconciliation (Medium Confidence):** Logs failing strict matching are routed to the Drain3 template mining engine, which extracts parameters and groups mutated log structures into dynamic clusters.
3. **Tier 3: AI Fallback (Flagged / Low Confidence):** Critical anomalies and structurally broken logs are flagged and routed to a local Qwen/Ollama LLM Tiebreaker node for advanced AI extraction and contextual parsing.

---

## File Structure

```text
biforge/
|-- audit-worker/          # Tier 2 Auditing and verification microservice
|   |-- Dockerfile         # Container configuration for audit worker
|-- common/                # Shared utilities
|   |-- config.py          # Global settings management
|   |-- db_clients.py      # MongoDB and OpenSearch connection singletons
|-- docs/                  # Internal project documentation and specs
|-- ingestion-api/         # REST API for external HTTP log ingestion
|   |-- Dockerfile
|-- parsing-worker/        # Core Tier 1 & Tier 2 processing engine
|   |-- Dockerfile           
|   |-- drain3_config.ini  # Statistical engine parameters
|   |-- tier0_parsers.py   # Fast-path deterministic regex rules
|   |-- worker.py          # Kafka consumer and OCSF normalization logic
|-- scripts/               # Generators and operational scripts
|   |-- ntro_producer.py   # 1500+ synthetic log generator
|   |-- send_logs.py       # Manual log injection utility
|   |-- test_tier3.py      # Anomaly simulation for Qwen fallback
|-- secrets/               # Secure Docker mounts
|   |-- mongo_pw.txt       # MongoDB root password
|-- tests/                 # Unit and integration test suites
|-- tiebreaker-worker/     # Tier 3 AI fallback container (Ollama integration)
|   |-- Dockerfile
|-- .env                   # Environment variable configurations
|-- .env.example           # Template for environment variables
|-- .gitignore             # Git exclusion rules
|-- docker-compose.yml     # Complete infrastructure and network orchestration
|-- requirements.txt       # Python dependencies for local script execution
```

---

## User Guide & Configuration Briefing

### 1. Prerequisites & Tech Stack
Ensure the following tools are installed on your host machine prior to deployment:
* **Docker & Docker Compose:** Container orchestration and network isolation.
* **Python 3.10+:** Required for running local ingestion scripts and tests.
* **Git:** For version control and repository management.

**Infrastructure Stack (Handled via Docker):**
* **Redpanda (v23.3.10):** Kafka-compatible message queue (`ports: 9092` internal, `19092` external).
* **MongoDB (v7.0.5):** Immutable raw log storage (`port: 27017`).
* **OpenSearch & Dashboards (v2.11.1):** High-performance search and visualization (`ports: 9200`, `5601`).

### 2. Initial Configuration

**Step A: Environment Variables**
Clone the repository and set up your local environment configuration:
```bash
cp .env.example .env
```
Ensure your `.env` contains the correct topic mapping (e.g., `QUEUE_TOPIC=raw-events`).

**Step B: Secret Management**
Create the required directory and password file for MongoDB initialization:
```bash
mkdir -p secrets
echo "your_secure_password" > secrets/mongo_pw.txt
```

**Step C: Python Virtual Environment**
Activate a virtual environment and install the script dependencies:
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Linux/Mac
pip install -r requirements.txt
```

### 3. Execution Commands

**Start the Infrastructure:**
Boot the entire multi-container architecture in detached mode. This command will pull necessary images, build the Python workers, and establish internal networks.
```bash
docker compose up -d --build
```

**Inject Telemetry Data:**
Run the synthetic producer script to blast 1500 NTRO-grade logs into the Redpanda `raw-events` topic.
```bash
cd scripts
python ntro_producer.py
```

**Graceful Shutdown:**
To stop the pipeline and remove the containers, run the following command from the root directory:
```bash
docker compose down
```
*(Note: Unless persistent volumes are explicitly defined in `docker-compose.yml`, this command will wipe the OpenSearch and MongoDB data upon shutdown.)*

### 4. Visualization & Dashboard Setup

Once the pipeline is ingesting data, configure the OpenSearch Dashboards interface to monitor performance. The design strictly utilizes a techwear-inspired metallic and blue aesthetic to maintain a sharp, modern interface.

1. **Access Dashboards:** Navigate to `http://localhost:5601`.
2. **Enable Dark Mode:** Go to the top-left menu > Stack Management > Advanced Settings. Toggle `theme:darkMode` to **On** and reload the page.
3. **Set Time Filter:** Set the top-right time filter to **Next 1 month** (to capture synthetic forward-dated timestamps).
4. **Create the Confidence Metrics Chart:**
   * Go to **Visualize** > **Create new visualization** > **Vertical Bar**.
   * Select the `biforge-ocsf-logs*` index.
   * Add an **X-axis** bucket with **Aggregation:** `Terms` and **Field:** `parser_confidence.keyword`.
   * Change the Bucket type to **Split series** to separate the tiers.
   * Apply custom hex colors by clicking the legend dots to fit the aesthetic profile:
     * **High:** `#3A75C4` (Metallic Blue)
     * **Medium:** `#545454` (Muted Gunmetal)
     * **Flagged:** `#D32F2F` (Crimson Accent)
5. **Save:** Save the visualization as "Pipeline Confidence Metrics".