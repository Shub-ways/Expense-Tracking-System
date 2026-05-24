from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
import db_helper
from typing import List
from pydantic import BaseModel, field_validator, Field

# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

VALID_CATEGORIES = {"Rent", "Food", "Shopping", "Entertainment", "Other"}

class Expense(BaseModel):
    amount: float = Field(..., gt=0, description="Must be a positive number")
    category: str = Field(..., min_length=1, max_length=50)
    notes: str = Field("", max_length=255)

    @field_validator("category")
    @classmethod
    def category_must_be_valid(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of {sorted(VALID_CATEGORIES)}")
        return v


class DateRange(BaseModel):
    start_date: date
    end_date: date

    @field_validator("end_date")
    @classmethod
    def end_must_be_after_start(cls, v, info):
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be on or after start_date")
        return v


class BudgetItem(BaseModel):
    category: str = Field(..., min_length=1, max_length=50)
    monthly_limit: float = Field(..., gt=0)

    @field_validator("category")
    @classmethod
    def category_must_be_valid(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of {sorted(VALID_CATEGORIES)}")
        return v


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Expense Tracker API",
    description="REST API for managing personal expenses and budgets.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Expense Endpoints
# ---------------------------------------------------------------------------

@app.get("/expenses/{expense_date}", response_model=List[Expense], tags=["Expenses"])
def get_expenses(expense_date: date):
    """Retrieve all expenses logged for a specific date."""
    expenses = db_helper.fetch_expenses_for_date(expense_date)
    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses from the database.")
    return expenses


@app.post("/expenses/{expense_date}", tags=["Expenses"])
def add_or_update_expense(expense_date: date, expenses: List[Expense]):
    """Replace all expenses for a given date with the provided list."""
    db_helper.delete_expenses_for_date(expense_date)
    for expense in expenses:
        db_helper.insert_expense(expense_date, expense.amount, expense.category, expense.notes)
    return {"message": "Expenses updated successfully!"}


# ---------------------------------------------------------------------------
# Analytics Endpoints
# ---------------------------------------------------------------------------

@app.post("/analytics/", tags=["Analytics"])
def get_analytics(date_range: DateRange):
    """Get a spending breakdown by category for a given date range."""
    data = db_helper.fetch_expense_summary(date_range.start_date, date_range.end_date)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expense summary from the database.")

    total = sum(row["total"] for row in data)
    breakdown = {}
    for row in data:
        percentage = (row["total"] / total) * 100 if total != 0 else 0
        breakdown[row["category"]] = {
            "total": row["total"],
            "percentage": percentage,
        }
    return breakdown


@app.post("/analytics/month", tags=["Analytics"])
def get_analytics_by_month():
    """Get a month-by-month spending summary with percentages."""
    try:
        return db_helper.fetch_monthly_expenses()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Budget Endpoints
# ---------------------------------------------------------------------------

@app.get("/budgets/", tags=["Budget"])
def get_budgets():
    """Retrieve all category budget limits."""
    try:
        return db_helper.fetch_budgets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/budgets/", tags=["Budget"])
def set_budget(budget: BudgetItem):
    """Create or update a monthly budget limit for a category."""
    try:
        db_helper.upsert_budget(budget.category, budget.monthly_limit)
        return {"message": f"Budget for '{budget.category}' set to {budget.monthly_limit}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/budgets/vs-actual", tags=["Budget"])
def get_budget_vs_actual(year: int, month: int):
    """Return how much was spent vs the budget limit per category for a given month."""
    if not (1 <= month <= 12):
        raise HTTPException(status_code=422, detail="month must be between 1 and 12")
    try:
        rows = db_helper.fetch_budget_vs_actual(year, month)
        result = {}
        for row in rows:
            limit = float(row["monthly_limit"])
            spent = float(row["spent"])
            result[row["category"]] = {
                "monthly_limit": limit,
                "spent": spent,
                "remaining": limit - spent,
                "percentage_used": (spent / limit * 100) if limit > 0 else 0,
                "over_budget": spent > limit,
            }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))