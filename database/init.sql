-- ============================================================
-- Expense Tracking System — Database Initialization Script
-- Run automatically when the MySQL container starts for the
-- first time via docker-compose.
-- ============================================================

CREATE DATABASE IF NOT EXISTS expense_manager;
USE expense_manager;

-- ─── Users Table ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INT            AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)    UNIQUE NOT NULL,
    password_hash VARCHAR(255)   NOT NULL,
    created_at    TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

-- ─── Expenses Table ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS expenses (
    id           INT            AUTO_INCREMENT PRIMARY KEY,
    user_id      INT            NOT NULL,
    expense_date DATE           NOT NULL,
    amount       DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    category     VARCHAR(50)    NOT NULL,
    notes        TEXT,
    created_at   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_expense_date (user_id, expense_date),
    INDEX idx_user_category    (user_id, category),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── Budgets Table ─────────────────────────────────────────
-- Stores monthly spending limits per category per user.
CREATE TABLE IF NOT EXISTS budgets (
    id            INT            AUTO_INCREMENT PRIMARY KEY,
    user_id       INT            NOT NULL,
    category      VARCHAR(50)    NOT NULL,
    monthly_limit DECIMAL(10, 2) NOT NULL CHECK (monthly_limit > 0),
    updated_at    TIMESTAMP      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY idx_user_category (user_id, category),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── Seed Data ─────────────────────────────────────────────
-- Insert default user (username: demo, password: demo123)
INSERT IGNORE INTO users (id, username, password_hash) VALUES
    (1, 'demo', '$2b$12$.5fsYsD5E659JmYOItlfQ.5oNZeOLgqxcM8sgxnkWGQpCnd12eqKS');

-- Seed data for demo user
INSERT IGNORE INTO expenses (user_id, expense_date, amount, category, notes) VALUES
    (1, '2024-08-01', 500.00, 'Food',          'Weekly groceries'),
    (1, '2024-08-01', 200.00, 'Entertainment', 'Netflix + Prime'),
    (1, '2024-08-05', 150.00, 'Food',          'Restaurant dinner'),
    (1, '2024-08-10', 9000.00,'Rent',          'Monthly rent'),
    (1, '2024-08-15', 10.00,  'Shopping',      'Bought potatoes'),
    (1, '2024-09-01', 600.00, 'Food',          'Groceries'),
    (1, '2024-09-10', 9000.00,'Rent',          'Monthly rent');

INSERT IGNORE INTO budgets (user_id, category, monthly_limit) VALUES
    (1, 'Food',          3000.00),
    (1, 'Rent',          10000.00),
    (1, 'Shopping',      2000.00),
    (1, 'Entertainment', 1000.00),
    (1, 'Other',         500.00);
