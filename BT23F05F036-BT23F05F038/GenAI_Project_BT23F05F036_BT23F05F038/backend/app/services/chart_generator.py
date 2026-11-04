from typing import Any, Dict, List, Optional
from app.models.schemas import ChartSpec


class ChartGenerator:
    """
    Analyzes query result dimensions, data types, and row cardinalities
    to build production Plotly JSON specifications.
    Supports bar, line, scatter, pie, histogram, and heatmap with
    graceful fallback to 'none' (table-only).
    """

    CHART_PALETTE = [
        "#3b82f6",  # blue
        "#10b981",  # emerald
        "#f59e0b",  # amber
        "#ef4444",  # red
        "#8b5cf6",  # violet
        "#ec4899",  # pink
        "#06b6d4",  # cyan
        "#84cc16",  # lime
    ]

    @classmethod
    def generate(
        cls,
        question: str,
        columns: List[str],
        rows: List[Dict[str, Any]],
        suggested_type: Optional[str] = None,
    ) -> ChartSpec:
        if not columns or not rows:
            return ChartSpec(chart_type="none", title="No Data", plotly_json={})

        row_count = len(rows)

        # 1. Single scalar KPI (1 row, <=2 cols) -> table or KPI, no chart needed
        if row_count == 1 and len(columns) <= 2:
            return ChartSpec(chart_type="none", title="Single Metric KPI", plotly_json={})

        # Inspect column types based on values in rows
        numeric_cols = []
        date_cols = []
        text_cols = []

        for col in columns:
            vals = [r.get(col) for r in rows if r.get(col) is not None]
            if not vals:
                continue
            first_val = vals[0]
            if isinstance(first_val, (int, float)) and not isinstance(first_val, bool):
                numeric_cols.append(col)
            elif (
                isinstance(first_val, str)
                and ("-" in first_val or "/" in first_val)
                and len(first_val) in (7, 10, 19, 20, 24)
            ):
                date_cols.append(col)
            else:
                text_cols.append(col)

        # Determine best chart type
        chart_type = suggested_type or cls._determine_chart_type(
            question, numeric_cols, date_cols, text_cols, row_count
        )

        if chart_type == "none":
            return ChartSpec(chart_type="none", title="Table View Recommended", plotly_json={})

        return cls._build_plotly_spec(
            chart_type=chart_type,
            columns=columns,
            rows=rows,
            numeric_cols=numeric_cols,
            date_cols=date_cols,
            text_cols=text_cols,
            question=question,
        )

    @classmethod
    def _determine_chart_type(
        cls,
        question: str,
        numeric_cols: List[str],
        date_cols: List[str],
        text_cols: List[str],
        row_count: int,
    ) -> str:
        q_lower = question.lower()

        # Explicit user question hints
        if "trend" in q_lower or "over time" in q_lower or "monthly" in q_lower or "timeline" in q_lower:
            return "line"
        if "scatter" in q_lower or "correlation" in q_lower:
            return "scatter"
        if "pie" in q_lower or "share" in q_lower or "proportion" in q_lower:
            if row_count <= 8 and len(numeric_cols) >= 1 and len(text_cols) >= 1:
                return "pie"
        if "distribution" in q_lower or "histogram" in q_lower:
            return "histogram"
        if "heatmap" in q_lower and len(text_cols) >= 2 and len(numeric_cols) >= 1:
            return "heatmap"

        # Heuristic rules
        if date_cols and numeric_cols:
            return "line"
        if len(text_cols) >= 1 and len(numeric_cols) >= 1:
            if row_count <= 6 and ("percentage" in q_lower or "share" in q_lower):
                return "pie"
            return "bar"
        if len(numeric_cols) >= 2:
            return "scatter"
        if len(numeric_cols) == 1 and not text_cols and not date_cols and row_count > 5:
            return "histogram"

        return "bar"

    @classmethod
    def _build_plotly_spec(
        cls,
        chart_type: str,
        columns: List[str],
        rows: List[Dict[str, Any]],
        numeric_cols: List[str],
        date_cols: List[str],
        text_cols: List[str],
        question: str,
    ) -> ChartSpec:
        x_axis = None
        y_axis = None
        title = f"{question[:60]}..." if len(question) > 60 else question

        base_layout: Dict[str, Any] = {
            "title": {"text": title, "font": {"size": 15, "color": "#1f2937"}},
            "autosize": True,
            "margin": {"l": 55, "r": 30, "t": 50, "b": 60},
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "hovermode": "closest",
            "legend": {"orientation": "h", "y": -0.2},
            "font": {"family": "Inter, sans-serif"},
        }

        # 1. Line Chart
        if chart_type == "line":
            x_axis = date_cols[0] if date_cols else (text_cols[0] if text_cols else columns[0])
            y_axis = numeric_cols[0] if numeric_cols else columns[1]
            x_vals = [r.get(x_axis) for r in rows]
            y_vals = [r.get(y_axis) for r in rows]
            data = [
                {
                    "x": x_vals,
                    "y": y_vals,
                    "type": "scatter",
                    "mode": "lines+markers",
                    "line": {"color": cls.CHART_PALETTE[0], "width": 3},
                    "marker": {"size": 7, "color": cls.CHART_PALETTE[0]},
                    "name": y_axis.replace("_", " ").title(),
                }
            ]
            base_layout["xaxis"] = {"title": x_axis.replace("_", " ").title(), "gridcolor": "#e5e7eb"}
            base_layout["yaxis"] = {"title": y_axis.replace("_", " ").title(), "gridcolor": "#e5e7eb"}

        # 2. Pie Chart
        elif chart_type == "pie":
            label_col = text_cols[0] if text_cols else columns[0]
            val_col = numeric_cols[0] if numeric_cols else columns[1]
            x_axis = label_col
            y_axis = val_col
            labels = [r.get(label_col) for r in rows]
            values = [r.get(val_col) for r in rows]
            data = [
                {
                    "labels": labels,
                    "values": values,
                    "type": "pie",
                    "hole": 0.4,
                    "marker": {"colors": cls.CHART_PALETTE},
                    "textinfo": "label+percent",
                }
            ]

        # 3. Scatter Chart
        elif chart_type == "scatter":
            x_axis = numeric_cols[0] if numeric_cols else columns[0]
            y_axis = numeric_cols[1] if len(numeric_cols) > 1 else (numeric_cols[0] if numeric_cols else columns[1])
            x_vals = [r.get(x_axis) for r in rows]
            y_vals = [r.get(y_axis) for r in rows]
            hover_text = [str(r.get(text_cols[0])) for r in rows] if text_cols else None
            data = [
                {
                    "x": x_vals,
                    "y": y_vals,
                    "text": hover_text,
                    "type": "scatter",
                    "mode": "markers",
                    "marker": {"size": 9, "color": cls.CHART_PALETTE[4], "opacity": 0.8},
                }
            ]
            base_layout["xaxis"] = {"title": x_axis.replace("_", " ").title(), "gridcolor": "#e5e7eb"}
            base_layout["yaxis"] = {"title": y_axis.replace("_", " ").title(), "gridcolor": "#e5e7eb"}

        # 4. Histogram
        elif chart_type == "histogram":
            val_col = numeric_cols[0] if numeric_cols else columns[0]
            x_axis = val_col
            x_vals = [r.get(val_col) for r in rows]
            data = [
                {
                    "x": x_vals,
                    "type": "histogram",
                    "marker": {"color": cls.CHART_PALETTE[2]},
                }
            ]
            base_layout["xaxis"] = {"title": val_col.replace("_", " ").title(), "gridcolor": "#e5e7eb"}
            base_layout["yaxis"] = {"title": "Frequency", "gridcolor": "#e5e7eb"}

        # 5. Bar Chart (Default)
        else:
            chart_type = "bar"
            x_axis = text_cols[0] if text_cols else columns[0]
            y_axis = numeric_cols[0] if numeric_cols else columns[1]
            x_vals = [r.get(x_axis) for r in rows]
            y_vals = [r.get(y_axis) for r in rows]
            data = [
                {
                    "x": x_vals,
                    "y": y_vals,
                    "type": "bar",
                    "marker": {"color": cls.CHART_PALETTE[0], "borderRadius": 4},
                    "name": y_axis.replace("_", " ").title(),
                }
            ]
            base_layout["xaxis"] = {"title": x_axis.replace("_", " ").title(), "gridcolor": "#e5e7eb"}
            base_layout["yaxis"] = {"title": y_axis.replace("_", " ").title(), "gridcolor": "#e5e7eb"}

        return ChartSpec(
            chart_type=chart_type,
            title=base_layout["title"]["text"],
            x_axis=str(x_axis) if x_axis else None,
            y_axis=str(y_axis) if y_axis else None,
            plotly_json={"data": data, "layout": base_layout},
        )
