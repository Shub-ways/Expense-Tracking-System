"""
Unit tests for db_helper.py using mocks.

The MySQL connection pool and cursor are fully mocked — no live database
required. These tests verify that:
  - The correct SQL is executed with the correct parameters.
  - Return values are passed through unchanged.
  - Commits are triggered only on write operations.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from backend import db_helper
import mysql.connector

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class AsyncContextManagerMock:
    """Mock helper for async context managers (e.g. pool.acquire, conn.cursor)."""
    def __init__(self, target):
        self.target = target

    async def __aenter__(self):
        return self.target

    async def __aexit__(self, exc_type, exc, tb):
        pass


def make_mock_cursor(fetchall_return=None, fetchone_return=None):
    """Return a mock cursor pre-configured with async return values."""
    cursor = MagicMock()
    cursor.execute = AsyncMock()
    cursor.fetchall = AsyncMock(return_value=fetchall_return or [])
    cursor.fetchone = AsyncMock(return_value=fetchone_return)
    return cursor


def make_mock_connection(cursor):
    """Return a mock connection that yields the given cursor."""
    conn = MagicMock()
    conn.commit = AsyncMock()
    conn.rollback = AsyncMock()
    conn.cursor = MagicMock(return_value=AsyncContextManagerMock(cursor))
    return conn


def setup_mock_pool(mock_get_pool, cursor):
    """Setup mock get_pool to resolve to a mock pool/connection/cursor."""
    conn = make_mock_connection(cursor)
    mock_pool = MagicMock()
    mock_pool.acquire = MagicMock(return_value=AsyncContextManagerMock(conn))
    mock_get_pool.return_value = mock_pool
    return conn


# ---------------------------------------------------------------------------
# User operations
# ---------------------------------------------------------------------------

class TestUserHelpers:
    @patch("backend.db_helper.get_pool")
    async def test_create_user_success(self, mock_get_pool):
        cursor = make_mock_cursor()
        conn = setup_mock_pool(mock_get_pool, cursor)

        result = await db_helper.create_user("testuser", "hashed_pass")

        assert result is True
        cursor.execute.assert_called_once()
        sql = cursor.execute.call_args[0][0].upper()
        assert "INSERT INTO USERS" in sql
        params = cursor.execute.call_args[0][1]
        assert "testuser" in params
        assert "hashed_pass" in params
        conn.commit.assert_called_once()

    @patch("backend.db_helper.get_pool")
    async def test_create_user_duplicate_error(self, mock_get_pool):
        cursor = MagicMock()
        cursor.execute = AsyncMock(side_effect=mysql.connector.Error(msg="Duplicate entry"))
        conn = setup_mock_pool(mock_get_pool, cursor)

        result = await db_helper.create_user("testuser", "hashed_pass")

        assert result is False
        conn.rollback.assert_called_once()

    @patch("backend.db_helper.get_pool")
    async def test_fetch_user_by_username_returns_user(self, mock_get_pool):
        expected = {"id": 1, "username": "testuser", "password_hash": "hashed_pass"}
        cursor = make_mock_cursor(fetchone_return=expected)
        setup_mock_pool(mock_get_pool, cursor)

        result = await db_helper.fetch_user_by_username("testuser")

        assert result == expected
        cursor.execute.assert_called_once()
        sql = cursor.execute.call_args[0][0].upper()
        assert "SELECT" in sql
        assert "FROM USERS" in sql


# ---------------------------------------------------------------------------
# fetch_expenses_for_date
# ---------------------------------------------------------------------------

class TestFetchExpensesForDate:
    @patch("backend.db_helper.get_pool")
    async def test_returns_expenses_from_db(self, mock_get_pool):
        expected = [{"amount": 10.0, "category": "Shopping", "notes": "Bought potatoes"}]
        cursor = make_mock_cursor(fetchall_return=expected)
        setup_mock_pool(mock_get_pool, cursor)

        result = await db_helper.fetch_expenses_for_date(1, "2024-08-15")

        assert result == expected
        cursor.execute.assert_called_once()
        args = cursor.execute.call_args[0]
        assert args[1][0] == 1
        assert args[1][1] == "2024-08-15"

    @patch("backend.db_helper.get_pool")
    async def test_returns_empty_list_for_unknown_date(self, mock_get_pool):
        cursor = make_mock_cursor(fetchall_return=[])
        setup_mock_pool(mock_get_pool, cursor)

        result = await db_helper.fetch_expenses_for_date(1, "9999-08-15")

        assert result == []

    @patch("backend.db_helper.get_pool")
    async def test_selects_by_expense_date(self, mock_get_pool):
        cursor = make_mock_cursor()
        setup_mock_pool(mock_get_pool, cursor)

        await db_helper.fetch_expenses_for_date(1, "2024-08-15")

        sql = cursor.execute.call_args[0][0].upper()
        assert "SELECT" in sql
        assert "USER_ID" in sql
        assert "EXPENSE_DATE" in sql


# ---------------------------------------------------------------------------
# delete_expenses_for_date
# ---------------------------------------------------------------------------

class TestDeleteExpensesForDate:
    @patch("backend.db_helper.get_pool")
    async def test_executes_delete_with_correct_date(self, mock_get_pool):
        cursor = make_mock_cursor()
        setup_mock_pool(mock_get_pool, cursor)

        await db_helper.delete_expenses_for_date(1, "2024-08-15")

        sql = cursor.execute.call_args[0][0].upper()
        assert "DELETE" in sql
        args = cursor.execute.call_args[0][1]
        assert args[0] == 1
        assert args[1] == "2024-08-15"

    @patch("backend.db_helper.get_pool")
    async def test_commits_the_transaction(self, mock_get_pool):
        cursor = make_mock_cursor()
        conn = setup_mock_pool(mock_get_pool, cursor)

        await db_helper.delete_expenses_for_date(1, "2024-08-15")

        conn.commit.assert_called_once()


# ---------------------------------------------------------------------------
# insert_expense
# ---------------------------------------------------------------------------

class TestInsertExpense:
    @patch("backend.db_helper.get_pool")
    async def test_inserts_with_correct_values(self, mock_get_pool):
        cursor = make_mock_cursor()
        setup_mock_pool(mock_get_pool, cursor)

        await db_helper.insert_expense(1, "2024-08-15", 150.0, "Food", "Lunch")

        sql = cursor.execute.call_args[0][0].upper()
        assert "INSERT" in sql
        params = cursor.execute.call_args[0][1]
        assert params[0] == 1
        assert params[1] == "2024-08-15"
        assert params[2] == 150.0
        assert params[3] == "Food"
        assert params[4] == "Lunch"

    @patch("backend.db_helper.get_pool")
    async def test_commits_after_insert(self, mock_get_pool):
        cursor = make_mock_cursor()
        conn = setup_mock_pool(mock_get_pool, cursor)

        await db_helper.insert_expense(1, "2024-08-15", 50.0, "Shopping", "")

        conn.commit.assert_called_once()


# ---------------------------------------------------------------------------
# fetch_expense_summary
# ---------------------------------------------------------------------------

class TestFetchExpenseSummary:
    @patch("backend.db_helper.get_pool")
    async def test_returns_summary_rows(self, mock_get_pool):
        expected = [{"category": "Food", "total": 300.0}]
        cursor = make_mock_cursor(fetchall_return=expected)
        setup_mock_pool(mock_get_pool, cursor)

        result = await db_helper.fetch_expense_summary(1, "2024-08-01", "2024-08-31")

        assert result == expected

    @patch("backend.db_helper.get_pool")
    async def test_returns_empty_for_future_date_range(self, mock_get_pool):
        cursor = make_mock_cursor(fetchall_return=[])
        setup_mock_pool(mock_get_pool, cursor)

        result = await db_helper.fetch_expense_summary(1, "2099-01-01", "2099-12-31")

        assert result == []

    @patch("backend.db_helper.get_pool")
    async def test_passes_date_range_to_query(self, mock_get_pool):
        cursor = make_mock_cursor()
        setup_mock_pool(mock_get_pool, cursor)

        await db_helper.fetch_expense_summary(1, "2024-08-01", "2024-08-31")

        params = cursor.execute.call_args[0][1]
        assert params[0] == 1
        assert params[1] == "2024-08-01"
        assert params[2] == "2024-08-31"


# ---------------------------------------------------------------------------
# fetch_monthly_expenses
# ---------------------------------------------------------------------------

class TestFetchMonthlyExpenses:
    @patch("backend.db_helper.get_pool")
    async def test_calculates_percentages_correctly(self, mock_get_pool):
        rows = [
            {"month": "August",    "month_num": 8,  "total": 1000.0},
            {"month": "September", "month_num": 9,  "total": 3000.0},
        ]
        cursor = make_mock_cursor(fetchall_return=rows)
        setup_mock_pool(mock_get_pool, cursor)

        result = await db_helper.fetch_monthly_expenses(1)

        assert result["August"]["total"] == 1000.0
        assert result["September"]["total"] == 3000.0
        assert abs(result["August"]["percentage"] - 25.0) < 0.01
        assert abs(result["September"]["percentage"] - 75.0) < 0.01

    @patch("backend.db_helper.get_pool")
    async def test_returns_empty_dict_when_no_data(self, mock_get_pool):
        cursor = make_mock_cursor(fetchall_return=[])
        setup_mock_pool(mock_get_pool, cursor)

        result = await db_helper.fetch_monthly_expenses(1)

        assert result == {}


# ---------------------------------------------------------------------------
# Budget helpers
# ---------------------------------------------------------------------------

class TestBudgetHelpers:
    @patch("backend.db_helper.get_pool")
    async def test_fetch_budgets_returns_dict(self, mock_get_pool):
        rows = [
            {"category": "Food", "monthly_limit": 3000.0},
            {"category": "Rent", "monthly_limit": 10000.0},
        ]
        cursor = make_mock_cursor(fetchall_return=rows)
        setup_mock_pool(mock_get_pool, cursor)

        result = await db_helper.fetch_budgets(1)

        assert result == {"Food": 3000.0, "Rent": 10000.0}

    @patch("backend.db_helper.get_pool")
    async def test_upsert_budget_commits(self, mock_get_pool):
        cursor = make_mock_cursor()
        conn = setup_mock_pool(mock_get_pool, cursor)

        await db_helper.upsert_budget(1, "Food", 5000.0)

        conn.commit.assert_called_once()
        sql = cursor.execute.call_args[0][0].upper()
        assert "INSERT" in sql
        params = cursor.execute.call_args[0][1]
        assert params[0] == 1
        assert params[1] == "Food"
        assert params[2] == 5000.0

    @patch("backend.db_helper.get_pool")
    async def test_fetch_budget_vs_actual_returns_rows(self, mock_get_pool):
        rows = [{"category": "Food", "monthly_limit": 3000.0, "spent": 1500.0}]
        cursor = make_mock_cursor(fetchall_return=rows)
        setup_mock_pool(mock_get_pool, cursor)

        result = await db_helper.fetch_budget_vs_actual(1, 2024, 8)

        assert result == rows