import pandas as pd
from app.services.profiler import profile_dataframe


class TestProfiler:
    """Tests for dataset profiling and column statistics computation."""

    def test_profile_basic_dataframe(self):
        data = {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", None, "Evan"],
            "score": [85.5, 92.0, 78.5, 88.0, 95.5],
            "active": [True, False, True, True, False],
        }
        df = pd.DataFrame(data)
        profile = profile_dataframe(df, "test_users")

        assert profile.table_name == "test_users"
        assert profile.row_count == 5
        assert profile.column_count == 4
        assert len(profile.columns) == 4
        assert len(profile.preview_rows) == 5

        # Check name column null count
        name_col = next(c for c in profile.columns if c.name == "name")
        assert name_col.null_count == 1
        assert name_col.null_percentage == 20.0
        assert name_col.unique_count == 4

        # Check score column min/max
        score_col = next(c for c in profile.columns if c.name == "score")
        assert score_col.min_value == 78.5
        assert score_col.max_value == 95.5

    def test_profile_empty_dataframe(self):
        df = pd.DataFrame({"col_a": [], "col_b": []})
        profile = profile_dataframe(df, "empty_table")
        assert profile.row_count == 0
        assert profile.column_count == 2
        assert len(profile.preview_rows) == 0
