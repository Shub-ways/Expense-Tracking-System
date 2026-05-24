"""
Unit tests for db_helper.py using mocks.

The MySQL connection pool and cursor are fully mocked — no live database
required. These tests verify that:
  - The correct SQL is executed with the correct parameters.
  - Return values are passed through unchanged.
  - Commits are triggered only on write operations.
"""
import pytest
from unittest.mock import patch, MagicMock, call
from backend import db_helper


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_mock_cursor(fetchall_return=None, fetchone_return=None):
    """Return a mock cursor pre-configured with return values."""
    cursor = MagicMock()
    cursor.fetchall.return_value = fetchall_return or []
    cursor.fetchone.return_value = fetchone_return
    return cursor


def make_mock_connection(cursor):
    """Return a mock connection that yields the given cursor."""
    conn = MagicMock()
    conn.cursor.return_value = cursor
    return conn


# ---------------------------------------------------------------------------
# fetch_expenses_for_date
# ---------------------------------------------------------------------------

class TestFetchExpensesForDate:
    @patch("backend.db_helper._get_pool")
    def test_returns_expenses_from_db(self, mock_get_pool):
        expected = [{"amount": 10.0, "category": "Shopping", "notes": "Bought potatoes"}]
        cursor = make_mock_cursor(fetchall_return=expected)
        mock_get_pool.return_value.get_connection.return_value = make_mock_connection(cursor)

        result = db_helper.fetch_expenses_for_date("2024-08-15")

        assert result == expected
        cursor.execute.assert_called_once()
        # Verify the date parameter was passed
        args = cursor.execute.call_args[0]
        assert "2024-08-15" in args[1]

    @patch("backend.db_helper._get_pool")
    def test_returns_empty_list_for_unknown_date(self, mock_get_pool):
        cursor = make_mock_cursor(fetchall_return=[])
        mock_get_pool.return_value.get_connection.return_value = make_mock_connection(cursor)

        result = db_helper.fetch_expenses_for_date("9999-08-15")

        assert result == []

    @patch("backend.db_helper._get_pool")
    def test_selects_by_expense_date(self, mock_get_pool):
        cursor = make_mock_cursor()
        mock_get_pool.return_value.get_connection.return_value = make_mock_connection(cursor)

        db_helper.fetch_expenses_for_date("2024-08-15")

        sql = cursor.execute.call_args[0][0].upper()
        assert "SELECT" in sql
        assert "EXPENSE_DATE" in sql


# ---------------------------------------------------------------------------
# delete_expenses_for_date
# ---------------------------------------------------------------------------

class TestDeleteExpensesForDate:
    @patch("backend.db_helper._get_pool")
    def test_executes_delete_with_correct_date(self, mock_get_pool):
        cursor = make_mock_cursor()
        conn = make_mock_connection(cursor)
        mock_get_pool.return_value.get_connection.return_value = conn

        db_helper.delete_expenses_for_date("2024-08-15")

        sql = cursor.execute.call_args[0][0].upper()
        assert "DELETE" in sql
        args = cursor.execute.call_args[0][1]
        assert "2024-08-15" in args

    @patch("backend.db_helper._get_pool")
    def test_commits_the_transaction(self, mock_get_pool):
        cursor = make_mock_cursor()
        conn = make_mock_connection(cursor)
        mock_get_pool.return_value.get_connection.return_value = conn

        db_helper.delete_expenses_for_date("2024-08-15")

        conn.commit.assert_called_once()


# ---------------------------------------------------------------------------
# insert_expense
# ---------------------------------------------------------------------------

class TestInsertExpense:
    @patch("backend.db_helper._get_pool")
    def test_inserts_with_correct_values(self, mock_get_pool):
        cursor = make_mock_cursor()
        conn = make_mock_connection(cursor)
        mock_get_pool.return_value.get_connection.return_value = conn

        db_helper.insert_expense("2024-08-15", 150.0, "Food", "Lunch")

        sql = cursor.execute.call_args[0][0].upper()
        assert "INSERT" in sql
        params = cursor.execute.call_args[0][1]
        assert "2024-08-15" in params
        assert 150.0 in params
        assert "Food" in params
        assert "Lunch" in params

    @patch("backend.db_helper._get_pool")
    def test_commits_after_insert(self, mock_get_pool):
        cursor = make_mock_cursor()
        conn = make_mock_connection(cursor)
        mock_get_pool.return_value.get_connection.return_value = conn

        db_helper.insert_expense("2024-08-15", 50.0, "Shopping", "")

        conn.commit.assert_called_once()


