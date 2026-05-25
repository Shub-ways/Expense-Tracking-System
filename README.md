---
title: Expense Backend
emoji: 💰
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---
<div align="center">

<pre>
███████╗██╗  ██╗██████╗ ███████╗███╗   ██╗███████╗███████╗
██╔════╝╚██╗██╔╝██╔══██╗██╔════╝████╗  ██║██╔════╝██╔════╝
█████╗   ╚███╔╝ ██████╔╝█████╗  ██╔██╗ ██║███████╗█████╗  
██╔══╝   ██╔██╗ ██╔═══╝ ██╔══╝  ██║╚██╗██║╚════██║██╔══╝  
███████╗██╔╝ ██╗██║     ███████╗██║ ╚████║███████║███████╗
╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝
████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗  
╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗ 
   ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝ 
   ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗ 
   ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║ 
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ 
</pre>

### `Full-Stack Personal Finance Management System`

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](./LICENSE)

<br/>

> *Know where every rupee goes.*  
> Log expenses · Visualize spending · Stay in control — all from your browser.

<br/>

---

</div>

<br/>

## 💡 What is Expense Tracker?

A **full-stack web application** built to take the friction out of personal finance tracking. Log your daily expenses by category, filter by date, and get visual insights into your spending habits — all powered by a clean **FastAPI** backend, a **Streamlit** frontend, and a reliable **MySQL** database.

No spreadsheets. No guesswork. Just clarity.

<br/>

## 🚀 Features

<table>
<tr>
<td width="50%">

### 💸 Add & Update Expenses
An easy-to-use form to log daily expenses with categories — Rent, Food, Shopping, Transport, and more — plus custom notes for context.

</td>
<td width="50%">

### 📅 Date-wise Filtering
Retrieve and review expenses for any specific date. Drill down into exactly what you spent and when.

</td>
</tr>
<tr>
<td width="50%">

### 📊 Analytics Dashboard
Visual spending insights with tabulated summaries and charts. Understand patterns, identify overspending, and take action.

</td>
<td width="50%">

### ⚡ Robust FastAPI Backend
A high-performance REST API server that handles all database operations with speed, validation, and clean error responses.

</td>
</tr>
<tr>
<td width="50%">

### 🪵 Server-Side Logging
Comprehensive logging for every operation — errors, requests, and database events — making debugging effortless.

</td>
<td width="50%">

### 🧪 Test Coverage
A dedicated `tests/` module to validate core backend logic and keep the system reliable as it grows.

</td>
</tr>
</table>

<br/>

## 🛠️ Tech Stack

```
┌──────────────────────────────────────────────────────────────────┐
│                    EXPENSE TRACKER STACK                         │
├───────────────────────┬──────────────────────────────────────────┤
│  Frontend / UI        │  Streamlit (Python)                      │
├───────────────────────┼──────────────────────────────────────────┤
│  Backend / API        │  FastAPI + Uvicorn                       │
├───────────────────────┼──────────────────────────────────────────┤
│  Database             │  MySQL                                   │
├───────────────────────┼──────────────────────────────────────────┤
│  Language             │  Python 3.10+                            │
├───────────────────────┼──────────────────────────────────────────┤
│  Logging              │  Python logging module                   │
├───────────────────────┼──────────────────────────────────────────┤
│  Testing              │  pytest (tests/ module)                  │
└───────────────────────┴──────────────────────────────────────────┘
```

<br/>

## 📂 Project Structure

```
Expense-Tracking-System/
│
├── backend/
│   ├── server.py            # 🚀 FastAPI server entry point
│   ├── db_helper.py         # 🗄️  Database connection & SQL queries
│   ├── logging_setup.py     # 🪵  Logging configuration
│   └── server.log           # 📋  Runtime logs (auto-generated)
│
├── frontend/
│   ├── app.py               # 🖥️  Main Streamlit application
│   ├── add_update_ui.py     # ➕  Add/update expense UI component
│   └── analytics_ui.py      # 📊  Charts & summary UI component
│
├── tests/                   # 🧪 Unit tests
│
├── requirements.txt         # 📦 Python dependencies
├── .gitignore
└── README.md
```

<br/>

## ⚙️ Setup & Installation

### Prerequisites

- **Python 3.10+** installed
- **MySQL Server** installed and running locally

### 1. Clone the Repository

```bash
git clone https://github.com/Shub-ways/Expense-Tracking-System.git
cd Expense-Tracking-System
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Database

Open your MySQL client (Workbench or CLI) and run:

```sql
CREATE DATABASE expenses_db;

USE expenses_db;

CREATE TABLE expenses (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    expense_date  DATE           NOT NULL,
    amount        DECIMAL(10, 2) NOT NULL,
    category      VARCHAR(50)    NOT NULL,
    notes         TEXT
);
```

> ⚠️ Then update your credentials (host, user, password) inside `backend/db_helper.py`.

<br/>

## 🏃 How to Run

This app requires **two terminals** running simultaneously.

**Terminal 1 — Start the Backend**

```bash
cd backend
uvicorn server:app --reload
```

> Backend live at → `http://localhost:8000`

**Terminal 2 — Start the Frontend**

```bash
streamlit run frontend/app.py
```

> App opens in browser at → `http://localhost:8501`

<br/>

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Log in and get access token |
| `GET` | `/expenses/{date}` | Fetch all expenses for a specific date (Auth) |
| `POST` | `/expenses/{date}` | Add or update expenses for a date (Auth) |
| `POST` | `/analytics/` | Get spending summary for a date range (Auth) |
| `POST` | `/analytics/month` | Get month-by-month spend breakdown (Auth) |
| `GET` | `/budgets/` | Fetch monthly category budgets (Auth) |
| `POST` | `/budgets/` | Set budget limit for category (Auth) |
| `GET` | `/budgets/vs-actual` | Compare spend vs budget for a month (Auth) |

> 📖 Interactive API docs auto-generated at `http://localhost:8000/docs` (Swagger UI)

<br/>

## 🌐 Cloud Deployment Setup

You can deploy the complete stack using **Render Blueprints**. 

### 1. Set Up Database
Since Render's free tier does not host MySQL databases, create a free MySQL instance on a provider like:
- [Aiven](https://aiven.io/mysql)
- [Railway](https://railway.com)
- [Clever Cloud](https://www.clever-cloud.com)

Obtain the connection credentials (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`).

### 2. Deploy to Render
1. Click **New > Blueprint** in your Render Dashboard.
2. Link your repository.
3. Render will prompt you for the database connection variables (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`). Fill these in.
4. Render will automatically launch the backend and frontend services, run Alembic migrations, and wire them up using environment variables.

<br/>

## 🗺️ Roadmap

- [x] User authentication (Login / Signup)
- [x] Export reports to CSV
- [x] Monthly budget limits and alerts
- [x] Database migrations (Alembic)
- [ ] Recurring expense support
- [ ] Mobile-responsive UI

<br/>

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the project
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add some AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

<br/>

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](./LICENSE) for more information.

<br/>

## 👨‍💻 Author

<div align="center">

**Shubham Kumar**

[![GitHub](https://img.shields.io/badge/GitHub-Shub--ways-181717?style=for-the-badge&logo=github)](https://github.com/Shub-ways)

*Built with ❤️ for smarter personal finance*

---

⭐ **Found it useful? Drop a star!** ⭐

</div>
