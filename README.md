# Expense Tracking System

A full-stack web application designed to track personal daily expenses, categorize spending, and visualize monthly financial data. This project uses **Streamlit** for the frontend user interface and **FastAPI** for the backend REST API, backed by a **MySQL** database.

## 🚀 Features

* **Add & Update Expenses:** Easy-to-use form to log daily expenses with categories (Rent, Food, Shopping, etc.) and notes.
* **Date-wise Filtering:** View expenses for specific dates.
* **Analytics Dashboard:** Visual insights into spending habits (Tabulated summaries and charts).
* **Robust Backend:** FastAPI server handling database operations efficiently.
* **Logging:** Comprehensive server-side logging for debugging and tracking errors.

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Python)
* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
* **Database:** MySQL
* **Language:** Python 3.10+

## 📂 Project Structure

```text
project-expense-tracking/
├── backend/
│   ├── db_helper.py         # Database connection and SQL queries
│   ├── logging_setup.py     # Configuration for system logs
│   ├── server.py            # Main FastAPI server entry point
│   └── server.log           # Runtime logs
├── frontend/
│   ├── add_update_ui.py     # UI component for adding/updating expenses
│   ├── analytics_ui.py      # UI component for charts and summary
│   └── app.py               # Main Streamlit application entry point
├── tests/                   # Unit tests
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
⚙️ Setup & Installation
1. Prerequisites
Python installed (version 3.10 or higher recommended).

MySQL Server installed and running.

2. Clone the Repository
Bash

git clone [https://github.com/your-username/project-expense-tracking.git](https://github.com/your-username/project-expense-tracking.git)
cd project-expense-tracking
3. Install Dependencies
Install the required Python libraries using pip:

Bash

pip install -r requirements.txt
4. Database Configuration
Open your MySQL client (Workbench or Command Line).

Create a new database named expenses_db (or whatever name you used in db_helper.py).

Create the expenses table:

SQL

CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    expense_date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    notes TEXT
);
Note: Ensure your database credentials (host, user, password) in backend/db_helper.py are correct.

🏃‍♂️ How to Run
You need to run the Backend and Frontend in two separate terminals.

Step 1: Start the Backend Server
Open a terminal at the project root and run:

Bash

cd backend
uvicorn server:app --reload
The server will start at http://localhost:8000

Step 2: Start the Frontend Application
Open a new terminal at the project root and run:

Bash

streamlit run frontend/app.py
The application will open in your browser at http://localhost:8501

🔌 API Endpoints
The backend exposes the following RESTful endpoints:

GET /expenses/{date} - Retrieve all expenses for a specific date.

POST /expenses/{date} - Add or update expenses for a specific date.

GET /analytics - Get summary data for a date range.

DELETE /expenses/{id} - Delete a specific expense record.

📝 Future Improvements
Add authentication (Login/Signup).

Export reports to CSV/PDF.

Monthly budget limit alerts.

🤝 Contributing
Contributions are welcome! Please fork the repository and create a pull request.

📄 License
This project is licensed under the MIT License.
