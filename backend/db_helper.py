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
# User operations
# ---------------------------------------------------------------------------

def create_user(username, password_hash):
    """Insert a new user into the users table. Returns True on success, False otherwise."""
    logger.info(f"create_user called for username: {username}")
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash),
            )
        return True
    except mysql.connector.Error as e:
        logger.error(f"Error creating user {username}: {e}")
        return False


def fetch_user_by_username(username):
    """Retrieve user details by username. Returns None if not found."""
    logger.info(f"fetch_user_by_username called for username: {username}")
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT id, username, password_hash FROM users WHERE username = %s",
            (username,),
        )
        return cursor.fetchone()


# ---------------------------------------------------------------------------
# Query functions (scoped by user_id)
# ---------------------------------------------------------------------------

def fetch_expenses_for_date(user_id, expense_date):
    logger.info(f"fetch_expenses_for_date called for user {user_id} on {expense_date}")
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM expenses WHERE user_id = %s AND expense_date = %s",
            (user_id, expense_date),
        )
        return cursor.fetchall()


def delete_expenses_for_date(user_id, expense_date):
    logger.info(f"delete_expenses_for_date called for user {user_id} on {expense_date}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "DELETE FROM expenses WHERE user_id = %s AND expense_date = %s",
            (user_id, expense_date),
        )


def insert_expense(user_id, expense_date, amount, category, notes):
    logger.info(
        f"insert_expense called for user {user_id} with date: {expense_date}, "
        f"amount: {amount}, category: {category}, notes: {notes}"
    )
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO expenses (user_id, expense_date, amount, category, notes) "
            "VALUES (%s, %s, %s, %s, %s)",
            (user_id, expense_date, amount, category, notes),
        )


def fetch_expense_summary(user_id, start_date, end_date):
    logger.info(
        f"fetch_expense_summary called for user {user_id} with start: {start_date} end: {end_date}"
    )
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE user_id = %s AND expense_date BETWEEN %s AND %s
            GROUP BY category
            """,
            (user_id, start_date, end_date),
        )
        return cursor.fetchall()


def fetch_monthly_expenses(user_id):
    logger.info(f"fetch_monthly_expenses called for user {user_id}")
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT DATE_FORMAT(expense_date, '%M') AS month,
                   MONTH(expense_date)              AS month_num,
                   SUM(amount)                      AS total
            FROM expenses
            WHERE user_id = %s
            GROUP BY month, month_num
            ORDER BY month_num
            """,
            (user_id,),
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
# Budget helpers (scoped by user_id)
# ---------------------------------------------------------------------------

def fetch_budgets(user_id):
    """Return all budget limits for a specific user as {category: monthly_limit}."""
    logger.info(f"fetch_budgets called for user {user_id}")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT category, monthly_limit FROM budgets WHERE user_id = %s", (user_id,))
        rows = cursor.fetchall()
    return {row["category"]: row["monthly_limit"] for row in rows}


def upsert_budget(user_id, category, monthly_limit):
    """Insert or update the budget limit for a category and user."""
    logger.info(f"upsert_budget called for user {user_id}: {category} → {monthly_limit}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO budgets (user_id, category, monthly_limit)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE monthly_limit = %s
            """,
            (user_id, category, monthly_limit, monthly_limit),
        )


def fetch_budget_vs_actual(user_id, year, month):
    """Return per-category spend vs budget for a given user, year, and month."""
    logger.info(f"fetch_budget_vs_actual called for user {user_id}: {year}-{month:02d}")
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT b.category,
                   b.monthly_limit,
                   COALESCE(SUM(e.amount), 0) AS spent
            FROM budgets b
            LEFT JOIN expenses e
                   ON b.category = e.category
                  AND e.user_id = %s
                  AND YEAR(e.expense_date)  = %s
                  AND MONTH(e.expense_date) = %s
            WHERE b.user_id = %s
            GROUP BY b.category, b.monthly_limit
            """,
            (user_id, year, month, user_id),
        )
        return cursor.fetchall()