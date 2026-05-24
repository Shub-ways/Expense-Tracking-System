import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from contextlib import contextmanager
from logging_setup import setup_logger

logger = setup_logger('db_helper')
load_dotenv()

# ---------------------------------------------------------------------------
# Connection Pool — one pool shared across all requests (max 5 connections).
# This avoids the overhead of creating a new TCP connection per query.
# ---------------------------------------------------------------------------
_db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "expense_manager"),
}

# Lazy singleton — pool is created on first DB access, not at import time.
# This allows tests to import db_helper without a live MySQL instance.
_pool = None


def _get_pool():
    """Return the shared connection pool, creating it on first call."""
    global _pool
    if _pool is None:
        _pool = MySQLConnectionPool(pool_name="expense_pool", pool_size=5, **_db_config)
    return _pool


@contextmanager
def get_db_cursor(commit=False):
    """Context manager that borrows a connection from the pool, yields a
    dict cursor, and returns the connection to the pool on exit."""
    connection = _get_pool().get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        yield cursor
        if commit:
            connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()  # returns connection to pool


# ---------------------------------------------------------------------------
# Query functions
# ---------------------------------------------------------------------------

def fetch_expenses_for_date(expense_date):
    logger.info(f"fetch_expenses_for_date called with {expense_date}")
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM expenses WHERE expense_date = %s", (expense_date,)
        )
        return cursor.fetchall()


def delete_expenses_for_date(expense_date):
    logger.info(f"delete_expenses_for_date called with {expense_date}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "DELETE FROM expenses WHERE expense_date = %s", (expense_date,)
        )


def insert_expense(expense_date, amount, category, notes):
    logger.info(
        f"insert_expense called with date: {expense_date}, amount: {amount}, "
        f"category: {category}, notes: {notes}"
    )
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO expenses (expense_date, amount, category, notes) "
            "VALUES (%s, %s, %s, %s)",
            (expense_date, amount, category, notes),
        )


def fetch_expense_summary(start_date, end_date):
    logger.info(f"fetch_expense_summary called with start: {start_date} end: {end_date}")
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE expense_date BETWEEN %s AND %s
            GROUP BY category
            """,
            (start_date, end_date),
        )
        return cursor.fetchall()


def fetch_monthly_expenses():
    logger.info("fetch_monthly_expenses called")
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT DATE_FORMAT(expense_date, '%M') AS month,
                   MONTH(expense_date)              AS month_num,
                   SUM(amount)                      AS total
            FROM expenses
            GROUP BY month, month_num
            ORDER BY month_num
            """
        )
        rows = cursor.fetchall()

    grand_total = sum(row["total"] for row in rows)

    return {
        row["month"]: {
            "total": row["total"],
            "percentage": (row["total"] / grand_total * 100) if grand_total > 0 else 0,
        }
        for row in rows
    }


# ---------------------------------------------------------------------------
# Budget helpers
# ---------------------------------------------------------------------------

def fetch_budgets():
    """Return all budget limits as {category: monthly_limit}."""
    logger.info("fetch_budgets called")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT category, monthly_limit FROM budgets")
        rows = cursor.fetchall()
    return {row["category"]: row["monthly_limit"] for row in rows}


def upsert_budget(category, monthly_limit):
    """Insert or update the budget limit for a category."""
    logger.info(f"upsert_budget called: {category} → {monthly_limit}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO budgets (category, monthly_limit)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE monthly_limit = %s
            """,
            (category, monthly_limit, monthly_limit),
        )


def fetch_budget_vs_actual(year, month):
    """Return per-category spend vs budget for a given year/month."""
    logger.info(f"fetch_budget_vs_actual called: {year}-{month:02d}")
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT b.category,
                   b.monthly_limit,
                   COALESCE(SUM(e.amount), 0) AS spent
            FROM budgets b
            LEFT JOIN expenses e
                   ON b.category = e.category
                  AND YEAR(e.expense_date)  = %s
                  AND MONTH(e.expense_date) = %s
            GROUP BY b.category, b.monthly_limit
            """,
            (year, month),
        )
        return cursor.fetchall()


if __name__ == "__main__":
    expenses = fetch_expenses_for_date("2024-09-29")
    print(expenses)
    summary = fetch_expense_summary("2024-08-01", "2024-08-05")
    for record in summary:
        print(record)