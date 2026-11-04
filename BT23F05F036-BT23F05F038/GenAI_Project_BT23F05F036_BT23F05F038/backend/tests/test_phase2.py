import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.chart_generator import ChartGenerator
from app.services.explainer import Explainer

client = TestClient(app)


class TestPhase2Features:
    """Tests for Phase 2: Charts, Explanations, Memory, SSE Streaming & Retry Loop."""

    def test_chart_generator_bar_chart(self):
        rows = [
            {"region": "East", "sales": 15000},
            {"region": "West", "sales": 12000},
            {"region": "Central", "sales": 9500},
        ]
        spec = ChartGenerator.generate(
            question="Total sales by region",
            columns=["region", "sales"],
            rows=rows,
        )
        assert spec.chart_type == "bar"
        assert spec.x_axis == "region"
        assert spec.y_axis == "sales"
        assert "data" in spec.plotly_json
        assert spec.plotly_json["data"][0]["type"] == "bar"

    def test_chart_generator_line_chart_for_dates(self):
        rows = [
            {"order_month": "2024-01", "monthly_sales": 5000},
            {"order_month": "2024-02", "monthly_sales": 7500},
            {"order_month": "2024-03", "monthly_sales": 9200},
        ]
        spec = ChartGenerator.generate(
            question="Monthly sales trend",
            columns=["order_month", "monthly_sales"],
            rows=rows,
        )
        assert spec.chart_type == "line"
        assert spec.plotly_json["data"][0]["type"] == "scatter"
        assert spec.plotly_json["data"][0]["mode"] == "lines+markers"

    def test_chart_generator_scatter_plot(self):
        rows = [
            {"study_hours": 15.0, "final_score": 75.0, "student": "Alice"},
            {"study_hours": 25.0, "final_score": 92.0, "student": "Bob"},
            {"study_hours": 30.0, "final_score": 98.0, "student": "Charlie"},
        ]
        spec = ChartGenerator.generate(
            question="Correlation between study hours and final score",
            columns=["study_hours", "final_score", "student"],
            rows=rows,
        )
        assert spec.chart_type == "scatter"
        assert spec.plotly_json["data"][0]["mode"] == "markers"

    def test_chart_generator_single_kpi_fallback(self):
        rows = [{"total_sales": 45000.0}]
        spec = ChartGenerator.generate(
            question="Overall total sales",
            columns=["total_sales"],
            rows=rows,
        )
        assert spec.chart_type == "none"

    def test_grounded_explainer_single_row(self):
        rows = [{"total_revenue": 125000.50, "orders_count": 450}]
        text = Explainer.explain(
            question="Total revenue and order count",
            sql="SELECT ...",
            columns=["total_revenue", "orders_count"],
            rows=rows,
            row_count=1,
        )
        assert "125,000.50" in text
        assert "450" in text

    def test_grounded_explainer_multi_row(self):
        rows = [
            {"department": "Computer Science", "avg_gpa": 3.82},
            {"department": "Data Science", "avg_gpa": 3.75},
            {"department": "Electrical Engineering", "avg_gpa": 2.85},
        ]
        text = Explainer.explain(
            question="Average GPA by department",
            sql="SELECT ...",
            columns=["department", "avg_gpa"],
            rows=rows,
            row_count=3,
        )
        assert "Computer Science" in text
        assert "3.82" in text
        assert "Electrical Engineering" in text

    def test_sse_chat_stream_endpoint(self):
        # 1. Upload CSV
        csv_path = os.path.join("sample_data", "sales_data.csv")
        with open(csv_path, "rb") as f:
            upload_resp = client.post(
                "/api/upload",
                files={"file": ("sales_data.csv", f, "text/csv")},
            )
        session_id = upload_resp.json()["session_id"]

        # 2. Call stream endpoint
        resp = client.get(
            f"/api/chat/stream?session_id={session_id}&question=What+is+total+sales+by+region"
        )
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]
        body = resp.text
        assert "data:" in body
        assert "[DONE]" in body
        assert "understanding" in body
        assert "generating_sql" in body
        assert "charting" in body
