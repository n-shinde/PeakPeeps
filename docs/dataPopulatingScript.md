Create csv files for adding data to database


```python
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import random

user_length = 33000
route_length = 16500
reviews_length = 165000
```


```python
# users

header = ['id', 'username']
data = []

for i in range(user_length):
    data.append([i,f"username_{i}"])

data = pd.DataFrame(data, columns=header)
data.to_csv('users_data.csv', index=False)

    
```


```python
# routes

header = ['id', 'name','address','city','state','length_in_miles','added_by_user_id','coordinates']
data = []

for i in range(route_length):
    data.append([i,f"route_{i}",f'fake address {i}23', 'San Luis Obispo','CA',random.randint(1,10),i,[i,i+1]])

data = pd.DataFrame(data, columns=header)
data.to_csv('routes_data.csv', index=False)
```


```python
# businesses

header = ['id', 'name','address','commissions_rate']
data = []

for i in range(route_length):
    data.append([i,f"business_{i}",f'fake address {i}23', random.random()])

data = pd.DataFrame(data, columns=header)
data.to_csv('businesses_data.csv', index=False)
```


```python
# reviews

header = ['id', 'description','rating','route_id','user_id','difficulty']
data = []

for i in range(reviews_length):
    data.append([i,f"This route was so cool",random.randint(0,5), random.randint(0,route_length-1), 
                 random.randint(0,user_length-1),random.randint(0,5)])

data = pd.DataFrame(data, columns=header)
data.to_csv('reviews_data.csv', index=False)
```


```python
# followers

header = ['follower_id', 'user_id']
data = []

for i in range(int(reviews_length/2)):
    
    user = random.randint(0,user_length-1)
    follower = random.randint(0,user_length-1)

    while [user,follower] in data:
        user = random.randint(0,user_length-1)
        follower = random.randint(0,route_length-1)
        
    data.append([follower, user])
    data.append([user, follower])

data = pd.DataFrame(data, columns=header)
data.to_csv('followers_data.csv', index=False)
```


```python
# coupons

header = ['id', 'name','valid','business_id','price']
data = []

for i in range(user_length):
    data.append([i,f"coupon_{i}",True, random.randint(0,route_length-1),random.randint(10,50)])

data = pd.DataFrame(data, columns=header)
data.to_csv('coupons_data.csv', index=False)
```


```python
# coupon ledger

header = ['id', 'user_id','coupon_id','change']
data = []

for i in range(user_length):
    data.append([i,random.randint(0,user_length-1),random.randint(0,user_length-1), 1])

data = pd.DataFrame(data, columns=header)
data.to_csv('couponLedger_data.csv', index=False)
```


```python
# peepcoin ledger

header = ['id', 'user_id','change']
data = []

for i in range(reviews_length):
    data.append([i,random.randint(0,user_length-1),5]) # Adding reviews

for i in range(reviews_length,reviews_length*2):  
    data.append([i,random.randint(0,user_length-1),15]) # Completing routes

for i in range(reviews_length*2,reviews_length*2+user_length):
    data.append([i,random.randint(0,user_length-1),random.randint(10,30)]) # Buying coupons (should be negative but 
                                                                   # negative balances will mess w functions later)

for i in range(reviews_length*2+user_length,reviews_length*2+user_length+route_length):
    data.append([i,random.randint(0,user_length-1),10]) # Adding routes

data = pd.DataFrame(data, columns=header)
data.to_csv('peepCoinLedger_data.csv', index=False)
```


```python
# completed route ledger

header = ['user_id', 'route_id']
data = []

for i in range(reviews_length):
    user = random.randint(0,user_length-1)
    route = random.randint(0,route_length-1)
    while [user,route] in data:
        user = random.randint(0,user_length-1)
        route = random.randint(0,route_length-1)
        
    data.append([user,route])

data = pd.DataFrame(data, columns=header)
data.to_csv('completedRoute_data.csv', index=False)
```


```python

```


```python

```
