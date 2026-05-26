# 💸 Expense Tracking System

> A full-stack, cloud-native personal finance manager — track expenses, set budgets, and visualize your spending habits with beautiful analytics.

[![Frontend](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://expense-tracking-system-xapxb6qjyvhmdtagpejtii.streamlit.app/)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://huggingface.co/spaces/Shub-ways/expense-backend)
[![Database](https://img.shields.io/badge/Database-TiDB%20Serverless-CC0000?style=for-the-badge&logo=mysql&logoColor=white)]()
[![Auth](https://img.shields.io/badge/Auth-JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)]()

---

## 🌐 Live Demo

| Service  | URL |
|----------|-----|
| 🖥️ **Frontend** | [expense-tracking-system-xapxb6qjyvhmdtagpejtii.streamlit.app](https://expense-tracking-system-xapxb6qjyvhmdtagpejtii.streamlit.app/) |
| ⚙️ **Backend API** | [huggingface.co/spaces/Shub-ways/expense-backend](https://huggingface.co/spaces/Shub-ways/expense-backend) |

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Local Setup](#-local-setup)
- [Environment Variables](#-environment-variables)
- [API Design](#-api-design)
- [Key Architectural Decisions](#-key-architectural-decisions)
- [Project Structure](#-project-structure)

---

## 🧭 Overview

The **Expense Tracking System** is a production-grade, cloud-hosted personal finance application built with a fully decoupled frontend/backend architecture. Users can securely register, log and categorize their daily expenses, set per-category budgets, and explore rich visual analytics of their spending patterns — all from a clean, responsive web interface.

The application is designed for real-world use with attention to security (bcrypt + JWT), reliability (async DB connections with pool recycling), and scalability (stateless API design).

---

## ✨ Features

### 🔐 User Authentication
- Secure **registration and login** with JWT-based sessions.
- Passwords are **never stored in plain text** — bcrypt hashing is applied before persisting to the database.
- All protected API routes require a valid `Bearer` token in the `Authorization` header.

### 📊 Dashboard & Budget Alerts
- At-a-glance **budget vs. actual spending** comparison per category.
- Dynamic warning banners:
  - 🟡 **Near Budget** — triggered when spending approaches the set limit.
  - 🔴 **Budget Exceeded** — triggered when spending goes over the limit.

### 🧾 Expense Management
- Add, edit, and delete expenses with category tags.
- Calendar-based date selection for accurate temporal tracking.
- Instant UI updates after every operation.

### 📈 Analytics — By Category
- Interactive **donut charts** (Plotly) breaking down spending by category.
- Filter by any custom date range to zoom in on a period.

### 📅 Analytics — By Month
- **Bar charts** showing month-over-month spending trends.
- Quickly identify high-spend months and seasonal patterns.

### 🔍 Dynamic Search & Filters
- Powerful search tab supporting:
  - Keyword search
  - Category filter
  - Date range filter
  - Min / Max price range filter

### 🌍 User Preferences & Multi-Currency
- Users can switch their **display currency** dynamically: ₹ INR, $ USD, € EUR, £ GBP.
- Currency preference is persisted to the user's profile and reflected across the entire app instantly.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│              User's Browser                       │
└──────────────────────┬───────────────────────────┘
                       │  HTTPS
                       ▼
┌──────────────────────────────────────────────────┐
│         Streamlit Frontend                        │
│    (Streamlit Community Cloud)                    │
│                                                   │
│  • Renders UI & charts (Plotly)                   │
│  • Manages JWT token in session state             │
│  • Calls FastAPI via REST (requests library)      │
└──────────────────────┬───────────────────────────┘
                       │  REST API (JWT Bearer)
                       ▼
┌──────────────────────────────────────────────────┐
│         FastAPI Backend                           │
│    (Hugging Face Spaces — Docker/uvicorn)         │
│                                                   │
│  • Async route handlers                           │
│  • Pydantic validation on all inputs              │
│  • JWT issuance & verification (PyJWT)            │
│  • bcrypt password hashing                        │
│  • Alembic migrations run on boot                 │
└──────────────────────┬───────────────────────────┘
                       │  aiomysql (async)
                       ▼
┌──────────────────────────────────────────────────┐
│         TiDB Serverless                           │
│    (Cloud MySQL-compatible database)              │
│                                                   │
│  • Stores users, expenses, categories, budgets    │
│  • Schema managed via Alembic migrations          │
│  • Connection pool with aggressive pool_recycle   │
└──────────────────────────────────────────────────┘
```

The architecture is **fully decoupled**: the Streamlit frontend runs on Streamlit Community Cloud and knows nothing about the database — it only speaks to the FastAPI backend. The backend, deployed on Hugging Face Spaces, handles all business logic, authentication, and data persistence.

---

## 🛠️ Technology Stack

### Frontend
| Tool | Purpose |
|------|---------|
| **Streamlit** | UI framework |
| **Plotly** | Interactive charts (donut, bar) |
| **Pandas** | Data manipulation & aggregation |
| **Requests** | REST API communication with backend |

### Backend
| Tool | Purpose |
|------|---------|
| **FastAPI** (Python 3.10+) | Async REST API framework |
| **Uvicorn** | ASGI server (port 7860 on HF Spaces) |
| **PyJWT** | JWT token creation & verification |
| **bcrypt** | Secure password hashing |
| **Pydantic** | Request/response data validation |
| **Alembic** | Database schema migrations |
| **aiomysql** | Async MySQL database driver |

### Infrastructure
| Tool | Purpose |
|------|---------|
| **Streamlit Community Cloud** | Frontend hosting |
| **Hugging Face Spaces** | Backend hosting (Dockerfile) |
| **TiDB Serverless** | Cloud MySQL-compatible database |

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.10+
- A [TiDB Serverless](https://tidbcloud.com/) account (free tier works)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/expense-tracking-system.git
cd expense-tracking-system
```

### 2. Set Up the Environment

Create a `.env` file in the project root:

```env
# TiDB Database Credentials
DB_HOST=your-tidb-host.tidbcloud.com
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# JWT Secret Key (use a long, random string)
SECRET_KEY=your_super_secret_key_here
```

> ⚠️ **Never commit your `.env` file.** Ensure `.env` is listed in your `.gitignore`.

### 3. Install Dependencies

```bash
# Backend dependencies
pip install -r backend/requirements.txt

# Frontend dependencies
pip install -r frontend/requirements.txt
```

### 4. Run Database Migrations

```bash
alembic upgrade head
```

This will create all required tables in your TiDB database.

### 5. Start the Backend

```bash
uvicorn backend.server:app --reload --port 8000
```

The API will be live at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive Swagger UI.

### 6. Start the Frontend

In a new terminal:

```bash
streamlit run frontend/app.py
```

The app will open in your browser at `http://localhost:8501`.

> 💡 Make sure the `API_URL` variable in your frontend config/secrets points to `http://localhost:8000` during local development.

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DB_HOST` | ✅ | TiDB Serverless host address |
| `DB_USER` | ✅ | TiDB database username |
| `DB_PASSWORD` | ✅ | TiDB database password |
| `SECRET_KEY` | ✅ | Secret key for signing JWT tokens |
| `API_URL` | ✅ (Frontend) | Base URL of the FastAPI backend |

For **Hugging Face Spaces**, these are added as **Repository Secrets** in the Space settings. For **Streamlit Cloud**, they are added under **App Settings → Secrets**.

---

## 📡 API Design

The backend exposes a RESTful API. All protected routes require:

```
Authorization: Bearer <your_jwt_token>
```

### Key Endpoint Groups

| Group | Description |
|-------|-------------|
| `POST /auth/register` | Register a new user |
| `POST /auth/login` | Login and receive a JWT token |
| `GET/POST /expenses` | List or create expenses |
| `PUT/DELETE /expenses/{id}` | Update or delete an expense |
| `GET/POST /budgets` | Manage category budgets |
| `GET /analytics/category` | Spending breakdown by category |
| `GET /analytics/monthly` | Month-over-month spending trends |
| `GET /expenses/search` | Search/filter expenses |
| `PATCH /users/preferences` | Update user preferences (currency) |

> 📄 Full interactive docs available at `/docs` (Swagger UI) or `/redoc` when the backend is running.

---

## 🧠 Key Architectural Decisions

### Decoupled Frontend & Backend
The Streamlit frontend and FastAPI backend are deployed independently on separate cloud platforms. This separation allows each layer to be scaled, updated, and maintained independently without affecting the other.

### Stateless JWT Authentication
The API is entirely stateless. JWTs are issued on login and verified on each request — no server-side session storage. This means the backend can scale horizontally without any session affinity concerns.

### Async Throughout
FastAPI route handlers and database queries are fully `async/await`. Combined with `aiomysql`, this ensures the backend can handle high concurrency without blocking threads on I/O.

### Pydantic Validation
All incoming request bodies are validated against strict Pydantic models before touching the database. Malformed requests are rejected early with clear error messages — no raw, unvalidated data ever reaches the SQL layer.

### Alembic Auto-Migration on Boot
The Hugging Face Space Dockerfile is configured to run `alembic upgrade head` automatically on startup. This ensures the production database schema is always in sync with the codebase, with zero manual intervention needed after deployments.

### Connection Pool Recycling
TiDB Serverless aggressively closes idle connections. The backend uses an aggressive `pool_recycle` setting on the SQLAlchemy/aiomysql pool to prevent stale connections from causing silent 500 errors on low-traffic periods.

---

## 📁 Project Structure

```
expense-tracking-system/
│
├── backend/
│   ├── server.py          # FastAPI app entry point
│   ├── models.py          # SQLAlchemy ORM models
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── auth.py            # JWT & bcrypt utilities
│   ├── database.py        # Async DB connection & pool setup
│   └── routers/
│       ├── expenses.py
│       ├── budgets.py
│       ├── analytics.py
│       └── users.py
│
├── frontend/
│   └── app.py             # Streamlit app entry point
│
├── alembic/
│   ├── env.py
│   └── versions/          # Migration scripts
│
├── alembic.ini
├── Dockerfile             # For Hugging Face Spaces deployment
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

Built with ❤️ using **FastAPI** · **Streamlit** · **TiDB** · **Plotly**

</div>
