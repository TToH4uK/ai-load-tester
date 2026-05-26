# Monitoring & Observability 📈

The AI Load Tester includes a comprehensive observability stack powered by Prometheus and Grafana, allowing you to monitor bot performance, semantic matching scores, NLP quality (Precision/Recall), system resources, and Locust load metrics in real-time.

---

## 🛠 Built-in Metrics & MLops

The system automatically tracks a variety of metrics:
- **Load Metrics**: Requests per second (RPS), failure rates, and response times (via Locust).
- **Bot Engine Performance**: Processing latency, semantic matching confidence scores.
- **NLP Quality Metrics**: Tracks True Positives (TP), False Positives (FP), and False Negatives (FN) to calculate real-time Precision and Recall. This is achieved by passing the expected intent via the `X-Expected-Intent` header from Locust.
- **Embedding Cache**: Tracks `CACHE_HITS` and `CACHE_MISSES` to calculate the cache Hit Ratio and optimize throughput.
- **System Resources**: Scrapes `node-exporter` (on port `9101`) to provide htop-like CPU and memory monitoring.

## 🛠 Adding Custom Metrics

The stack uses Prometheus to scrape metrics. To add a new metric to your testing environment:

1.  **Expose the Metric**: Update your `main.py` (Bot Engine) or `monitoring/` modules to expose Prometheus metrics. You can use libraries like `prometheus_client` to create custom Gauges, Counters, or Histograms.
2.  **Update Prometheus Config**: If you add a new service to scrape, add it to `prometheus/prometheus.yml` under the `scrape_configs` section. (The bot and node-exporter are already accessible).
3.  **Restart Prometheus**: Run `docker compose restart prometheus` to apply the new configuration.

---

## 📊 Adding Grafana Dashboards

Grafana is provisioned automatically. All dashboards stored in the `grafana/dashboards/` directory are loaded on startup.

To add or update a dashboard:

### 1. Create or Edit the Dashboard in the UI
- Access Grafana at `http://localhost:3000` (Anonymous Admin access is enabled by default, no password required).
- Create your panels using Prometheus as the data source (it is pre-configured to point to `http://prometheus:9090`).
- Once you are happy with the dashboard, click on **Dashboard settings** (the gear icon at the top) -> **JSON Model**.
- Copy the entire JSON block.

### 2. Save the Dashboard to the Repository
- Create a new JSON file in the `grafana/dashboards/` directory (e.g., `grafana/dashboards/my_new_dashboard.json`), or overwrite an existing one like `bank_bot_pro.json`.
- Paste the copied JSON into this file.
- Commit this file to version control so the dashboard is persisted across deployments.

### 3. Apply Changes
To apply the new dashboard configurations without restarting the entire stack, restart the Grafana container:
```bash
docker compose restart grafana
```

---

## 📡 Available Endpoints

| Service | Local Address | Description |
| :--- | :--- | :--- |
| **Grafana** | `http://localhost:3000` | Real-time metric visualization. |
| **Prometheus** | `http://localhost:9090` | Raw metric querying and target status. |
| **Locust Master**| `http://localhost:8089` | Load test orchestration and status. |
