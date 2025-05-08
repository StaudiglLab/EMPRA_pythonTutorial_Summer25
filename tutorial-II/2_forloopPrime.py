import time

#get starting time
tstart=time.time()

#Nested for loops
#count all prime numbers from 1-100
nPrime=0
for num in range(1,11):
    isPrime=True
    for div in range(2,num):
        if(num%div==0):
            isPrime=False
    if(isPrime):
        nPrime=nPrime+1

tstop=time.time()
print("Number of primes:%d"%nPrime)
print("Time taken to run: %.3f milliseconds"%(1e3*(tstop-tstart)))