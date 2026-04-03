import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        .main {
            background-color: #f0f2f6;
        }
        .stButton>button {
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: bold;
            transition: 0.3s;
        }
        .stButton>button:hover {
            transform: scale(1.05);
        }
        .kpi-card {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        .kpi-card h2 {
            margin: 0;
            color: #31333f;
            font-size: 1.5rem;
        }
        .kpi-card p {
            margin: 10px 0 0 0;
            color: #1f77b4;
            font-size: 2rem;
            font-weight: bold;
        }
        .budget-alert {
            background-color: #ffe8e8;
            border-left: 5px solid #ff4b4b;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        </style>
    """, unsafe_allow_html=True)

def kpi_card(title, value, icon=""):
    st.markdown(f"""
        <div class="kpi-card">
            <h2>{icon} {title}</h2>
            <p>{value}</p>
        </div>
    """, unsafe_allow_html=True)

def budget_alert(category, spent, budget):
    st.markdown(f"""
        <div class="budget-alert">
            🚨 <b>{category}</b> limit reached! Spent: ₹{spent:.2f} / ₹{budget:.2f}
        </div>
    """, unsafe_allow_html=True)
