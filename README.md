<div align="center">

<br/>

**A full-stack, cloud-hosted personal finance manager — track expenses, set budgets, and explore beautiful analytics of your spending habits.**

<br/>

[![Frontend](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://expense-tracking-system-xapxb6qjyvhmdtagpejtii.streamlit.app/)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://huggingface.co/spaces/Shub-ways/expense-backend)
[![Database](https://img.shields.io/badge/Database-TiDB%20Serverless-CC0000?style=for-the-badge&logo=mysql&logoColor=white)](#)
[![Auth](https://img.shields.io/badge/Auth-JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](#)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](#)
[![Async](https://img.shields.io/badge/Async-aiomysql-00C7B7?style=flat-square)](#)
[![Pydantic](https://img.shields.io/badge/Validated-Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white)](#)
[![Alembic](https://img.shields.io/badge/Migrations-Alembic-6BA539?style=flat-square)](#)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](#)

<br/>

🌐 **[Live App →](https://expense-tracking-system-xapxb6qjyvhmdtagpejtii.streamlit.app/)**  &nbsp;&nbsp;|&nbsp;&nbsp;  ⚙️ **[Backend API →](https://huggingface.co/spaces/Shub-ways/expense-backend)**

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Local Setup](#-local-setup)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Key Design Decisions](#-key-design-decisions)
- [Project Structure](#-project-structure)

---

## 🧭 Overview

<img width="959" height="450" alt="Screenshot 2026-05-26 154826" src="https://github.com/user-attachments/assets/5cc68756-aa17-4d6e-ab6a-cc68826d3e68" />

<img width="959" height="450" alt="Screenshot 2026-05-26 154859" src="https://github.com/user-attachments/assets/5eec7fa9-560a-49ec-9a46-22419351cd95" />

<img width="959" height="449" alt="Screenshot 2026-05-26 154930" src="https://github.com/user-attachments/assets/88e5ee19-5717-4a8c-b2ac-1c3537ae8d03" />

<img width="959" height="449" alt="Screenshot 2026-05-26 154945" src="https://github.com/user-attachments/assets/4f9f662a-bdb3-4786-a39a-927373d84581" />


The **Expense Tracking System** is a production-grade, cloud-hosted personal finance application built with a fully decoupled frontend/backend architecture.

Users can securely register, log and categorize daily expenses, set per-category budgets, and explore rich visual analytics — all from a clean, responsive web interface.

> Designed with attention to **security** (bcrypt + JWT), **reliability** (async DB with pool recycling), and **scalability** (stateless API design).

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔐 User Authentication
Secure register & login with JWT-based sessions. Passwords are **never stored in plain text** — bcrypt hashing is applied before persisting to the database.

</td>
<td width="50%">

### 📊 Dashboard & Budget Alerts
Real-time budget vs. actual spending comparison. Dynamic banners for:
- 🟡 **Near Budget** — approaching limit
- 🔴 **Budget Exceeded** — over the limit

</td>
</tr>
<tr>
<td width="50%">

### 🧾 Expense Management
Add, edit, and delete expenses with category tags and calendar-based date selection. Instant UI updates after every operation.

</td>
<td width="50%">

### 📈 Analytics by Category
Interactive **donut charts** (Plotly) breaking down spending by category for any custom date range.

</td>
</tr>
<tr>
<td width="50%">

### 📅 Analytics by Month
**Bar charts** showing month-over-month spending trends — identify high-spend months at a glance.

</td>
<td width="50%">

### 🔍 Dynamic Search & Filters
Query expenses by **keyword**, **category**, **date range**, and **min/max price** from a single powerful tab.

</td>
</tr>
<tr>
<td colspan="2">

### 🌍 Multi-Currency Support
Switch display currency dynamically — **₹ INR · $ USD · € EUR · £ GBP** — persisted to user profile and reflected app-wide instantly.

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  User's Browser                     │
└──────────────────────┬──────────────────────────────┘
                       │  HTTPS
                       ▼
┌─────────────────────────────────────────────────────┐
│           🖥️  Streamlit Frontend                    │
│         (Streamlit Community Cloud)                 │
│                                                     │
│  • Renders UI & Plotly charts                       │
│  • Manages JWT token in session state               │
│  • Communicates via REST (requests library)         │
└──────────────────────┬──────────────────────────────┘
                       │  REST API + JWT Bearer Token
                       ▼
┌─────────────────────────────────────────────────────┐
│           ⚙️  FastAPI Backend                      │
│         (Hugging Face Spaces — Docker)              │
│                                                     │
│  • Async route handlers (uvicorn)                   │
│  • Pydantic validation on all inputs                │
│  • JWT issuance & verification (PyJWT)              │
│  • bcrypt password hashing                          │
│  • Alembic migrations run automatically on boot     │
└──────────────────────┬──────────────────────────────┘
                       │  aiomysql (async)
                       ▼
┌─────────────────────────────────────────────────────┐
│           🗄️  TiDB Serverless                       │
│         (Cloud MySQL-compatible)                    │
│                                                     │
│  • Stores users, expenses, categories, budgets      │
│  • Schema managed via Alembic migrations            │
│  • pool_recycle to prevent idle connection drops    │
└─────────────────────────────────────────────────────┘
```

> The architecture is **fully decoupled** — Streamlit runs on Streamlit Community Cloud and only speaks REST to the FastAPI backend. The backend handles all business logic, auth, and data persistence.

---

## 🛠️ Tech Stack

### Frontend
| Tool | Purpose |
|------|---------|
| ![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) | UI framework & deployment |
| ![Plotly](https://img.shields.io/badge/-Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white) | Interactive donut & bar charts |
| ![Pandas](https://img.shields.io/badge/-Pandas-150458?style=flat-square&logo=pandas&logoColor=white) | Data manipulation & aggregation |
| ![Requests](https://img.shields.io/badge/-Requests-2CA5E0?style=flat-square) | REST API communication |

### Backend
| Tool | Purpose |
|------|---------|
| ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) | Async REST API framework |
| ![Uvicorn](https://img.shields.io/badge/-Uvicorn-4051B5?style=flat-square) | ASGI server on port 7860 |
| ![PyJWT](https://img.shields.io/badge/-PyJWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white) | JWT token issuance & verification |
| ![bcrypt](https://img.shields.io/badge/-bcrypt-E91E63?style=flat-square) | Secure password hashing |
| ![Pydantic](https://img.shields.io/badge/-Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white) | Request/response validation |
| ![Alembic](https://img.shields.io/badge/-Alembic-6BA539?style=flat-square) | Database schema migrations |
| ![aiomysql](https://img.shields.io/badge/-aiomysql-00758F?style=flat-square&logo=mysql&logoColor=white) | Async MySQL driver |

### Infrastructure
| Tool | Purpose |
|------|---------|
| ![Streamlit Cloud](https://img.shields.io/badge/-Streamlit_Cloud-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) | Frontend hosting |
| ![Hugging Face](https://img.shields.io/badge/-Hugging_Face_Spaces-FFD21E?style=flat-square&logo=huggingface&logoColor=black) | Backend hosting (Dockerfile) |
| ![TiDB](https://img.shields.io/badge/-TiDB_Serverless-CC0000?style=flat-square&logo=mysql&logoColor=white) | Cloud MySQL-compatible database |

---

## ⚙️ Local Setup

### Prerequisites
- Python `3.10+`
- A [TiDB Serverless](https://tidbcloud.com/) account *(free tier works)*
- Git

### Step 1 — Clone

```bash
git clone https://github.com/your-username/expense-tracking-system.git
cd expense-tracking-system
```

### Step 2 — Create `.env`

```env
# TiDB Database Credentials
DB_HOST=your-tidb-host.tidbcloud.com
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# JWT Secret Key (use a long, random string)
SECRET_KEY=your_super_secret_key_here
```

> ⚠️ Never commit your `.env` — ensure it's in `.gitignore`.

### Step 3 — Install Dependencies

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### Step 4 — Run Migrations

```bash
alembic upgrade head
```

### Step 5 — Start the Backend

```bash
uvicorn backend.server:app --reload --port 8000
# Interactive API docs → http://localhost:8000/docs
```

### Step 6 — Start the Frontend

```bash
streamlit run frontend/app.py
# Opens at → http://localhost:8501
```

> 💡 Set `API_URL=http://localhost:8000` in your frontend secrets/config for local dev.

---

## 🔑 Environment Variables

| Variable | Required | Where | Description |
|----------|----------|-------|-------------|
| `DB_HOST` | ✅ | Backend | TiDB Serverless host address |
| `DB_USER` | ✅ | Backend | TiDB database username |
| `DB_PASSWORD` | ✅ | Backend | TiDB database password |
| `SECRET_KEY` | ✅ | Backend | Secret for signing JWT tokens |
| `API_URL` | ✅ | Frontend | Base URL of the FastAPI backend |

> For **Hugging Face Spaces** → add as Repository Secrets in Space settings.
> For **Streamlit Cloud** → add under App Settings → Secrets.

---

## 📡 API Reference

All protected routes require:
```
Authorization: Bearer <your_jwt_token>
```

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | ❌ | Register a new user |
| `POST` | `/auth/login` | ❌ | Login & receive JWT token |
| `GET` | `/expenses` | ✅ | List all expenses |
| `POST` | `/expenses` | ✅ | Create a new expense |
| `PUT` | `/expenses/{id}` | ✅ | Update an expense |
| `DELETE` | `/expenses/{id}` | ✅ | Delete an expense |
| `GET` | `/budgets` | ✅ | Get category budgets |
| `POST` | `/budgets` | ✅ | Set a category budget |
| `GET` | `/analytics/category` | ✅ | Spending by category |
| `GET` | `/analytics/monthly` | ✅ | Month-over-month trends |
| `GET` | `/expenses/search` | ✅ | Search & filter expenses |
| `PATCH` | `/users/preferences` | ✅ | Update display currency |

> 📄 Full interactive docs at `/docs` (Swagger UI) when the backend is running.

---

## 🧠 Key Design Decisions

<details>
<summary><b>🔀 Decoupled Frontend & Backend</b></summary>
<br>
Streamlit and FastAPI are deployed independently on separate platforms. Each layer can be scaled, updated, and maintained without affecting the other — true separation of concerns.
</details>

<details>
<summary><b>🔐 Stateless JWT Authentication</b></summary>
<br>
The API is entirely stateless. JWTs are issued on login and verified per request — no server-side session storage. This means the backend can scale horizontally with zero session affinity concerns.
</details>

<details>
<summary><b>⚡ Fully Async I/O</b></summary>
<br>
FastAPI route handlers and DB queries are fully <code>async/await</code>. Combined with <code>aiomysql</code>, the backend handles high concurrency without blocking threads on I/O-bound operations.
</details>

<details>
<summary><b>✅ Pydantic Validation Layer</b></summary>
<br>
All incoming request bodies are validated against strict Pydantic models before reaching the database. Malformed requests are rejected early with clear error messages — no raw unvalidated data ever hits SQL.
</details>

<details>
<summary><b>🔄 Alembic Auto-Migration on Boot</b></summary>
<br>
The Hugging Face Spaces Dockerfile runs <code>alembic upgrade head</code> automatically on startup. The production DB schema is always in sync with the codebase — zero manual intervention needed after deploys.
</details>

<details>
<summary><b>🔁 Aggressive Connection Pool Recycling</b></summary>
<br>
TiDB Serverless aggressively closes idle connections. An aggressive <code>pool_recycle</code> setting on the connection pool prevents stale connections from causing silent 500 errors during low-traffic periods.
</details>

---

## 📁 Project Structure

```
expense-tracking-system/
│
├── backend/
│   ├── server.py           # FastAPI app entry point
│   ├── models.py           # SQLAlchemy ORM models
│   ├── schemas.py          # Pydantic request/response schemas
│   ├── auth.py             # JWT & bcrypt utilities
│   ├── database.py         # Async DB connection & pool setup
│   └── routers/
│       ├── expenses.py
│       ├── budgets.py
│       ├── analytics.py
│       └── users.py
│
├── frontend/
│   └── app.py              # Streamlit app entry point
│
├── alembic/
│   ├── env.py
│   └── versions/           # Migration scripts
│
├── alembic.ini
├── Dockerfile              # For Hugging Face Spaces deployment
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch → `git checkout -b feature/your-feature`
3. Commit your changes → `git commit -m 'Add some feature'`
4. Push to the branch → `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ using FastAPI · Streamlit · TiDB · Plotly**

<br/>

[![Frontend](https://img.shields.io/badge/🚀_Live_App-Click_Here-00D4A0?style=for-the-badge)](https://expense-tracking-system-xapxb6qjyvhmdtagpejtii.streamlit.app/)

</div>