# ---------------------------------------------------------------------------
# fetch_expense_summary
# ---------------------------------------------------------------------------

class TestFetchExpenseSummary:
    @patch("backend.db_helper._get_pool")
    def test_returns_summary_rows(self, mock_get_pool):
        expected = [{"category": "Food", "total": 300.0}]
        cursor = make_mock_cursor(fetchall_return=expected)
        mock_get_pool.return_value.get_connection.return_value = make_mock_connection(cursor)

        result = db_helper.fetch_expense_summary("2024-08-01", "2024-08-31")

        assert result == expected

    @patch("backend.db_helper._get_pool")
    def test_returns_empty_for_future_date_range(self, mock_get_pool):
        cursor = make_mock_cursor(fetchall_return=[])
        mock_get_pool.return_value.get_connection.return_value = make_mock_connection(cursor)

        result = db_helper.fetch_expense_summary("2099-01-01", "2099-12-31")

        assert result == []

    @patch("backend.db_helper._get_pool")
    def test_passes_date_range_to_query(self, mock_get_pool):
        cursor = make_mock_cursor()
        mock_get_pool.return_value.get_connection.return_value = make_mock_connection(cursor)

        db_helper.fetch_expense_summary("2024-08-01", "2024-08-31")

        params = cursor.execute.call_args[0][1]
        assert "2024-08-01" in params
        assert "2024-08-31" in params


# ---------------------------------------------------------------------------
# fetch_monthly_expenses
# ---------------------------------------------------------------------------

class TestFetchMonthlyExpenses:
    @patch("backend.db_helper._get_pool")
    def test_calculates_percentages_correctly(self, mock_get_pool):
        rows = [
            {"month": "August",    "month_num": 8,  "total": 1000.0},
            {"month": "September", "month_num": 9,  "total": 3000.0},
        ]
        cursor = make_mock_cursor(fetchall_return=rows)
        mock_get_pool.return_value.get_connection.return_value = make_mock_connection(cursor)

        result = db_helper.fetch_monthly_expenses()

        assert result["August"]["total"] == 1000.0
        assert result["September"]["total"] == 3000.0
        assert abs(result["August"]["percentage"] - 25.0) < 0.01
        assert abs(result["September"]["percentage"] - 75.0) < 0.01

    @patch("backend.db_helper._get_pool")
    def test_returns_empty_dict_when_no_data(self, mock_get_pool):
        cursor = make_mock_cursor(fetchall_return=[])
        mock_get_pool.return_value.get_connection.return_value = make_mock_connection(cursor)

        result = db_helper.fetch_monthly_expenses()

        assert result == {}


# ---------------------------------------------------------------------------
# Budget helpers
# ---------------------------------------------------------------------------

class TestBudgetHelpers:
    @patch("backend.db_helper._get_pool")
    def test_fetch_budgets_returns_dict(self, mock_get_pool):
        rows = [
            {"category": "Food", "monthly_limit": 3000.0},
            {"category": "Rent", "monthly_limit": 10000.0},
        ]
        cursor = make_mock_cursor(fetchall_return=rows)
        mock_get_pool.return_value.get_connection.return_value = make_mock_connection(cursor)

        result = db_helper.fetch_budgets()

        assert result == {"Food": 3000.0, "Rent": 10000.0}

    @patch("backend.db_helper._get_pool")
    def test_upsert_budget_commits(self, mock_get_pool):
        cursor = make_mock_cursor()
        conn = make_mock_connection(cursor)
        mock_get_pool.return_value.get_connection.return_value = conn

        db_helper.upsert_budget("Food", 5000.0)

        conn.commit.assert_called_once()
        sql = cursor.execute.call_args[0][0].upper()
        assert "INSERT" in sql

    @patch("backend.db_helper._get_pool")
    def test_fetch_budget_vs_actual_returns_rows(self, mock_get_pool):
        rows = [{"category": "Food", "monthly_limit": 3000.0, "spent": 1500.0}]
        cursor = make_mock_cursor(fetchall_return=rows)
        mock_get_pool.return_value.get_connection.return_value = make_mock_connection(cursor)

        result = db_helper.fetch_budget_vs_actual(2024, 8)

        assert result == rows