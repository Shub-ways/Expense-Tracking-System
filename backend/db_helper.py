import os
import asyncio
from dotenv import load_dotenv
import aiomysql
from aiomysql.cursors import DictCursor
from contextlib import asynccontextmanager
from logging_setup import setup_logger

logger = setup_logger('db_helper')
load_dotenv()

# ---------------------------------------------------------------------------
# Connection Pool — one pool shared across all requests.
# This avoids the overhead of creating a new TCP connection per query.
# ---------------------------------------------------------------------------
_db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306") or "3306"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "db": os.getenv("DB_NAME", "expense_manager"),
}

# Lazy thread-safe singleton pool
_pool = None
_pool_lock = asyncio.Lock()


async def get_pool():
    global _pool
    if _pool is None:
        async with _pool_lock:
            if _pool is None:
                import ssl
                # TiDB Serverless requires SSL
                use_ssl = ssl.create_default_context() if "tidbcloud.com" in _db_config["host"] else None
                _pool = await aiomysql.create_pool(
                    host=_db_config["host"],
                    port=_db_config["port"],
                    user=_db_config["user"],
                    password=_db_config["password"],
                    db=_db_config["db"],
                    ssl=use_ssl,
                    minsize=1,
                    maxsize=5,
                    pool_recycle=60,  # Recycle connections every 60 seconds to prevent TiDB idle drop
                    autocommit=False
                )
    return _pool


