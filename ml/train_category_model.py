import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib

# 1. Load expense data
df = pd.read_csv("data/expenses.csv")

# 2. Input (description) and Output (category)
X = df["description"]
y = df["category"]

# 3. Create ML pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", MultinomialNB())
])

# 4. Train model
model.fit(X, y)

# 5. Save trained model
joblib.dump(model, "models/category_model.pkl")

print("✅ Expense categorization model trained successfully!")
