#print different response based on:
#1. if one is feeling good and the beer is cheap
#2. if one is feeling good but the cost of beer is too high
#3. if one is not feeling good and the beer is cheap
#4. if one is not feeling good and the beer is expensive
areWeFeelingGood=False
costOfBier=3
if(costOfBier<=4 and areWeFeelingGood):
    print("Cheap beer for the happy")
elif(costOfBier<=4 and not areWeFeelingGood):
    print("Cheap beer for the unhappy")
elif(costOfBier>4 and areWeFeelingGood):
    print("Expensive beer for the happy")
elif(costOfBier>4 and not areWeFeelingGood):
    print("Expensive beer for the unhappy")