import pandas as pd
from sklearn.linear_model import LinearRegression

# Training data
data = {
    'area': [1000, 1500, 2000, 2500, 3000],
    'bedrooms': [2, 3, 3, 4, 5],
    'age': [10, 8, 6, 4, 2],
    'price': [3, 4.5, 6, 7.5, 9]
}

df = pd.DataFrame(data)

# Features and target
X = df[['area', 'bedrooms', 'age']]
y = df['price']

# Train model
model = LinearRegression()
model.fit(X, y)

# User input
area = float(input("area:"))
bedrooms = int(input("bedrooms:"))
age = int(input("age:"))

# Prediction
prediction = model.predict([[area, bedrooms, age]])

# Output (only predicted price)
print(f"price of the house is {prediction[0]} lakh")