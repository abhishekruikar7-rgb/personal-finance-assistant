import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Personal Finance Assistant", layout="wide")

# =========================
# LOAD DATA SAFELY
# =========================
if "expenses" not in st.session_state:
    df = pd.read_csv("data/expenses.csv")

    # Ensure date column
    df["date"] = pd.to_datetime(df["date"])

    # Ensure month column (fixes KeyError)
    if "month" not in df.columns:
        df["month"] = df["date"].dt.strftime("%Y-%m")

    st.session_state.expenses = df

# ===== FIX MIXED DATA TYPES (IMPORTANT) =====
st.session_state.expenses["date"] = pd.to_datetime(
    st.session_state.expenses["date"], errors="coerce"
)

st.session_state.expenses["month"] = (
    st.session_state.expenses["date"].dt.strftime("%Y-%m")
)

st.session_state.expenses["category"] = (
    st.session_state.expenses["category"]
    .astype(str)
    .replace("nan", "Other")
    .replace("", "Other")
)



# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("📊 Filters")

# Clean month column before using it
st.session_state.expenses["month"] = (
    st.session_state.expenses["month"]
    .astype(str)
    .replace("nan", "")
)

months = ["All"] + sorted(
    [m for m in st.session_state.expenses["month"].unique().tolist() if m != ""]
)

selected_month = st.sidebar.selectbox("Select Month", months)

categories = ["All"] + sorted(
    st.session_state.expenses["category"].dropna().unique().tolist()
)

selected_category = st.sidebar.selectbox("Select Category", categories)


# =========================
# APPLY FILTERS
# =========================
df = st.session_state.expenses.copy()

if selected_month != "All":
    df = df[df["month"] == selected_month]

if selected_category != "All":
    df = df[df["category"] == selected_category]


# =========================
# DASHBOARD KPIs
# =========================
st.title("💰 Personal Finance Assistant")

col1, col2, col3 = st.columns(3)
col1.metric("Total Spent", f"₹{df['amount'].sum():.2f}")
col2.metric("Transactions", len(df))
col3.metric("Average Expense", f"₹{df['amount'].mean():.2f}")


# =========================
# CATEGORY BAR CHART
# =========================
st.subheader("📊 Spending by Category")

if not df.empty:
    cat_data = df.groupby("category")["amount"].sum()

    fig, ax = plt.subplots()
    cat_data.plot(kind="bar", ax=ax)
    ax.set_ylabel("Amount")
    ax.set_xlabel("Category")

    st.pyplot(fig)
else:
    st.info("No data available for selected filters.")


# =========================
# MONTHLY TREND
# =========================
st.subheader("📈 Monthly Spending Trend")

monthly_data = (
    st.session_state.expenses
    .groupby("month")["amount"]
    .sum()
)

fig2, ax2 = plt.subplots()
monthly_data.plot(marker="o", ax=ax2)
ax2.set_ylabel("Total Spending")
ax2.set_xlabel("Month")

st.pyplot(fig2)


# =========================
# ADD NEW EXPENSE
# =========================
st.subheader("➕ Add New Expense")

with st.form("expense_form"):
    date = st.date_input("Date", value=datetime.today())
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=1.0)
    category = st.selectbox("Category", categories[1:] if len(categories) > 1 else ["Other"])

    submit = st.form_submit_button("Add Expense")

    if submit:
        new_row = {
            "date": pd.to_datetime(date),
            "description": description,
            "amount": amount,
            "category": category,
            "month": pd.to_datetime(date).strftime("%Y-%m")
        }

        st.session_state.expenses = pd.concat(
            [st.session_state.expenses, pd.DataFrame([new_row])],
            ignore_index=True
        )

        st.session_state.expenses.to_csv("data/expenses.csv", index=False)
        st.success("Expense added successfully!")
        st.rerun()


# =========================
# EDIT / DELETE EXPENSES  (STEP 11)
# =========================
st.subheader("📝 Edit / Delete Expenses")
st.info("✏ Edit values directly or 🗑 delete rows. Changes save automatically.")

edited_df = st.data_editor(
    st.session_state.expenses,
    num_rows="dynamic",
    use_container_width=True,
    key="expense_editor"
)

if not edited_df.equals(st.session_state.expenses):
    edited_df["date"] = pd.to_datetime(edited_df["date"])
    edited_df["month"] = edited_df["date"].dt.strftime("%Y-%m")

    st.session_state.expenses = edited_df.copy()
    st.session_state.expenses.to_csv("data/expenses.csv", index=False)

    st.success("Changes saved successfully!")
    st.rerun()
