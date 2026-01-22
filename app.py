import uuid
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Personal Finance Assistant", layout="wide")

 
# FILE STORAGE SETUP

DATA_DIR = "data/users"
os.makedirs(DATA_DIR, exist_ok=True)

def get_user_file(user_id):
    return f"{DATA_DIR}/{user_id}.csv"

def load_user_data(user_id):
    file_path = get_user_file(user_id)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame(
            columns=["date", "description", "amount", "category", "month"]
        )

    df["date"] = pd.to_datetime(df.get("date"), errors="coerce")
    df["amount"] = pd.to_numeric(df.get("amount"), errors="coerce").fillna(0)
    df["category"] = df.get("category", "Other").fillna("Other")
    df["month"] = df["date"].dt.strftime("%Y-%m")

    return df

def save_user_data(user_id, df):
    df.to_csv(get_user_file(user_id), index=False)


# USER SESSION

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if "expenses" not in st.session_state:
    st.session_state.expenses = load_user_data(st.session_state.user_id)

expenses = st.session_state.expenses


# SIDEBAR FILTERS

st.sidebar.header("📊 Filters")

months = ["All"] + sorted(expenses["month"].dropna().unique().tolist())
selected_month = st.sidebar.selectbox("Select Month", months)

categories = ["All"] + sorted(expenses["category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", categories)


# APPLY FILTERS

df = expenses.copy()

if selected_month != "All":
    df = df[df["month"] == selected_month]

if selected_category != "All":
    df = df[df["category"] == selected_category]


# DASHBOARD KPIs

st.title("💰 Personal Finance Assistant")

col1, col2, col3 = st.columns(3)
col1.metric("Total Spent", f"₹{df['amount'].sum():.2f}" if not df.empty else "₹0.00")
col2.metric("Transactions", len(df))
col3.metric(
    "Average Expense",
    f"₹{df['amount'].mean():.2f}" if not df.empty else "₹0.00"
)


# CATEGORY BAR CHART

st.subheader("📊 Spending by Category")

if not df.empty and df["amount"].sum() > 0:
    cat_data = df.groupby("category")["amount"].sum()

    if not cat_data.empty:
        fig, ax = plt.subplots()
        ax.bar(cat_data.index, cat_data.values)
        ax.set_xlabel("Category")
        ax.set_ylabel("Amount")
        st.pyplot(fig)
else:
    st.info("No category data available.")


# MONTHLY TREND (SAFE PLOT)

st.subheader("📈 Monthly Spending Trend")

monthly_summary = (
    expenses.groupby("month")["amount"]
    .sum()
    .reset_index()
)

if not monthly_summary.empty and monthly_summary["amount"].sum() > 0:
    fig2, ax2 = plt.subplots()
    ax2.plot(
        monthly_summary["month"],
        monthly_summary["amount"],
        marker="o"
    )
    ax2.set_xlabel("Month")
    ax2.set_ylabel("Total Spending")
    st.pyplot(fig2)
else:
    st.info("No monthly data available yet.")


# ADD NEW EXPENSE

st.subheader("➕ Add New Expense")

with st.form("expense_form"):
    date = st.date_input("Date", value=datetime.today())
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=1.0)
    category = st.selectbox(
        "Category",
        categories[1:] if len(categories) > 1 else ["Other"]
    )

    submit = st.form_submit_button("Add Expense")

    if submit:
        new_row = {
            "date": pd.to_datetime(date),
            "description": description,
            "amount": float(amount),
            "category": category,
            "month": pd.to_datetime(date).strftime("%Y-%m")
        }

        expenses = pd.concat(
            [expenses, pd.DataFrame([new_row])],
            ignore_index=True
        )

        st.session_state.expenses = expenses
        save_user_data(st.session_state.user_id, expenses)

        st.success("Expense added successfully!")
        st.rerun()


# EDIT / DELETE EXPENSES

st.subheader("📝 Edit / Delete Expenses")
st.info("✏ Edit or 🗑 delete rows (saved automatically).")

edited_df = st.data_editor(
    expenses,
    num_rows="dynamic",
    width="stretch",
    key="expense_editor"
)

if not edited_df.equals(expenses):
    edited_df["date"] = pd.to_datetime(edited_df["date"], errors="coerce")
    edited_df["amount"] = pd.to_numeric(
        edited_df["amount"], errors="coerce"
    ).fillna(0)
    edited_df["month"] = edited_df["date"].dt.strftime("%Y-%m")

    st.session_state.expenses = edited_df
    save_user_data(st.session_state.user_id, edited_df)

    st.success("Changes saved!")
    st.rerun()


# RESET USER DATA

if st.sidebar.button("🔄 Reset My Data"):
    empty_df = pd.DataFrame(
        columns=["date", "description", "amount", "category", "month"]
    )
    st.session_state.expenses = empty_df
    save_user_data(st.session_state.user_id, empty_df)
    st.rerun()
