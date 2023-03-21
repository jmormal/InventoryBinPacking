import time
a1=time.time()
a=0
for i in range(200000000):
    a+=i**2-i**2+1
print(time.time()-a1)