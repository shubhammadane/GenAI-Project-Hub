import os
import sqlite3
import tempfile
import pytest
from fastapi.testclient import TestClient
from app.core.db_connectors import ReadOnlyDatabaseConnector
from app.main import app

client = TestClient(app)


class TestPhase4Features:
    """Tests for Phase 4: Database Connectors (Read-Only) and Export Pipeline."""

    @pytest.fixture
    def sample_sqlite_db(self):
        """Creates a temporary SQLite database file with test records."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE employees (id INT, name TEXT, salary FLOAT);")
        cursor.execute("INSERT INTO employees VALUES (1, 'Alice', 95000.0);")
        cursor.execute("INSERT INTO employees VALUES (2, 'Bob', 82000.0);")
        conn.commit()
        conn.close()

        yield db_path

        # Cleanup
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception:
                pass

    def test_sqlite_connector_read_only_success(self, sample_sqlite_db):
        clean_path = sample_sqlite_db.replace("\\", "/")
        conn_url = f"sqlite:///{clean_path}"
        tables = ReadOnlyDatabaseConnector.list_tables(conn_url)
        assert "employees" in tables

        res = ReadOnlyDatabaseConnector.execute_read_only_query(
            conn_url, "SELECT name, salary FROM employees WHERE salary > 85000"
        )
        assert res.error is None
        assert res.row_count == 1
        assert res.rows[0]["name"] == "Alice"

    def test_sqlite_connector_blocks_modification(self, sample_sqlite_db):
        clean_path = sample_sqlite_db.replace("\\", "/")
        conn_url = f"sqlite:///{clean_path}"
        res = ReadOnlyDatabaseConnector.execute_read_only_query(
            conn_url, "DROP TABLE employees"
        )
        assert res.error is not None
        assert "Only read-only SELECT" in res.error or "Only SELECT or WITH" in res.error

    def test_api_connect_db_and_import(self, sample_sqlite_db):
        clean_path = sample_sqlite_db.replace("\\", "/")
        conn_url = f"sqlite:///{clean_path}"

        # 1. List tables via API
        list_resp = client.post(
            "/api/connect-db/list-tables",
            json={"connection_url": conn_url},
        )
        assert list_resp.status_code == 200
        assert "employees" in list_resp.json()["tables"]

        # 2. Connect and import table into AskData DuckDB session
        import_resp = client.post(
            "/api/connect-db",
            json={"connection_url": conn_url, "table_name": "employees"},
        )
        assert import_resp.status_code == 200
        data = import_resp.json()
        assert "session_id" in data
        assert data["table_name"] == "employees"
        assert data["profile"]["row_count"] == 2
        assert len(data["suggested_questions"]) == 5

    def test_export_report_and_csv(self):
        # 1. Upload CSV to establish session
        csv_path = os.path.join("sample_data", "sales_data.csv")
        with open(csv_path, "rb") as f:
            upload_resp = client.post(
                "/api/upload",
                files={"file": ("sales_data.csv", f, "text/csv")},
            )
        session_id = upload_resp.json()["session_id"]

        # 2. Query something
        client.post(
            "/api/chat",
            json={"session_id": session_id, "question": "Total sales by region"},
        )

        # 3. Export Markdown report
        rep_resp = client.get(f"/api/export/{session_id}/report")
        assert rep_resp.status_code == 200
        assert "text/plain" in rep_resp.headers["content-type"]
        assert "# AskData Analytical Report" in rep_resp.text
        assert "Total sales by region" in rep_resp.text
        assert "Security & Compliance Guarantee" in rep_resp.text

        # 4. Export CSV
        csv_export_resp = client.get(f"/api/export/{session_id}/csv")
        assert csv_export_resp.status_code == 200
        assert "text/csv" in csv_export_resp.headers["content-type"]
        assert len(csv_export_resp.text.split("\n")) > 1
