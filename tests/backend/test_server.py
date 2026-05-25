"""
Unit tests for the FastAPI backend using mocks.

These tests do NOT require a running MySQL instance — the database layer
(db_helper) is fully mocked using pytest-mock / unittest.mock.
Run with:  pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.server import app
import auth

# ---------------------------------------------------------------------------
# Setup dependency override for authentication
# ---------------------------------------------------------------------------

def override_get_current_user():
    return {"id": 1, "username": "testuser"}

# Apply the override to all endpoints in this test module
app.dependency_overrides[auth.get_current_user] = override_get_current_user

client = TestClient(app)


# ---------------------------------------------------------------------------
# POST /auth/register & /auth/login
# ---------------------------------------------------------------------------

class TestAuthEndpoints:
    @patch("backend.server.db_helper.create_user")
    @patch("backend.server.db_helper.fetch_user_by_username")
    def test_register_user_success(self, mock_fetch, mock_create):
        mock_fetch.return_value = None
        mock_create.return_value = True

        payload = {"username": "newuser", "email": "newuser@example.com", "password": "password123"}
        response = client.post("/auth/register", json=payload)

        assert response.status_code == 200
        assert response.json()["message"] == "User registered successfully!"
        mock_fetch.assert_called_once_with("newuser")
        mock_create.assert_called_once()

    @patch("backend.server.db_helper.fetch_user_by_username")
    def test_register_user_already_exists(self, mock_fetch):
        mock_fetch.return_value = {"id": 1, "username": "existinguser", "password_hash": "hash"}

        payload = {"username": "existinguser", "email": "existing@example.com", "password": "password123"}
        response = client.post("/auth/register", json=payload)

        assert response.status_code == 400
        assert "taken" in response.json()["detail"].lower()

    @patch("backend.server.db_helper.fetch_user_by_username")
    @patch("auth.verify_password")
    def test_login_user_success(self, mock_verify, mock_fetch):
        mock_fetch.return_value = {"id": 1, "username": "testuser", "password_hash": "hashed_pass"}
        mock_verify.return_value = True

        payload = {"username": "testuser", "password": "password123"}
        response = client.post("/auth/login", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @patch("backend.server.db_helper.fetch_user_by_username")
    def test_login_user_not_found(self, mock_fetch):
        mock_fetch.return_value = None

        payload = {"username": "unknown", "password": "password123"}
        response = client.post("/auth/login", json=payload)

        assert response.status_code == 401
        assert "Invalid username" in response.json()["detail"]


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
        from datetime import date
        mock_fetch.assert_called_once_with(1, date(2024, 8, 15))

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
        mock_upsert.assert_called_once_with(1, "Food", 5000.0)

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


# ---------------------------------------------------------------------------
# New Enhancements (Currency & Search)
# ---------------------------------------------------------------------------

class TestCurrencyPreferences:
    @patch("backend.server.db_helper.fetch_user_by_username")
    def test_get_currency_success(self, mock_fetch):
        mock_fetch.return_value = {"id": 1, "username": "testuser", "password_hash": "hash", "currency": "$"}
        response = client.get("/auth/currency")
        assert response.status_code == 200
        assert response.json()["currency"] == "$"

    @patch("backend.server.db_helper.update_user_currency")
    def test_update_currency_success(self, mock_update):
        mock_update.return_value = True
        payload = {"currency": "€"}
        response = client.put("/auth/currency", json=payload)
        assert response.status_code == 200
        assert response.json()["message"] == "Currency preference updated successfully!"
        mock_update.assert_called_once_with(1, "€")


class TestSearchExpenses:
    @patch("backend.server.db_helper.fetch_expenses_search")
    def test_search_expenses_success(self, mock_search):
        mock_search.return_value = [
            {"id": 10, "expense_date": "2024-08-15", "amount": 150.0, "category": "Food", "notes": "Pizza party"}
        ]
        params = {
            "start_date": "2024-08-01",
            "end_date": "2024-08-31",
            "category": "Food",
            "notes_query": "Pizza",
            "min_amount": 100.0,
            "max_amount": 200.0,
        }
        response = client.get("/expenses/search/all", params=params)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["notes"] == "Pizza party"
        from datetime import date
        mock_search.assert_called_once_with(1, date(2024, 8, 1), date(2024, 8, 31), "Food", "Pizza", 100.0, 200.0)

