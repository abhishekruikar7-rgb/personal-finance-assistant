import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression

# Load data
df = pd.read_csv("data/expenses.csv")

# Convert date column to datetime
df["date"] = pd.to_datetime(df["date"])

# Extract month number
df["month"] = df["date"].dt.month

# Group by month
monthly_expense = df.groupby("month")["amount"].sum().reset_index()

X = monthly_expense[["month"]]
y = monthly_expense["amount"]

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model
joblib.dump(model, "models/prediction_model.pkl")

print("✅ Spending prediction model trained successfully!")
