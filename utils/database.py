import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = "data/finance_assistant.db"

def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            month TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Budget table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            month TEXT NOT NULL,
            UNIQUE(user_id, category, month),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)

# User functions
def add_user(username, hashed_password):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# Expense functions
def add_expense(user_id, date, description, amount, category):
    conn = get_connection()
    cursor = conn.cursor()
    month = pd.to_datetime(date).strftime("%Y-%m")
    cursor.execute('''
        INSERT INTO expenses (user_id, date, description, amount, category, month)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, str(date), description, amount, category, month))
    conn.commit()
    conn.close()

def get_expenses(user_id):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM expenses WHERE user_id = ?", conn, params=(user_id,))
    conn.close()
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df

def delete_expense(expense_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

def update_expenses_from_df(user_id, df):
    conn = get_connection()
    cursor = conn.cursor()
    # For simplicity, we'll clear and re-insert for the dynamic data editor
    # In a more production-ready app, we'd use UPSERT or matched IDs
    cursor.execute("DELETE FROM expenses WHERE user_id = ?", (user_id,))
    for _, row in df.iterrows():
        month = pd.to_datetime(row['date']).strftime("%Y-%m")
        cursor.execute('''
            INSERT INTO expenses (user_id, date, description, amount, category, month)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, str(row['date']), row['description'], row['amount'], row['category'], month))
    conn.commit()
    conn.close()

# Budget functions
def set_budget(user_id, category, amount, month):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO budgets (user_id, category, amount, month)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, category, month) DO UPDATE SET amount=excluded.amount
    ''', (user_id, category, amount, month))
    conn.commit()
    conn.close()

def get_budgets(user_id, month):
    conn = get_connection()
    df = pd.read_sql_query("SELECT category, amount FROM budgets WHERE user_id = ? AND month = ?", 
                          conn, params=(user_id, month))
    conn.close()
    return df
