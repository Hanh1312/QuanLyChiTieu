import sqlite3
from datetime import date
import os
DATABASE = "expense.db"

source = os.path.join(
    os.getcwd(),
    "expense.db"
)


def get_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn
def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users
    (
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT UNIQUE,
        PasswordHash TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Transactions
    (
        TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER,
        TransactionDate TEXT,
        Type TEXT,
        Category TEXT,
        Amount REAL,
        Note TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DebtPay
    (
        DebtID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER,
        PersonName TEXT,
        Amount REAL,
        DueDate TEXT,
        Status TEXT DEFAULT 'Unpaid',
        Note TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DebtReceive
    (
        DebtID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER,
        PersonName TEXT,
        Amount REAL,
        DueDate TEXT,
        Status TEXT DEFAULT 'Uncollected',
        Note TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Savings
    (
        SavingID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER,
        SavingDate TEXT,
        Type TEXT DEFAULT 'Deposit',
        Amount REAL,
        Note TEXT
    )
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO Users
    (
        UserID,
        Username,
        PasswordHash
    )
    VALUES
    (
        1,
        'admin',
        'admin123'
    )
    """)

    conn.commit()
    conn.close()


create_tables()
# =====================================
# LOGIN
# =====================================

def check_login(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM Users
        WHERE Username=?
        AND PasswordHash=?
        """,
        (username, password)
    )

    user = cursor.fetchone()

    conn.close()

    return user


# =====================================
# DASHBOARD
# =====================================

def get_total_income(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COALESCE(SUM(Amount),0)
    FROM Transactions
    WHERE Type='Income'
    AND UserID=?
    """,(user_id,))

    result = cursor.fetchone()[0]

    conn.close()

    return result


def get_total_expense(user_id):

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
    SELECT COALESCE(SUM(Amount),0)
    FROM Transactions
    WHERE Type='Expense'
    AND UserID=?
    """,(user_id,))

    result = cursor.fetchone()[0]

    conn.close()

    return result


def get_total_debt_pay(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COALESCE(SUM(Amount),0)
    FROM DebtPay
    WHERE Status='Unpaid'
    AND UserID=?
    """,(user_id,))

    result = cursor.fetchone()[0]

    conn.close()

    return result


def get_total_debt_receive(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(Amount),0)
        FROM DebtReceive
        WHERE Status='Uncollected'
        AND UserID=?
        """,(user_id,))

    result = cursor.fetchone()[0]

    conn.close()

    return result


# =====================================
# DUE DEBT WARNING
# =====================================
def get_due_debts(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM DebtPay
        WHERE Status='Unpaid'
        AND UserID=?
    """,(user_id,))

    debts = cursor.fetchall()

    conn.close()

    warning_list = []

    today = date.today()

    for debt in debts:

        try:

            due_date = date.fromisoformat(
                debt["DueDate"]
            )

            days_left = (
                due_date - today
            ).days

            if days_left <= 3:

                warning_list.append(
                    (
                        debt["PersonName"],
                        debt["Amount"],
                        days_left
                    )
                )

        except:
            pass

    return warning_list

def get_total_saving(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT Type, Amount      
    FROM Savings
    WHERE UserID=?
    """,(user_id,))

    rows = cursor.fetchall()

    conn.close()

    total = 0

    for row in rows:

        if row["Type"] == "Deposit":
            total += row["Amount"]
        else:
            total -= row["Amount"]

    return total