@asynccontextmanager
async def get_db_cursor(commit=False):
    """Async context manager that borrows a connection from the pool, yields a
    dict cursor, and returns the connection to the pool on exit."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        async with connection.cursor(DictCursor) as cursor:
            try:
                yield cursor
                if commit:
                    await connection.commit()
            except Exception:
                await connection.rollback()
                raise


# ---------------------------------------------------------------------------
# User operations
# ---------------------------------------------------------------------------

async def create_user(username, password_hash):
    """Insert a new user into the users table. Returns True on success, False otherwise."""
    logger.info(f"create_user called for username: {username}")
    try:
        async with get_db_cursor(commit=True) as cursor:
            await cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash),
            )
        return True
    except Exception as e:
        logger.error(f"Error creating user {username}: {e}")
        return False


async def fetch_user_by_username(username):
    """Retrieve user details by username. Returns None if not found."""
    logger.info(f"fetch_user_by_username called for username: {username}")
    async with get_db_cursor() as cursor:
        await cursor.execute(
            "SELECT id, username, email, password_hash, currency FROM users WHERE username = %s",
            (username,),
        )
        return await cursor.fetchone()


async def update_user_currency(user_id, currency):
    """Update preferred currency for a specific user. Returns True on success, False otherwise."""
    logger.info(f"update_user_currency called for user {user_id} -> {currency}")
    try:
        async with get_db_cursor(commit=True) as cursor:
            await cursor.execute(
                "UPDATE users SET currency = %s WHERE id = %s",
                (currency, user_id),
            )
        return True
    except Exception as e:
        logger.error(f"Error updating currency for user {user_id}: {e}")
        return False



# ---------------------------------------------------------------------------
# Query functions (scoped by user_id)
# ---------------------------------------------------------------------------

async def fetch_expenses_for_date(user_id, expense_date):
    logger.info(f"fetch_expenses_for_date called for user {user_id} on {expense_date}")
    async with get_db_cursor() as cursor:
        await cursor.execute(
            "SELECT * FROM expenses WHERE user_id = %s AND expense_date = %s",
            (user_id, expense_date),
        )
        return await cursor.fetchall()


async def delete_expenses_for_date(user_id, expense_date):
    logger.info(f"delete_expenses_for_date called for user {user_id} on {expense_date}")
    async with get_db_cursor(commit=True) as cursor:
        await cursor.execute(
            "DELETE FROM expenses WHERE user_id = %s AND expense_date = %s",
            (user_id, expense_date),
        )


async def insert_expense(user_id, expense_date, amount, category, notes):
    logger.info(
        f"insert_expense called for user {user_id} with date: {expense_date}, "
        f"amount: {amount}, category: {category}, notes: {notes}"
    )
    async with get_db_cursor(commit=True) as cursor:
        await cursor.execute(
            "INSERT INTO expenses (user_id, expense_date, amount, category, notes) "
            "VALUES (%s, %s, %s, %s, %s)",
            (user_id, expense_date, amount, category, notes),
        )


async def fetch_expense_summary(user_id, start_date, end_date):
    logger.info(
        f"fetch_expense_summary called for user {user_id} with start: {start_date} end: {end_date}"
    )
    async with get_db_cursor() as cursor:
        await cursor.execute(
            """
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE user_id = %s AND expense_date BETWEEN %s AND %s
            GROUP BY category
            """,
            (user_id, start_date, end_date),
        )
        return await cursor.fetchall()


async def fetch_monthly_expenses(user_id):
    logger.info(f"fetch_monthly_expenses called for user {user_id}")
    async with get_db_cursor() as cursor:
        await cursor.execute(
            """
            SELECT DATE_FORMAT(expense_date, '%%M') AS month,
                   MONTH(expense_date)              AS month_num,
                   SUM(amount)                      AS total
            FROM expenses
            WHERE user_id = %s
            GROUP BY month, month_num
            ORDER BY month_num
            """,
            (user_id,),
        )
        rows = await cursor.fetchall()

    grand_total = sum(row["total"] for row in rows)

    return {
        row["month"]: {
            "total": row["total"],
            "percentage": (row["total"] / grand_total * 100) if grand_total > 0 else 0,
        }
        for row in rows
    }


async def fetch_expenses_search(
    user_id,
    start_date=None,
    end_date=None,
    category=None,
    query=None,
    min_amount=None,
    max_amount=None,
):
    """Search and filter user expenses dynamically based on optional criteria."""
    logger.info(f"fetch_expenses_search called for user {user_id} with filters")
    sql = "SELECT id, expense_date, amount, category, notes FROM expenses WHERE user_id = %s"
    params = [user_id]

    if start_date:
        sql += " AND expense_date >= %s"
        params.append(start_date)
    if end_date:
        sql += " AND expense_date <= %s"
        params.append(end_date)
    if category:
        sql += " AND category = %s"
        params.append(category)
    if query:
        sql += " AND notes LIKE %s"
        params.append(f"%{query}%")
    if min_amount is not None:
        sql += " AND amount >= %s"
        params.append(min_amount)
    if max_amount is not None:
        sql += " AND amount <= %s"
        params.append(max_amount)

    sql += " ORDER BY expense_date DESC, id DESC"

    async with get_db_cursor() as cursor:
        await cursor.execute(sql, tuple(params))
        return await cursor.fetchall()


# ---------------------------------------------------------------------------
# Budget helpers (scoped by user_id)
# ---------------------------------------------------------------------------

async def fetch_budgets(user_id):
    """Return all budget limits for a specific user as {category: monthly_limit}."""
    logger.info(f"fetch_budgets called for user {user_id}")
    async with get_db_cursor() as cursor:
        await cursor.execute("SELECT category, monthly_limit FROM budgets WHERE user_id = %s", (user_id,))
        rows = await cursor.fetchall()
    return {row["category"]: row["monthly_limit"] for row in rows}


async def upsert_budget(user_id, category, monthly_limit):
    """Insert or update the budget limit for a category and user."""
    logger.info(f"upsert_budget called for user {user_id}: {category} → {monthly_limit}")
    async with get_db_cursor(commit=True) as cursor:
        await cursor.execute(
            """
            INSERT INTO budgets (user_id, category, monthly_limit)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE monthly_limit = %s
            """,
            (user_id, category, monthly_limit, monthly_limit),
        )


async def fetch_budget_vs_actual(user_id, year, month):
    """Return per-category spend vs budget for a given user, year, and month."""
    logger.info(f"fetch_budget_vs_actual called for user {user_id}: {year}-{month:02d}")
    async with get_db_cursor() as cursor:
        await cursor.execute(
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
        return await cursor.fetchall()