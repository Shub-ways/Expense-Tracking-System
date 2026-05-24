from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from typing import List
from pydantic import BaseModel, field_validator, Field
import db_helper
import auth

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


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=50)


class UserLogin(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Expense Tracker API",
    description="REST API for managing personal expenses and budgets with JWT Authentication.",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Authentication Endpoints
# ---------------------------------------------------------------------------

@app.post("/auth/register", tags=["Authentication"])
def register_user(user: UserRegister):
    """Register a new user account."""
    existing = db_helper.fetch_user_by_username(user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username is already taken.")
    
    hashed = auth.hash_password(user.password)
    success = db_helper.create_user(user.username, hashed)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create user account.")
    
    return {"message": "User registered successfully!"}


@app.post("/auth/login", tags=["Authentication"])
def login_user(credentials: UserLogin):
    """Log in to retrieve an access token."""
    user = db_helper.fetch_user_by_username(credentials.username)
    if not user or not auth.verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    token = auth.create_access_token({"user_id": user["id"], "username": user["username"]})
    return {"access_token": token, "token_type": "bearer"}


# ---------------------------------------------------------------------------
# Expense Endpoints
# ---------------------------------------------------------------------------

@app.get("/expenses/{expense_date}", response_model=List[Expense], tags=["Expenses"])
def get_expenses(expense_date: date, current_user: dict = Depends(auth.get_current_user)):
    """Retrieve all expenses logged for a specific date (authenticated)."""
    expenses = db_helper.fetch_expenses_for_date(current_user["id"], expense_date)
    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses from the database.")
    return expenses


@app.post("/expenses/{expense_date}", tags=["Expenses"])
def add_or_update_expense(
    expense_date: date, expenses: List[Expense], current_user: dict = Depends(auth.get_current_user)
):
    """Replace all expenses for a given date with the provided list (authenticated)."""
    db_helper.delete_expenses_for_date(current_user["id"], expense_date)
    for expense in expenses:
        db_helper.insert_expense(
            current_user["id"], expense_date, expense.amount, expense.category, expense.notes
        )
    return {"message": "Expenses updated successfully!"}


# ---------------------------------------------------------------------------
# Analytics Endpoints
# ---------------------------------------------------------------------------

@app.post("/analytics/", tags=["Analytics"])
def get_analytics(date_range: DateRange, current_user: dict = Depends(auth.get_current_user)):
    """Get a spending breakdown by category for a given date range (authenticated)."""
    data = db_helper.fetch_expense_summary(current_user["id"], date_range.start_date, date_range.end_date)
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
def get_analytics_by_month(current_user: dict = Depends(auth.get_current_user)):
    """Get a month-by-month spending summary with percentages (authenticated)."""
    try:
        return db_helper.fetch_monthly_expenses(current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Budget Endpoints
# ---------------------------------------------------------------------------

@app.get("/budgets/", tags=["Budget"])
def get_budgets(current_user: dict = Depends(auth.get_current_user)):
    """Retrieve all category budget limits (authenticated)."""
    try:
        return db_helper.fetch_budgets(current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/budgets/", tags=["Budget"])
def set_budget(budget: BudgetItem, current_user: dict = Depends(auth.get_current_user)):
    """Create or update a monthly budget limit for a category (authenticated)."""
    try:
        db_helper.upsert_budget(current_user["id"], budget.category, budget.monthly_limit)
        return {"message": f"Budget for '{budget.category}' set to {budget.monthly_limit}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/budgets/vs-actual", tags=["Budget"])
def get_budget_vs_actual(year: int, month: int, current_user: dict = Depends(auth.get_current_user)):
    """Return how much was spent vs the budget limit per category for a given month (authenticated)."""
    if not (1 <= month <= 12):
        raise HTTPException(status_code=422, detail="month must be between 1 and 12")
    try:
        rows = db_helper.fetch_budget_vs_actual(current_user["id"], year, month)
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