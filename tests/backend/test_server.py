"""
Unit tests for the FastAPI backend using mocks.

These tests do NOT require a running MySQL instance — the database layer
(db_helper) is fully mocked using pytest-mock / unittest.mock.
Run with:  pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# The TestClient must import the app from the installed package path.
# Make sure PYTHONPATH includes the project root when running pytest.
from backend.server import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# GET /expenses/{date}
# ---------------------------------------------------------------------------

class TestGetExpenses:
    @patch("backend.server.db_helper.fetch_expenses_for_date")
    def test_returns_expenses_for_valid_date(self, mock_fetch):
        mock_fetch.return_value = [
            {"amount": 100.0, "category": "Food", "notes": "Lunch"}
        ]
        response = client.get("/expenses/2024-08-15")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "Food"
        mock_fetch.assert_called_once()

    @patch("backend.server.db_helper.fetch_expenses_for_date")
    def test_returns_empty_list_when_no_expenses(self, mock_fetch):
        mock_fetch.return_value = []
        response = client.get("/expenses/2024-01-01")
        assert response.status_code == 200
        assert response.json() == []

    @patch("backend.server.db_helper.fetch_expenses_for_date")
    def test_returns_500_on_db_failure(self, mock_fetch):
        mock_fetch.return_value = None
        response = client.get("/expenses/2024-08-15")
        assert response.status_code == 500
        assert "Failed to retrieve" in response.json()["detail"]

    def test_returns_422_for_invalid_date_format(self):
        response = client.get("/expenses/not-a-date")
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /expenses/{date}
# ---------------------------------------------------------------------------

class TestAddOrUpdateExpense:
    @patch("backend.server.db_helper.insert_expense")
    @patch("backend.server.db_helper.delete_expenses_for_date")
    def test_creates_expenses_successfully(self, mock_delete, mock_insert):
        payload = [{"amount": 50.0, "category": "Food", "notes": "Dinner"}]
        response = client.post("/expenses/2024-08-15", json=payload)
        assert response.status_code == 200
        assert response.json()["message"] == "Expenses updated successfully!"
        mock_delete.assert_called_once()
        mock_insert.assert_called_once()

    def test_rejects_negative_amount(self):
        payload = [{"amount": -10.0, "category": "Food", "notes": ""}]
        response = client.post("/expenses/2024-08-15", json=payload)
        assert response.status_code == 422

    def test_rejects_invalid_category(self):
        payload = [{"amount": 10.0, "category": "Invalid", "notes": ""}]
        response = client.post("/expenses/2024-08-15", json=payload)
        assert response.status_code == 422

    def test_rejects_zero_amount(self):
        payload = [{"amount": 0.0, "category": "Food", "notes": ""}]
        response = client.post("/expenses/2024-08-15", json=payload)
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /analytics/
# ---------------------------------------------------------------------------

class TestAnalytics:
    @patch("backend.server.db_helper.fetch_expense_summary")
    def test_returns_breakdown_with_percentages(self, mock_fetch):
        mock_fetch.return_value = [
            {"category": "Food", "total": 300.0},
            {"category": "Rent", "total": 700.0},
        ]
        payload = {"start_date": "2024-08-01", "end_date": "2024-08-31"}
        response = client.post("/analytics/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "Food" in data
        assert "Rent" in data
        assert abs(data["Food"]["percentage"] - 30.0) < 0.01
        assert abs(data["Rent"]["percentage"] - 70.0) < 0.01

    @patch("backend.server.db_helper.fetch_expense_summary")
    def test_handles_empty_range(self, mock_fetch):
        mock_fetch.return_value = []
        payload = {"start_date": "2099-01-01", "end_date": "2099-12-31"}
        response = client.post("/analytics/", json=payload)
        assert response.status_code == 200
        assert response.json() == {}

    def test_rejects_end_before_start(self):
        payload = {"start_date": "2024-08-31", "end_date": "2024-08-01"}
        response = client.post("/analytics/", json=payload)
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /analytics/month
# ---------------------------------------------------------------------------

class TestMonthlyAnalytics:
    @patch("backend.server.db_helper.fetch_monthly_expenses")
    def test_returns_monthly_data(self, mock_fetch):
        mock_fetch.return_value = {
            "August": {"total": 1000.0, "percentage": 100.0}
        }
        response = client.post("/analytics/month", json={})
        assert response.status_code == 200
        data = response.json()
        assert "August" in data
        assert data["August"]["total"] == 1000.0


# ---------------------------------------------------------------------------
# Budget endpoints
# ---------------------------------------------------------------------------

class TestBudget:
    @patch("backend.server.db_helper.fetch_budgets")
    def test_get_budgets_returns_dict(self, mock_fetch):
        mock_fetch.return_value = {"Food": 3000.0, "Rent": 10000.0}
        response = client.get("/budgets/")
        assert response.status_code == 200
        assert response.json()["Food"] == 3000.0

    @patch("backend.server.db_helper.upsert_budget")
    def test_set_budget_success(self, mock_upsert):
        payload = {"category": "Food", "monthly_limit": 5000.0}
        response = client.post("/budgets/", json=payload)
        assert response.status_code == 200
        mock_upsert.assert_called_once_with("Food", 5000.0)

    def test_set_budget_invalid_category(self):
        payload = {"category": "Luxury", "monthly_limit": 500.0}
        response = client.post("/budgets/", json=payload)
        assert response.status_code == 422

    def test_set_budget_zero_limit_rejected(self):
        payload = {"category": "Food", "monthly_limit": 0.0}
        response = client.post("/budgets/", json=payload)
        assert response.status_code == 422

    @patch("backend.server.db_helper.fetch_budget_vs_actual")
    def test_budget_vs_actual_over_budget(self, mock_fetch):
        mock_fetch.return_value = [
            {"category": "Food", "monthly_limit": 1000.0, "spent": 1500.0}
        ]
        response = client.get("/budgets/vs-actual", params={"year": 2024, "month": 8})
        assert response.status_code == 200
        data = response.json()
        assert data["Food"]["over_budget"] is True
        assert data["Food"]["remaining"] == pytest.approx(-500.0)

    def test_budget_vs_actual_invalid_month(self):
        response = client.get("/budgets/vs-actual", params={"year": 2024, "month": 13})
        assert response.status_code == 422
