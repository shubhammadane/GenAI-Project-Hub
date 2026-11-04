import pytest
from app.core.validator import SqlValidator


class TestSqlValidator:
    """Tests for SQL AST validation, injection prevention, and guardrail enforcement."""

    ALLOWED_TABLES = ["sales", "orders", "customers"]

    def test_valid_select_simple(self):
        sql = "SELECT order_id, sales, profit FROM sales"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is True
        assert "LIMIT 500" in result.sanitized_sql.upper()
        assert "sales" in result.referenced_tables

    def test_valid_select_aggregations_and_group(self):
        sql = "SELECT region, SUM(sales) AS total_sales FROM sales GROUP BY region ORDER BY total_sales DESC"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is True
        assert "LIMIT 500" in result.sanitized_sql.upper()

    def test_valid_with_cte(self):
        sql = """
        WITH high_value AS (
            SELECT customer_name, SUM(sales) AS total
            FROM sales
            GROUP BY customer_name
            HAVING SUM(sales) > 1000
        )
        SELECT * FROM high_value ORDER BY total DESC
        """
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is True
        assert "sales" in result.referenced_tables

    def test_respects_existing_valid_limit(self):
        sql = "SELECT * FROM sales LIMIT 25"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is True
        assert "LIMIT 25" in result.sanitized_sql.upper()

    def test_caps_excessive_limit(self):
        sql = "SELECT * FROM sales LIMIT 50000"
        result = SqlValidator.validate_and_sanitize(
            sql, allowed_tables=self.ALLOWED_TABLES, max_limit=10000
        )
        assert result.is_valid is True
        assert "LIMIT 10000" in result.sanitized_sql.upper()

    # --- MALICIOUS & REJECTED QUERIES ---

    def test_rejects_drop_table(self):
        sql = "DROP TABLE sales"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is False
        assert "Only SELECT or WITH" in result.error_message or "Forbidden operation" in result.error_message

    def test_rejects_delete(self):
        sql = "DELETE FROM sales WHERE sales < 10"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is False
        assert "Only SELECT or WITH" in result.error_message or "Forbidden operation" in result.error_message

    def test_rejects_update(self):
        sql = "UPDATE sales SET profit = 999999"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is False

    def test_rejects_insert(self):
        sql = "INSERT INTO sales VALUES (1, 'hack', 0)"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is False

    def test_rejects_alter(self):
        sql = "ALTER TABLE sales DROP COLUMN profit"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is False

    def test_rejects_multi_statement_sql_injection(self):
        sql = "SELECT * FROM sales; DROP TABLE customers;"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is False
        assert "Multi-statement" in result.error_message

    def test_rejects_multi_statement_benign(self):
        sql = "SELECT 1; SELECT 2;"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is False
        assert "Multi-statement" in result.error_message

    def test_rejects_pragma(self):
        sql = "PRAGMA table_info('sales')"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is False

    def test_rejects_read_csv_arbitrary_path(self):
        sql = "SELECT * FROM read_csv('/etc/passwd')"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is False
        assert "readcsv" in result.error_message.lower() or "read_csv" in result.error_message.lower()

    def test_rejects_read_csv_auto(self):
        sql = "SELECT * FROM read_csv_auto('C:\\secret.csv')"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is False
        assert "Forbidden function 'read_csv_auto'" in result.error_message

    def test_rejects_parquet_scan(self):
        sql = "SELECT * FROM scan_parquet('s3://confidential/dump.parquet')"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is False
        assert "Forbidden function 'scan_parquet'" in result.error_message

    def test_rejects_unwhitelisted_table(self):
        sql = "SELECT * FROM passwords_table"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is False
        assert "passwords_table" in result.error_message

    def test_rejects_empty_sql(self):
        result = SqlValidator.validate_and_sanitize("", allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is False
        assert "Empty" in result.error_message

    def test_rejects_malformed_syntax(self):
        sql = "SELECT FROM WHERE GROUP BY"
        result = SqlValidator.validate_and_sanitize(sql, allowed_tables=self.ALLOWED_TABLES)
        assert result.is_valid is False
