import math

arr=[]
n=int(input("enter length of array:"))
for x in range(n):
    value = int(input(f"enter element at {x}:"))
    arr.append(value)
arr.sort()
print("array:",arr)
mean=sum(arr)/n
print(f"mean is {mean}")
if n%2==0:
    print(f"median is {(arr[n//2]+arr[n//2 -1])/2}")
else:
    print(f"median is {arr[n//2 +1]}")
freq={}
for x in arr:
    if x in freq:
        freq[x]+=1
    else:
        freq[x]=1
print(f"mode: {max(freq,key=freq.get)}")
varience_sum=0
for x in arr:
    varience_sum+=(mean-x)**2
varience=varience_sum/n
print(f"varience is {varience}")
standard_deviation =math.sqrt(varience)
print(f"standead deviation is {standard_deviation}")
