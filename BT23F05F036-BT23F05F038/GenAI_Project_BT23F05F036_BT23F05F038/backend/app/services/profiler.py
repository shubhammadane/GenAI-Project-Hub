from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from app.models.schemas import ColumnProfile, TableProfile


def _clean_val(val: Any) -> Any:
    """Helper to convert pandas/numpy types to pure Python JSON-serializable types."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer, int)):
        return int(val)
    if isinstance(val, (np.floating, float)):
        return round(float(val), 4) if not np.isinf(val) else None
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return str(val)


def profile_dataframe(df: pd.DataFrame, table_name: str) -> TableProfile:
    """Profiles a pandas DataFrame returning schema types, nulls, unique counts, and preview."""
    total_rows = len(df)
    columns_profile: List[ColumnProfile] = []

    for col in df.columns:
        series = df[col]
        null_count = int(series.isna().sum())
        null_pct = round((null_count / total_rows * 100), 2) if total_rows > 0 else 0.0
        unique_vals = series.dropna().unique()
        unique_count = len(unique_vals)

        # Infer simplified SQL/DuckDB data type
        dtype_str = str(series.dtype).lower()
        if "int" in dtype_str:
            sql_type = "BIGINT"
        elif "float" in dtype_str:
            sql_type = "DOUBLE"
        elif "bool" in dtype_str:
            sql_type = "BOOLEAN"
        elif "datetime" in dtype_str or "date" in dtype_str:
            sql_type = "TIMESTAMP"
        else:
            sql_type = "VARCHAR"

        # Collect distinct sample values (useful for categorical columns)
        samples = [_clean_val(v) for v in unique_vals[:6]]

        # Min / Max calculation
        min_val: Optional[Any] = None
        max_val: Optional[Any] = None
        if len(unique_vals) > 0:
            try:
                if "int" in dtype_str or "float" in dtype_str:
                    min_val = _clean_val(series.min())
                    max_val = _clean_val(series.max())
                elif "date" in dtype_str:
                    min_val = _clean_val(series.min())
                    max_val = _clean_val(series.max())
            except Exception:
                pass

        columns_profile.append(
            ColumnProfile(
                name=str(col),
                data_type=sql_type,
                null_count=null_count,
                null_percentage=null_pct,
                unique_count=unique_count,
                sample_values=samples,
                min_value=min_val,
                max_value=max_val,
            )
        )

    # 5 preview rows
    preview_df = df.head(5)
    preview_rows: List[Dict[str, Any]] = []
    for _, row in preview_df.iterrows():
        preview_rows.append({str(k): _clean_val(v) for k, v in row.to_dict().items()})

    return TableProfile(
        table_name=table_name,
        row_count=total_rows,
        column_count=len(df.columns),
        columns=columns_profile,
        preview_rows=preview_rows,
    )
