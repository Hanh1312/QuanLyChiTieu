import pyodbc
SERVER = r'Manh'
DATABASE = 'QuanLyChiTieu'

def get_connection():

    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes;"
    )
# ==========================
# LOGIN
# ==========================

def check_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Users
        WHERE Username = ?
        AND PasswordHash = ?
    """, (username, password))

    user = cursor.fetchone()

    conn.close()

    return user

# ==========================
# DASHBOARD
# ==========================

def get_total_income():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ISNULL(SUM(Amount),0)
        FROM Transactions
        WHERE Type='Income'
    """)

    value = cursor.fetchone()[0]

    conn.close()

    return float(value)

def get_total_expense():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ISNULL(SUM(Amount),0)
        FROM Transactions
        WHERE Type='Expense'
    """)

    value = cursor.fetchone()[0]

    conn.close()

    return float(value)

def get_total_debt_pay():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ISNULL(SUM(Amount),0)
        FROM DebtPay
        WHERE Status='Unpaid'
    """)

    value = cursor.fetchone()[0]

    conn.close()

    return float(value)

def get_total_debt_receive():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ISNULL(SUM(Amount),0)
        FROM DebtReceive
        WHERE Status='Uncollected'
    """)

    value = cursor.fetchone()[0]

    conn.close()

    return float(value)

from datetime import date

def get_due_debts():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM DebtPay
        WHERE Status='Unpaid'
    """)

    debts = cursor.fetchall()

    conn.close()

    warning_list = []

    today = date.today()

    for debt in debts:

        days_left = (
            debt.DueDate - today
        ).days

        if days_left <= 3:

            warning_list.append(
                (
                    debt.PersonName,
                    debt.Amount,
                    days_left
                )
            )

    return warning_list