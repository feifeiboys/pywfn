def factorial(num): # 计算二级阶乘
    res=1
    for i in range(1,num+1,2):
        res*=i
    return res

print(factorial(-1))