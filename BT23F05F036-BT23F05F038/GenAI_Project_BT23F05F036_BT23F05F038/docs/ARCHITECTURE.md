# AskData System Architecture & Technical Specifications

AskData is a production-grade AI Data Analyst application designed for instant, conversational data analysis over uploaded CSV/Excel spreadsheets and relational databases.

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph UI ["Frontend (React + Vite + TypeScript + Tailwind)"]
        Sidebar["Sidebar (Dataset Catalog & Profile)"]
        Chat["Chat Stream & Thought Steps"]
        Tabs["Tab Container: Plotly Chart | Table | SQL Editor"]
    end

    subgraph API ["Backend API (FastAPI)"]
        Upload["/api/upload"]
        ChatAPI["/api/chat & /api/chat/stream"]
        QueryAPI["/api/run-sql"]
        ExportAPI["/api/export"]
        DBAPI["/api/connect-db"]
    end

    subgraph Core ["Engine & Guardrails"]
        Validator["sqlglot AST Validator & Sanitizer"]
        DuckEngine["Isolated DuckDB Sessions (external_access = false)"]
        DBConnector["ReadOnlyDatabaseConnector (SQLAlchemy)"]
        ChartEngine["Plotly Spec Generator"]
        Explainer["Grounded Explainer Engine"]
    end

    subgraph Models ["LLM Layer"]
        LLM["Provider-Agnostic LLM Wrapper (Gemini / OpenAI / Claude)"]
    end

    Sidebar -->|Upload CSV/XLSX| Upload
    Chat -->|Natural Language Question| ChatAPI
    ChatAPI --> LLM
    LLM -->|Generated SQL| Validator
    Validator -->|Safe AST| DuckEngine
    DuckEngine -->|Error (Retry Loop)| LLM
    DuckEngine -->|Result Rows| ChartEngine
    DuckEngine -->|Result Rows| Explainer
    ChartEngine --> Tabs
    Explainer --> Tabs
    QueryAPI --> Validator
    DBAPI --> DBConnector
```

---

## 2. Multi-Stage Text-to-SQL Pipeline

1. **Context Construction**:
   - Analyzes the DuckDB catalog schema.
   - Extracts column names, SQL data types, null percentages, and min/max value boundaries.
   - Samples up to 10 distinct values for low-cardinality categorical fields (e.g., regions, segments, departments) to ensure zero syntax or naming hallucination.
   - Injects the prior 4 query interactions from conversation memory for multi-turn follow-ups.

2. **Tool-Calling Generation**:
   - Prompts the LLM with strict instructions to generate read-only `SELECT` statements or request clarification if ambiguous.

3. **AST Security Validation (sqlglot)**:
   - Verifies the statement parses as a single `SELECT` or `WITH ... SELECT`.
   - Traverses the abstract syntax tree to detect and block forbidden AST types (`Drop`, `Delete`, `Insert`, `Update`, `Alter`, `Command`, `Pragma`).
   - Identifies and rejects file or network scanning functions (`read_csv`, `read_parquet`, `httpfs`).
   - Verifies all referenced tables belong to the active session catalog or local CTE aliases.
   - Injects a default `LIMIT 500` or caps user-specified limits at `10,000`.

4. **Isolated Execution**:
   - Runs in an in-memory DuckDB database configured with `SET enable_external_access = false;`, thread caps, and memory limits.
   - Executes with a 10-second timeout.
   - In the event of a query execution failure, the error trace is passed back to the LLM in an automated retry loop (up to 2 retries).

5. **Visualization & Plotly Generation**:
   - Evaluates result dimensions and column data types.
   - Builds responsive, dark-mode compatible Plotly specifications for `bar`, `line`, `scatter`, `pie`, `histogram`, or `heatmap`.
   - Gracefully falls back to Table-only view if the query result is scalar or unsuitable for charting.

6. **Grounded Explanations**:
   - Computes statistical summaries (sum, min, max, top performer, bottom performer) strictly from the returned dataset rows.
   - Generates a concise natural language explanation without hallucinated metrics.
