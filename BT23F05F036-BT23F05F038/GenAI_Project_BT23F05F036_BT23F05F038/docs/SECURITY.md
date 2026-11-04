# AskData Security & Guardrails Specification

AskData operates under a **defense-in-depth security model** to prevent unauthorized data access, SQL injection, remote code execution (RCE), and prompt injection attacks.

---

## 1. SQL Security & Guardrails (sqlglot AST)

Rather than relying on naive regex string matching, queries are parsed into Abstract Syntax Tree (AST) representations using `sqlglot`:

```python
# Permitted Statements:
- SELECT ...
- WITH cte AS (SELECT ...) SELECT ...
- UNION / UNION ALL

# Prohibited Operations (Rejected at AST Level):
- DDL/DML: DROP, TRUNCATE, DELETE, UPDATE, INSERT, ALTER, CREATE
- System / Administrative Commands: PRAGMA, ATTACH, DETACH, INSTALL, LOAD, SYSTEM
- Multi-Statement Query Chaining: e.g. "SELECT 1; DROP TABLE users;"
- Transaction Controls: COMMIT, ROLLBACK, BEGIN
```

### Prohibited Function Blacklist
Queries invoking filesystem, network, or process spawning functions are rejected:
- `read_csv`, `read_csv_auto`, `scan_csv`
- `read_parquet`, `scan_parquet`
- `read_json`, `read_json_auto`
- `httpfs`, `system`, `duckdb_settings`

---

## 2. DuckDB Sandbox & Process Isolation

Every upload initializes an ephemeral, in-memory DuckDB connection:
```sql
SET enable_external_access = false;
SET max_memory = '512MB';
SET threads = 2;
```
- Disabling `enable_external_access` prevents DuckDB from accessing local files, remote URLs, or network sockets even if an attacker attempts an unparsed subquery.
- Sessions are strictly isolated: Table references from Session A cannot access or see tables in Session B.

---

## 3. Row Capping & Query Timeout Protection

- **Row Limitation**: If a query omits a `LIMIT` clause, `LIMIT 500` is automatically injected into the AST. If a user or model specifies `LIMIT > 10000`, the limit clause is clamped to `10000`.
- **Query Timeout**: Query execution is wrapped in a worker thread monitored with a hard 10-second timeout. Queries exceeding 10 seconds are interrupted.

---

## 4. Prompt Injection Defense

1. **Cell Content Isolation**: Sample cell values injected into prompts for context enrichment are escaped and contained in explicit `<sample_data>` boundary blocks.
2. **Instruction Delimitation**: The system prompt explicitly dictates that cell contents and column labels represent raw data literals, never actionable instructions or model directives.

---

## 5. Audit Logging & Compliance

Every query executed via the API is recorded in structured audit logs (`askdata.audit`):
- Client IP address
- HTTP method & endpoint
- Execution latency in milliseconds
- HTTP status code
- Success / failure status
