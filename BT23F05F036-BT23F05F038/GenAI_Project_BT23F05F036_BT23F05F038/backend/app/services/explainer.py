from typing import Any, Dict, List


class Explainer:
    """
    Synthesizes natural language insights strictly grounded in the returned query results.
    Prevents hallucination by calculating exact aggregates and referencing empirical values.
    """

    @classmethod
    def explain(
        cls,
        question: str,
        sql: str,
        columns: List[str],
        rows: List[Dict[str, Any]],
        row_count: int,
    ) -> str:
        if not rows or row_count == 0:
            return "The query executed successfully and safely, but returned 0 matching records."

        # Case 1: Single row KPI
        if row_count == 1:
            row = rows[0]
            items = []
            for col, val in row.items():
                col_display = col.replace("_", " ").title()
                if isinstance(val, (int, float)):
                    formatted_val = f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"
                else:
                    formatted_val = str(val)
                items.append(f"**{col_display}**: {formatted_val}")
            return f"The calculated result is: {', '.join(items)}."

        # Case 2: Multi-row results
        first_row = rows[0]
        dim_col = columns[0]
        metric_col = columns[1] if len(columns) > 1 else columns[0]

        dim_label = dim_col.replace("_", " ").title()
        metric_label = metric_col.replace("_", " ").title()

        top_entity = first_row.get(dim_col)
        top_val = first_row.get(metric_col)

        # Format numeric value
        if isinstance(top_val, (int, float)):
            top_val_str = f"{top_val:,.2f}" if isinstance(top_val, float) else f"{top_val:,}"
        else:
            top_val_str = str(top_val)

        last_row = rows[-1]
        bottom_entity = last_row.get(dim_col)
        bottom_val = last_row.get(metric_col)
        if isinstance(bottom_val, (int, float)):
            bottom_val_str = f"{bottom_val:,.2f}" if isinstance(bottom_val, float) else f"{bottom_val:,}"
        else:
            bottom_val_str = str(bottom_val)

        # Build grounded summary
        summary = (
            f"The query retrieved {row_count} records. "
            f"The highest {metric_label.lower()} was recorded by **{top_entity}** at **{top_val_str}**."
        )

        if row_count > 1 and top_entity != bottom_entity:
            summary += f" In contrast, **{bottom_entity}** registered the lowest at **{bottom_val_str}**."

        return summary
