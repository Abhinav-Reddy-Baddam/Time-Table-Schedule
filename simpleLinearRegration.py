X = [1,2,3,4,5]
Y = [1,5,6,3,8]
n = len(X)
sum_X = sum(X)
sum_Y = sum(Y)
sum_XY = sum(x*y for x,y in zip(X,Y))
sum_X2 = sum(x**2 for x in X)
m = (n*sum_XY - sum_X*sum_Y)/((n*sum_X2 - (sum_X)**2))
b = (sum_Y - m*sum_X)/n
x_new = int(input("enter new value for x:"))
y_pred = m*x_new + b
print(f"prediction for {x_new} is {y_pred}")
