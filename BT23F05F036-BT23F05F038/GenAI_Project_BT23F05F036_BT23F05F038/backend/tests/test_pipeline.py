import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestChatPipeline:
    """End-to-end integration tests for AskData API pipeline."""

    def test_health_check(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_upload_and_chat_flow(self):
        # 1. Upload sample CSV file
        csv_path = os.path.join("sample_data", "sales_data.csv")
        assert os.path.exists(csv_path), "sample_data/sales_data.csv must exist"

        with open(csv_path, "rb") as f:
            upload_resp = client.post(
                "/api/upload",
                files={"file": ("sales_data.csv", f, "text/csv")},
            )

        assert upload_resp.status_code == 200, upload_resp.text
        upload_data = upload_resp.json()
        assert "session_id" in upload_data
        session_id = upload_data["session_id"]
        assert upload_data["table_name"] == "sales_data"
        assert upload_data["profile"]["row_count"] >= 50
        assert len(upload_data["suggested_questions"]) == 5

        # 2. Ask a natural language question
        chat_resp = client.post(
            "/api/chat",
            json={
                "session_id": session_id,
                "question": "What is the total sales by region?",
            },
        )
        assert chat_resp.status_code == 200, chat_resp.text
        chat_data = chat_resp.json()

        assert chat_data["sql"] is not None
        assert "region" in chat_data["sql"].lower()
        assert chat_data["execution"] is not None
        assert chat_data["execution"]["row_count"] > 0
        assert chat_data["chart"] is not None
        assert chat_data["explanation"] is not None
        assert len(chat_data["thinking_steps"]) >= 4

        # 3. Test running manual SQL query
        manual_sql = f'SELECT region, COUNT(*) AS count_orders FROM "{upload_data["table_name"]}" GROUP BY region'
        run_resp = client.post(
            "/api/run-sql",
            json={"session_id": session_id, "sql": manual_sql},
        )
        assert run_resp.status_code == 200
        run_data = run_resp.json()
        assert run_data["is_valid"] is True
        assert run_data["execution"]["row_count"] > 0

        # 4. Fetch session history
        sess_resp = client.get(f"/api/session/{session_id}")
        assert sess_resp.status_code == 200
        sess_data = sess_resp.json()
        assert sess_data["table_name"] == "sales_data"
        assert len(sess_data["history"]) >= 1

    def test_ambiguous_question_triggers_clarification(self):
        csv_path = os.path.join("sample_data", "sales_data.csv")
        with open(csv_path, "rb") as f:
            upload_resp = client.post(
                "/api/upload",
                files={"file": ("sales_data.csv", f, "text/csv")},
            )
        session_id = upload_resp.json()["session_id"]

        chat_resp = client.post(
            "/api/chat",
            json={
                "session_id": session_id,
                "question": "Show the average unknown_metric_score",
            },
        )
        assert chat_resp.status_code == 200
        chat_data = chat_resp.json()
        assert chat_data["is_clarification"] is True
        assert chat_data["clarification_message"] is not None
