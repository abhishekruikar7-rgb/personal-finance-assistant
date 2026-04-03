import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def category_pie_chart(df):
    if df.empty:
        st.info("No data for pie chart.")
        return
    
    cat_data = df.groupby("category")["amount"].sum().reset_index()
    fig = px.pie(cat_data, values="amount", names="category", 
                 title="Spending by Category",
                 hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

def spending_trend_chart(df):
    if df.empty:
        st.info("No data for trend chart.")
        return
    
    # Sort by month to ensure trend is chronological
    monthly_data = df.groupby("month")["amount"].sum().reset_index()
    monthly_data = monthly_data.sort_values("month")
    
    fig = px.line(monthly_data, x="month", y="amount", 
                  title="Monthly Spending Trend",
                  markers=True,
                  line_shape="spline",
                  render_mode="svg")
    fig.update_layout(xaxis_title="Month", yaxis_title="Total Spent (₹)")
    st.plotly_chart(fig, use_container_width=True)

def budget_vs_actual_chart(categories, spent_vals, budget_vals):
    if not categories:
        st.info("No budget data to display.")
        return
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Spent", x=categories, y=spent_vals, marker_color="#1f77b4"))
    fig.add_trace(go.Bar(name="Budget", x=categories, y=budget_vals, marker_color="#ff4b4b"))
    
    fig.update_layout(barmode="group", title="Budget vs. Actual Spending",
                      xaxis_title="Category", yaxis_title="Amount (₹)")
    st.plotly_chart(fig, use_container_width=True)
