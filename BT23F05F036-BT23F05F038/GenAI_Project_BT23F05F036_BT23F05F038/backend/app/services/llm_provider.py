import json
import os
import re
from typing import Any, Dict, List, Optional
from app.config import settings
from app.models.schemas import TableProfile


class BaseLLMClient:
    """Base interface for LLM provider wrappers."""

    def generate_sql(
        self,
        schema_context: str,
        user_question: str,
        error_feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    def generate_chart_spec(
        self,
        question: str,
        sql: str,
        columns: List[str],
        sample_rows: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        raise NotImplementedError

    def generate_explanation(
        self,
        question: str,
        sql: str,
        result_rows: List[Dict[str, Any]],
        row_count: int,
    ) -> str:
        raise NotImplementedError

    def generate_suggested_questions(self, profile: TableProfile) -> List[str]:
        raise NotImplementedError


class MockLLMClient(BaseLLMClient):
    """
    High-fidelity deterministic Mock LLM client for offline development,
    automated unit/integration tests, and CI/CD pipelines.
    """

    def generate_sql(
        self,
        schema_context: str,
        user_question: str,
        error_feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Extract table name from schema context
        table_match = re.search(r"TABLE NAME:\s*([a-zA-Z0-9_]+)", schema_context)
        table_name = table_match.group(1) if table_match else "data"
        q_lower = user_question.lower()

        # Check for ambiguity
        if "unknown_metric" in q_lower or "xyzzy" in q_lower or "fake_column" in q_lower:
            return {
                "sql": "",
                "thought": "The requested column does not exist in the schema.",
                "is_clarification": True,
                "clarification_message": "Could you clarify which metric you are referring to? It is not present in the dataset columns.",
            }

        # Handling sales_data questions
        if "sales" in table_name or "category" in schema_context:
            if "region" in q_lower:
                return {
                    "sql": f'SELECT region, SUM(sales) AS total_sales, SUM(profit) AS total_profit FROM "{table_name}" GROUP BY region ORDER BY total_sales DESC',
                    "thought": "Grouping sales and profit by geographic region.",
                    "is_clarification": False,
                }
            if "total sales" in q_lower or "overall sales" in q_lower:
                return {
                    "sql": f'SELECT SUM(sales) AS total_sales, SUM(profit) AS total_profit FROM "{table_name}"',
                    "thought": "Calculating overall sales and profit across all records.",
                    "is_clarification": False,
                }
            if "category" in q_lower or "sub_category" in q_lower:
                return {
                    "sql": f'SELECT category, SUM(sales) AS total_sales, ROUND(AVG(discount), 2) AS avg_discount FROM "{table_name}" GROUP BY category ORDER BY total_sales DESC',
                    "thought": "Aggregating sales and average discount per category.",
                    "is_clarification": False,
                }
            if "top" in q_lower and "customer" in q_lower:
                return {
                    "sql": f'SELECT customer_name, SUM(sales) AS total_sales, COUNT(*) AS order_count FROM "{table_name}" GROUP BY customer_name ORDER BY total_sales DESC LIMIT 5',
                    "thought": "Selecting top 5 customers by aggregated sales volume.",
                    "is_clarification": False,
                }
            if "month" in q_lower or "trend" in q_lower or "date" in q_lower:
                return {
                    "sql": f'SELECT strftime(CAST(order_date AS DATE), \'%Y-%m\') AS order_month, SUM(sales) AS monthly_sales FROM "{table_name}" GROUP BY order_month ORDER BY order_month ASC',
                    "thought": "Extracting monthly sales trend over time.",
                    "is_clarification": False,
                }
            # Default sales query
            return {
                "sql": f'SELECT category, region, SUM(sales) AS total_sales, SUM(profit) AS total_profit FROM "{table_name}" GROUP BY category, region ORDER BY total_sales DESC LIMIT 10',
                "thought": "Aggregating sales and profit broken down by category and region.",
                "is_clarification": False,
            }

        # Handling student_performance questions
        if "student" in table_name or "gpa" in schema_context:
            if "average gpa" in q_lower or "avg gpa" in q_lower:
                return {
                    "sql": f'SELECT department, ROUND(AVG(gpa), 2) AS avg_gpa, COUNT(*) AS student_count FROM "{table_name}" GROUP BY department ORDER BY avg_gpa DESC',
                    "thought": "Calculating average GPA by academic department.",
                    "is_clarification": False,
                }
            if "pass" in q_lower or "pass rate" in q_lower:
                return {
                    "sql": f'SELECT department, COUNT(*) AS total_students, SUM(CASE WHEN passed THEN 1 ELSE 0 END) AS passed_students FROM "{table_name}" GROUP BY department',
                    "thought": "Computing pass rates per department.",
                    "is_clarification": False,
                }
            if "top" in q_lower or "highest" in q_lower:
                return {
                    "sql": f'SELECT name, department, gpa, final_score FROM "{table_name}" ORDER BY gpa DESC LIMIT 5',
                    "thought": "Querying top performing students by GPA.",
                    "is_clarification": False,
                }
            return {
                "sql": f'SELECT department, ROUND(AVG(final_score), 2) AS avg_final_score, ROUND(AVG(study_hours_per_week), 2) AS avg_study_hours FROM "{table_name}" GROUP BY department ORDER BY avg_final_score DESC',
                "thought": "Comparing average final exam scores and study hours by department.",
                "is_clarification": False,
            }

        # Generic fallback query
        return {
            "sql": f'SELECT * FROM "{table_name}" LIMIT 10',
            "thought": "Retrieving sample rows from table.",
            "is_clarification": False,
        }

    def generate_chart_spec(
        self,
        question: str,
        sql: str,
        columns: List[str],
        sample_rows: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if not columns or not sample_rows:
            return {"chart_type": "none", "title": "No Chart", "plotly_json": {}}

        # If 1 numeric column and 1 row (scalar KPI) -> no chart or indicator
        if len(sample_rows) == 1 and len(columns) <= 2:
            return {"chart_type": "none", "title": "Summary KPI", "plotly_json": {}}

        # Categorical X + Numerical Y -> Bar chart
        x_candidate = columns[0]
        y_candidate = columns[1] if len(columns) > 1 else columns[0]

        q_lower = question.lower()
        if "trend" in q_lower or "time" in q_lower or "month" in q_lower or "date" in x_candidate.lower():
            chart_type = "line"
        elif "share" in q_lower or "distribution" in q_lower or "pie" in q_lower:
            chart_type = "pie"
        elif "scatter" in q_lower or "correlation" in q_lower:
            chart_type = "scatter"
        else:
            chart_type = "bar"

        # Construct Plotly JSON
        x_vals = [r.get(x_candidate) for r in sample_rows]
        y_vals = [r.get(y_candidate) for r in sample_rows]

        if chart_type == "pie":
            data = [{"labels": x_vals, "values": y_vals, "type": "pie"}]
        elif chart_type == "line":
            data = [{"x": x_vals, "y": y_vals, "type": "scatter", "mode": "lines+markers", "marker": {"color": "#3b82f6"}}]
        elif chart_type == "scatter":
            data = [{"x": x_vals, "y": y_vals, "type": "scatter", "mode": "markers", "marker": {"size": 10, "color": "#8b5cf6"}}]
        else:
            data = [{"x": x_vals, "y": y_vals, "type": "bar", "marker": {"color": "#3b82f6"}}]

        layout = {
            "title": {"text": f"{y_candidate.replace('_', ' ').title()} by {x_candidate.replace('_', ' ').title()}"},
            "xaxis": {"title": x_candidate.replace("_", " ").title()},
            "yaxis": {"title": y_candidate.replace("_", " ").title()},
            "autosize": True,
            "margin": {"l": 50, "r": 30, "t": 50, "b": 50},
            "paper_bgcolor": "transparent",
            "plot_bgcolor": "transparent",
        }

        return {
            "chart_type": chart_type,
            "title": layout["title"]["text"],
            "x_axis": x_candidate,
            "y_axis": y_candidate,
            "plotly_json": {"data": data, "layout": layout},
        }

    def generate_explanation(
        self,
        question: str,
        sql: str,
        result_rows: List[Dict[str, Any]],
        row_count: int,
    ) -> str:
        if not result_rows:
            return "The query executed successfully but returned 0 matching records."

        if row_count == 1:
            first_row = result_rows[0]
            items = [f"**{k.replace('_', ' ').title()}**: {v}" for k, v in first_row.items()]
            return f"The calculation returned: {', '.join(items)}."

        # Multi-row summary
        first_row = result_rows[0]
        keys = list(first_row.keys())
        first_key = keys[0]
        val_key = keys[1] if len(keys) > 1 else first_key
        top_name = first_row.get(first_key)
        top_val = first_row.get(val_key)

        return (
            f"The query returned {row_count} rows. "
            f"The leading entry is **{top_name}** with a {val_key.replace('_', ' ')} of **{top_val}**. "
            f"Results are sorted based on query criteria."
        )

    def generate_suggested_questions(self, profile: TableProfile) -> List[str]:
        cols = [c.name.lower() for c in profile.columns]
        if "sales" in cols and "region" in cols:
            return [
                "What is the total sales and profit by region?",
                "Which product categories generate the highest revenue?",
                "Who are the top 5 customers by sales?",
                "What is the monthly sales trend over time?",
                "Which orders had the highest discount rates?",
            ]
        elif "gpa" in cols and "department" in cols:
            return [
                "What is the average GPA by academic department?",
                "What is the pass rate across different majors?",
                "Who are the top 5 students by overall performance?",
                "Is there a correlation between study hours and final score?",
                "How does student attendance vary by department?",
            ]
        else:
            col_names = [c.name for c in profile.columns[:3]]
            return [
                f"Show the first 10 rows of {profile.table_name}",
                f"What is the count of records grouped by {col_names[0]}?",
                f"What are the top values for {col_names[-1]}?",
                "Are there any null or missing values in this dataset?",
                "Show summary statistics for the numerical columns.",
            ]


class GeminiLLMClient(BaseLLMClient):
    """Google Gemini LLM wrapper using official SDK."""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        # Configure client
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def generate_sql(
        self,
        schema_context: str,
        user_question: str,
        error_feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        prompt = f"""You are an expert DuckDB SQL data analyst.
Given the dataset schema below, write a safe, single DuckDB SQL query to answer the user's question.

RULES:
1. ONLY write a SELECT statement. Never write DDL, DML, PRAGMA, COPY, or file functions.
2. Use exact table and column names matching the schema.
3. If the question is ambiguous or asks for columns that do not exist, set is_clarification=true and provide a helpful clarification_message.
4. Output STRICT JSON only with keys: "sql", "thought", "is_clarification", "clarification_message".
Do not wrap in markdown quotes if possible, or use standard ```json.

SCHEMA CONTEXT:
{schema_context}

USER QUESTION:
{user_question}
"""
        if error_feedback:
            prompt += f"\nPREVIOUS EXECUTION ERROR TO FIX:\n{error_feedback}\nFix the query to address this error."

        response = self.model.generate_content(prompt)
        text = response.text.strip()
        # Parse JSON
        clean_json = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
        clean_json = re.sub(r"```$", "", clean_json, flags=re.MULTILINE).strip()
        try:
            return json.loads(clean_json)
        except Exception:
            # Fallback regex extraction
            sql_match = re.search(r"SELECT.*", text, re.IGNORECASE | re.DOTALL)
            if sql_match:
                return {"sql": sql_match.group(0).strip().rstrip(";"), "thought": "Extracted SQL from text", "is_clarification": False}
            return {"sql": "", "thought": "Failed to parse JSON", "is_clarification": True, "clarification_message": "Could not understand question."}

    def generate_chart_spec(
        self,
        question: str,
        sql: str,
        columns: List[str],
        sample_rows: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        # Fall back to heuristic chart spec builder or call Gemini
        mock = MockLLMClient()
        return mock.generate_chart_spec(question, sql, columns, sample_rows)

    def generate_explanation(
        self,
        question: str,
        sql: str,
        result_rows: List[Dict[str, Any]],
        row_count: int,
    ) -> str:
        prompt = f"""You are a data analyst explaining a query result.
Question: {question}
Returned rows count: {row_count}
Sample result rows: {json.dumps(result_rows[:5])}

Write a 2-3 sentence clear, professional insight grounded ONLY in the exact numbers shown above.
Do not invent any facts, numbers, or external assumptions.
"""
        try:
            resp = self.model.generate_content(prompt)
            return resp.text.strip()
        except Exception:
            return MockLLMClient().generate_explanation(question, sql, result_rows, row_count)

    def generate_suggested_questions(self, profile: TableProfile) -> List[str]:
        return MockLLMClient().generate_suggested_questions(profile)


def get_llm_client() -> BaseLLMClient:
    """Factory creating the appropriate LLM client based on configuration."""
    provider = settings.llm_provider.lower()
    gemini_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")

    if provider == "gemini" and gemini_key:
        try:
            return GeminiLLMClient(api_key=gemini_key, model_name=settings.llm_model)
        except Exception as e:
            print(f"Warning: Failed to initialize Gemini client ({e}). Falling back to MockLLMClient.")
            return MockLLMClient()

    # Default fallback for testing and development
    return MockLLMClient()
