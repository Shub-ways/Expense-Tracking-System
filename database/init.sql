-- ============================================================
-- Expense Tracking System — Database Initialization Script
-- Run automatically when the MySQL container starts for the
-- first time via docker-compose.
-- ============================================================

CREATE DATABASE IF NOT EXISTS expense_manager;
USE expense_manager;

-- ─── Expenses Table ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS expenses (
    id           INT            AUTO_INCREMENT PRIMARY KEY,
    expense_date DATE           NOT NULL,
    amount       DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    category     VARCHAR(50)    NOT NULL,
    notes        TEXT,
    created_at   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_expense_date (expense_date),
    INDEX idx_category    (category)
);

-- ─── Budgets Table ─────────────────────────────────────────
-- Stores monthly spending limits per category.
-- UNIQUE constraint on category so we can use ON DUPLICATE KEY UPDATE.
CREATE TABLE IF NOT EXISTS budgets (
    id            INT            AUTO_INCREMENT PRIMARY KEY,
    category      VARCHAR(50)    NOT NULL UNIQUE,
    monthly_limit DECIMAL(10, 2) NOT NULL CHECK (monthly_limit > 0),
    updated_at    TIMESTAMP      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ─── Seed Data (optional — remove in production) ──────────
INSERT IGNORE INTO expenses (expense_date, amount, category, notes) VALUES
    ('2024-08-01', 500.00, 'Food',          'Weekly groceries'),
    ('2024-08-01', 200.00, 'Entertainment', 'Netflix + Prime'),
    ('2024-08-05', 150.00, 'Food',          'Restaurant dinner'),
    ('2024-08-10', 9000.00,'Rent',          'Monthly rent'),
    ('2024-08-15', 10.00,  'Shopping',      'Bought potatoes'),
    ('2024-09-01', 600.00, 'Food',          'Groceries'),
    ('2024-09-10', 9000.00,'Rent',          'Monthly rent');

INSERT IGNORE INTO budgets (category, monthly_limit) VALUES
    ('Food',          3000.00),
    ('Rent',          10000.00),
    ('Shopping',      2000.00),
    ('Entertainment', 1000.00),
    ('Other',         500.00);
