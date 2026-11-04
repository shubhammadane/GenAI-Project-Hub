from typing import List, Optional, Set
import sqlglot
from sqlglot import exp
from app.models.schemas import SqlValidationResult


class SqlValidator:
    """
    Validates and sanitizes SQL queries using sqlglot AST parsing.
    Enforces strict read-only guarantees:
    - Exactly one SELECT or WITH ... SELECT statement
    - Blocks DDL/DML (DROP, INSERT, UPDATE, DELETE, ALTER, CREATE, COPY, ATTACH, etc.)
    - Blocks PRAGMA commands and file/network scan functions (read_csv, read_parquet, httpfs, etc.)
    - Verifies referenced tables against an allowed whitelist (respecting CTE names)
    - Enforces row LIMIT injection and ceiling caps
    """

    FORBIDDEN_FUNCTIONS: Set[str] = {
        "read_csv",
        "read_csv_auto",
        "read_parquet",
        "read_json",
        "read_json_auto",
        "read_text",
        "scan_csv",
        "scan_parquet",
        "httpfs",
        "load",
        "install",
        "write_csv",
        "copy",
        "system",
        "duckdb_settings",
        "query_table",
    }

    FORBIDDEN_EXPRESSIONS = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Create,
        exp.Alter,
        exp.Command,
        exp.Pragma,
        exp.Kill,
        exp.Transaction,
        exp.Commit,
        exp.Rollback,
        exp.ReadCSV,
        exp.ReadParquet,
    )

    @classmethod
    def validate_and_sanitize(
        cls,
        sql: str,
        allowed_tables: Optional[List[str]] = None,
        default_limit: int = 500,
        max_limit: int = 10000,
    ) -> SqlValidationResult:
        if not sql or not sql.strip():
            return SqlValidationResult(is_valid=False, error_message="Empty SQL statement.")

        raw_sql = sql.strip()

        # Parse statements
        try:
            statements = sqlglot.parse(raw_sql, read="duckdb")
        except Exception as e:
            return SqlValidationResult(
                is_valid=False,
                error_message=f"SQL syntax error: {str(e)}",
            )

        if not statements or len(statements) == 0:
            return SqlValidationResult(is_valid=False, error_message="No valid SQL statements found.")

        # Ensure single statement
        if len(statements) > 1:
            return SqlValidationResult(
                is_valid=False,
                error_message="Multi-statement queries are forbidden. Submit a single SELECT statement.",
            )

        stmt = statements[0]
        if stmt is None:
            return SqlValidationResult(is_valid=False, error_message="Malformed SQL statement.")

        # Check statement root type
        if not (isinstance(stmt, (exp.Select, exp.Union)) or (isinstance(stmt, exp.Expression) and stmt.find(exp.Select))):
            return SqlValidationResult(
                is_valid=False,
                error_message=f"Only SELECT or WITH queries are permitted. Found statement type: {type(stmt).__name__}.",
            )

        # Check for forbidden AST nodes
        for node in stmt.walk():
            if isinstance(node, cls.FORBIDDEN_EXPRESSIONS):
                node_name = type(node).__name__
                if isinstance(node, (exp.ReadCSV, exp.ReadParquet)):
                    return SqlValidationResult(
                        is_valid=False,
                        error_message=f"Forbidden function '{node_name}'. External file and system functions are disabled.",
                    )
                return SqlValidationResult(
                    is_valid=False,
                    error_message=f"Forbidden operation '{node_name}'. Only read-only SELECT queries are allowed.",
                )

            # Check for forbidden function calls
            if isinstance(node, (exp.Anonymous, exp.Func)):
                func_name = node.name.lower() if hasattr(node, "name") and node.name else ""
                key_name = getattr(node, "key", "").lower()
                if (
                    func_name in cls.FORBIDDEN_FUNCTIONS
                    or key_name in cls.FORBIDDEN_FUNCTIONS
                    or func_name.startswith("read_")
                    or func_name.startswith("scan_")
                ):
                    return SqlValidationResult(
                        is_valid=False,
                        error_message=f"Forbidden function '{func_name or key_name}'. External file and system functions are disabled.",
                    )

        # Collect CTE names (so local CTEs aren't flagged as unapproved tables)
        cte_names: Set[str] = {c.alias_or_name.lower() for c in stmt.find_all(exp.CTE) if c.alias_or_name}

        # Collect referenced tables
        referenced_tables: List[str] = []
        for table_node in stmt.find_all(exp.Table):
            t_name = table_node.name.lower() if table_node.name else ""
            if t_name and t_name not in cte_names:
                referenced_tables.append(t_name)

        # Whitelist verification
        if allowed_tables is not None:
            allowed_set = {t.lower() for t in allowed_tables}
            for t_name in referenced_tables:
                if t_name not in allowed_set:
                    return SqlValidationResult(
                        is_valid=False,
                        error_message=f"Table '{t_name}' is not accessible in this session. Allowed tables: {list(allowed_set)}",
                    )

        # Enforce LIMIT
        limit_clause = stmt.args.get("limit")
        if limit_clause is None:
            # Inject default limit
            stmt = stmt.limit(default_limit)
        else:
            try:
                limit_val_expr = limit_clause.expression
                if isinstance(limit_val_expr, exp.Literal) and limit_val_expr.is_int:
                    limit_val = int(limit_val_expr.this)
                    if limit_val > max_limit:
                        # Cap limit to maximum
                        stmt.set("limit", exp.Limit(expression=exp.Literal.number(max_limit)))
                    elif limit_val <= 0:
                        stmt.set("limit", exp.Limit(expression=exp.Literal.number(default_limit)))
            except Exception:
                stmt.set("limit", exp.Limit(expression=exp.Literal.number(default_limit)))

        sanitized = stmt.sql(dialect="duckdb")
        return SqlValidationResult(
            is_valid=True,
            sanitized_sql=sanitized,
            referenced_tables=list(set(referenced_tables)),
        )
