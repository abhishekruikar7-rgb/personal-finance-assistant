import streamlit as st
import pandas as pd
from datetime import datetime
import os
import joblib

from utils.database import init_db, get_connection, add_expense, get_expenses, update_expenses_from_df, set_budget, get_budgets
from utils.auth import check_auth, login_user, signup_user, logout
from utils.reports import generate_pdf_report
from components.ui import apply_custom_css, kpi_card, budget_alert
from components.charts import category_pie_chart, spending_trend_chart, budget_vs_actual_chart

# Page Setup
st.set_page_config(page_title="Personal Finance Assistant", layout="wide", page_icon="💰")
init_db()
apply_custom_css()

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

# --- AUTH SECTOR ---
if not st.session_state.authenticated:
    st.sidebar.title("🔐 Authentication")
    auth_mode = st.sidebar.selectbox("Choose Mode", ["Login", "Signup"])
    
    with st.container():
        st.title("💰 Welcome to Finance Assistant")
        col1, col2 = st.columns(2)
        
        with col1:
            st.image("https://img.freepik.com/free-vector/finance-department-employees-analyzing-financial-report-graphs-charts_74855-14194.jpg", use_container_width=True)
        
        with col2:
            st.subheader(f"{auth_mode} to continue")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if auth_mode == "Login":
                if st.button("Login"):
                    if login_user(username, password):
                        st.success(f"Welcome back, {username}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
            else:
                if st.button("Signup"):
                    if signup_user(username, password):
                        st.info("Now please login with your account.")
    st.stop()

# --- LOGGED IN SECTOR ---

# Sidebar Navigation
st.sidebar.title(f"👋 Hello, {st.session_state.username}")
nav = st.sidebar.radio("Navigation", ["📊 Dashboard", "➕ Expenses", "🎯 Budgets", "💡 ML Insights"])

if st.sidebar.button("🚪 Logout"):
    logout()

# Load Data
expenses_df = get_expenses(st.session_state.user_id)
categories = ["Food", "Transport", "Rent", "Shopping", "Entertainment", "Health", "Other"]

# --- NAVIGATION VIEWS ---

if nav == "📊 Dashboard":
    st.title("💸 Your Financial Overview")
    
    # Filter by Month
    all_months = sorted(expenses_df['month'].unique().tolist(), reverse=True) if not expenses_df.empty else []
    current_month = datetime.today().strftime("%Y-%m")
    if current_month not in all_months:
        all_months = [current_month] + all_months
        
    selected_month = st.sidebar.selectbox("Filter by Month", all_months, index=0)
    month_df = expenses_df[expenses_df['month'] == selected_month] if not expenses_df.empty else pd.DataFrame()
    
    # KPIs
    c1, c2, c3 = st.columns(3)
    total_spent = month_df['amount'].sum() if not month_df.empty else 0
    with c1: kpi_card("Total Spent", f"₹{total_spent:.2f}", "💵")
    with c2: kpi_card("Transactions", len(month_df), "📋")
    with c3: 
        avg = month_df['amount'].mean() if not month_df.empty else 0
        kpi_card("Avg Expense", f"₹{avg:.2f}", "⚖️")
    
    st.markdown("---")
    
    # Charts
    col_l, col_r = st.columns(2)
    with col_l:
        spending_trend_chart(expenses_df)
    with col_r:
        category_pie_chart(month_df)
    
    # Budget Alerts
    st.subheader("⚠️ Budget Status")
    budgets = get_budgets(st.session_state.user_id, selected_month)
    if not budgets.empty:
        for idx, row in budgets.iterrows():
            cat = row['category']
            limit = row['amount']
            spent = month_df[month_df['category'] == cat]['amount'].sum() if not month_df.empty else 0
            if spent >= limit:
                budget_alert(cat, spent, limit)
            else:
                progress = spent / limit
                st.write(f"**{cat}**: ₹{spent:.2f} / ₹{limit:.2f}")
                st.progress(min(progress, 1.0))
    else:
        st.info("No budgets set for this month. Go to the 'Budgets' tab to set one!")

elif nav == "➕ Expenses":
    st.title("🧾 Manage Expenses")
    
    with st.expander("Add New Expense", expanded=True):
        with st.form("add_exp"):
            d1, d2 = st.columns(2)
            date = d1.date_input("Date", value=datetime.today())
            amount = d2.number_input("Amount (₹)", min_value=0.01)
            
            c1, c2 = st.columns(2)
            desc = c1.text_input("Description (e.g. Starbucks coffee)")
            cat = c2.selectbox("Category", categories)
            
            submit = st.form_submit_button("Save Expense")
            if submit:
                add_expense(st.session_state.user_id, date, desc, amount, cat)
                st.success("Expense recorded!")
                st.rerun()
                
    st.subheader("📝 Edit / Delete Transactions")
    if not expenses_df.empty:
        # Display editable table
        edit_cols = ["date", "description", "amount", "category"]
        display_df = expenses_df[edit_cols].copy()
        
        edited_df = st.data_editor(display_df, num_rows="dynamic", use_container_width=True)
        
        if st.button("💾 Save Changes"):
            update_expenses_from_df(st.session_state.user_id, edited_df)
            st.success("All changes saved!")
            st.rerun()
            
        # Download Reports
        st.markdown("---")
        st.subheader("📥 Export Data")
        col1, col2 = st.columns(2)
        
        csv = expenses_df.to_csv(index=False)
        col1.download_button(label="📄 Download CSV", data=csv, file_name="expenses.csv", mime="text/csv")
        
        # PDF Generator (Filtered by Month)
        # We'll use the month filter from the sidebar or just the latest month
        latest_month = expenses_df['month'].max()
        month_df = expenses_df[expenses_df['month'] == latest_month]
        pdf_path = generate_pdf_report(st.session_state.username, latest_month, month_df)
        with open(pdf_path, "rb") as f:
            col2.download_button(label="📜 Download Monthly PDF", data=f, file_name=f"report_{latest_month}.pdf", mime="application/pdf")
    else:
        st.write("No transactions found.")

elif nav == "🎯 Budgets":
    st.title("🎯 Monthly Budgets")
    st.write("Set spending limits for different categories to stay on track.")
    
    selected_month = st.sidebar.selectbox("Budget Month", [datetime.today().strftime("%Y-%m")], index=0)
    
    with st.form("budget_form"):
        col1, col2 = st.columns(2)
        b_cat = col1.selectbox("Category", categories)
        b_amt = col2.number_input("Budget Amount (₹)", min_value=0.0)
        
        if st.form_submit_button("Set Budget"):
            set_budget(st.session_state.user_id, b_cat, b_amt, selected_month)
            st.success(f"Budget for {b_cat} set to ₹{b_amt:.2f}")

    st.subheader("Current Budgets")
    curr_budgets = get_budgets(st.session_state.user_id, selected_month)
    if not curr_budgets.empty:
        st.table(curr_budgets)
        
        # Visually compare
        month_df = expenses_df[expenses_df['month'] == selected_month]
        spent_data = month_df.groupby("category")["amount"].sum().reset_index()
        
        comp_df = pd.merge(curr_budgets, spent_data, on="category", how="left").fillna(0)
        budget_vs_actual_chart(comp_df['category'].tolist(), comp_df['amount_y'].tolist(), comp_df['amount_x'].tolist())
    else:
        st.info("No budgets defined for this month.")

elif nav == "💡 ML Insights":
    st.title("🧠 Spending Insights")
    
    if expenses_df.empty:
        st.warning("Need transaction data for ML predictions.")
    else:
        tab1, tab2 = st.tabs(["🔮 Future Prediction", "🏷 Auto-Categorization"])
        
        with tab1:
            st.subheader("Predicted Spending for Next Month")
            try:
                model_pred = joblib.load("models/prediction_model.pkl")
                last_month_num = int(expenses_df['date'].dt.month.max())
                next_month_num = (last_month_num % 12) + 1
                
                prediction = model_pred.predict([[next_month_num]])[0]
                
                st.metric("Estimated Next Month", f"₹{prediction:,.2f}")
                st.info("Note: This simple prediction is based on monthly trends.")
            except Exception as e:
                st.error(f"Prediction model not loaded or failing: {e}")
                
        with tab2:
            st.subheader("Smart Category Suggestion")
            test_desc = st.text_input("Enter a description to see how I would categorize it:")
            if test_desc:
                try:
                    cat_model = joblib.load("models/category_model.pkl")
                    pred_cat = cat_model.predict([test_desc])[0]
                    st.write(f"Proposed Category: **{pred_cat}**")
                except Exception as e:
                    st.error("Categorization model error.")
