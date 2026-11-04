import pandas as pd
from app.core.engine import session_manager


class TestEngine:
    """Tests for isolated DuckDB sessions, query timeouts, and execution safety."""

    def test_session_isolation(self):
        s1 = session_manager.get_or_create("session_1")
        s2 = session_manager.get_or_create("session_2")

        df1 = pd.DataFrame({"alpha": [1, 2, 3]})
        df2 = pd.DataFrame({"beta": [4, 5, 6]})

        s1.register_dataframe("tbl_one", df1)
        s2.register_dataframe("tbl_two", df2)

        # Session 1 has tbl_one but not tbl_two
        assert "tbl_one" in s1.list_tables()
        assert "tbl_two" not in s1.list_tables()

        # Session 2 has tbl_two but not tbl_one
        assert "tbl_two" in s2.list_tables()
        assert "tbl_one" not in s2.list_tables()

    def test_query_execution_success(self):
        session = session_manager.get_or_create("session_exec")
        df = pd.DataFrame({"x": [10, 20, 30], "y": ["a", "b", "c"]})
        session.register_dataframe("test_tbl", df)

        result = session.execute_query("SELECT SUM(x) AS total FROM test_tbl")
        assert result.error is None
        assert result.row_count == 1
        assert result.rows[0]["total"] == 60
        assert result.execution_time_ms >= 0

    def test_query_timeout_protection(self):
        session = session_manager.get_or_create("session_timeout")
        # DuckDB query that sleeps longer than timeout
        # Using timeout_seconds = 1
        result = session.execute_query(
            "SELECT count(*) FROM range(100000000) t1, range(1000) t2",
            timeout_seconds=1,
        )
        assert result.error is not None
        assert "timed out" in result.error.lower() or "timeout" in result.error.lower()
