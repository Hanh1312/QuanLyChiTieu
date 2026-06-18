import sqlite3
from datetime import date
import os

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
        PersonName TEXT,
        Amount REAL,
        DueDate TEXT,
        Status TEXT DEFAULT 'Uncollected',
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