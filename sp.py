import numpy as np

# Training data (AND gate)
X = np.array([
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1]
])

y = np.array([0, 0, 0, 1])

# Initialize weights and bias
weights = np.zeros(2)
bias = 0
lr = 0.1

# Training
for _ in range(10):  # epochs
    for i in range(len(X)):
        linear = np.dot(X[i], weights) + bias
        prediction = 1 if linear >= 0 else 0

        # Update
        error = y[i] - prediction
        weights += lr * error * X[i]
        bias += lr * error

# Testing
for i in range(len(X)):
    linear = np.dot(X[i], weights) + bias
    prediction = 1 if linear >= 0 else 0
    print(X[i], "->", prediction)