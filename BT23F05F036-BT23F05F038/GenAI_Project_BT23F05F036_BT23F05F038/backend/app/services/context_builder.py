from typing import Any, Dict, List, Optional
import json
from app.models.schemas import TableProfile
from app.core.security import escape_data_for_prompt


def build_schema_prompt_context(
    profile: TableProfile,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Constructs an explicit, injection-resilient schema context block for the LLM.
    Includes column names, inferred types, distinct sample values for categorical columns,
    and 3 representative sample rows.
    """
    lines: List[str] = [
        f"TABLE NAME: {profile.table_name}",
        f"TOTAL ROWS: {profile.row_count}",
        "",
        "COLUMNS AND CONSTRAINTS:",
    ]

    for col in profile.columns:
        col_desc = f"- {col.name} ({col.data_type}): nulls={col.null_count} ({col.null_percentage}%)"
        if col.min_value is not None and col.max_value is not None:
            col_desc += f", range=[{col.min_value} to {col.max_value}]"
        if col.unique_count <= 15 and col.sample_values:
            # Low-cardinality categorical samples
            vals_str = ", ".join(f"'{escape_data_for_prompt(str(v))}'" for v in col.sample_values)
            col_desc += f", distinct_values=[{vals_str}]"
        elif col.sample_values:
            vals_str = ", ".join(f"'{escape_data_for_prompt(str(v))}'" for v in col.sample_values[:3])
            col_desc += f", sample_values=[{vals_str}]"
        lines.append(col_desc)

    lines.append("\nSAMPLE ROWS (First 3 rows as reference):")
    sample_rows = profile.preview_rows[:3]
    for idx, row in enumerate(sample_rows, 1):
        escaped_row = {k: escape_data_for_prompt(str(v)) if v is not None else None for k, v in row.items()}
        lines.append(f"Row {idx}: {json.dumps(escaped_row)}")

    if conversation_history:
        lines.append("\nPREVIOUS CONVERSATION CONTEXT (for follow-up questions):")
        for idx, item in enumerate(conversation_history[-4:], 1):
            q = item.get("question", "")
            sql = item.get("sql", "")
            lines.append(f"Q{idx}: {q}")
            if sql:
                lines.append(f"SQL{idx}: {sql}")

    return "\n".join(lines)
