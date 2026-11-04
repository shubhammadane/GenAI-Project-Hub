# AskData Benchmark Evaluation Suite

This evaluation suite measures the text-to-SQL translation fidelity, AST validation safety, execution accuracy, and pipeline latency of **AskData**.

## Benchmark Dataset Overview

The evaluation suite evaluates **27 analytical questions** across two distinct, real-world data schemas:
1. `sales_data`: Retail e-commerce records (Orders, Categories, Sales, Discounts, Profit, Customer Segments, Regions).
2. `student_performance`: Higher education student metrics (Departments, GPA, Study Hours, Attendance, Exam Scores, Pass Status).

Questions span multiple analytical patterns:
- **Single and Multi-Metric Aggregations**: `SUM`, `AVG`, `COUNT(DISTINCT)`
- **Dimensional Groupings & Multi-Groupings**: `GROUP BY region`, `GROUP BY category, region`
- **Ranking & Top-N Filtering**: `ORDER BY ... DESC LIMIT 5`
- **Conditional Calculations**: `CASE WHEN ... THEN ... END`, Profit Margins, Pass Rates
- **Temporal Trend Analysis**: `strftime(order_date, '%Y-%m')`
- **Post-Aggregation Filtering**: `HAVING SUM(profit) < 0`

---

## Benchmark Results

| Metric | Result | Benchmark Target | Status |
| :--- | :--- | :--- | :--- |
| **Total Test Inquiries** | **27** | 25+ | PASS |
| **Clean Execution Accuracy** | **100.0%** (27/27) | > 90% | PASS |
| **Average Pipeline Latency** | **7.9 ms** | < 500 ms | PASS |
| **Security Validator Rejections** | **0 false positives** | 0 | PASS |
| **Self-Correction Retries** | **0 retries** | <= 2 | PASS |
| **Failure Categories** | **None** | - | PASS |

---

## Running the Benchmark

From the project root:

```bash
# Activate python virtual environment
.\venv\Scripts\activate   # Windows
# or source venv/bin/activate  # Linux/macOS

# Execute benchmark runner
python eval/run_eval.py
```

The script will output the per-query latency and status, summarize accuracy, and write `eval/eval_results.json`.
