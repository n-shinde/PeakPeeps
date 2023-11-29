**Case 1: Lost Update with PeepCoin Balances**

Problem:

In this situation, a user Lucas has a balance of 100 PeepCoins. 
He decides to go on a 20-mile hike to complete a challenge on the app, so he logs his hike, 
which updates his PeepCoin balance by adding 50 PeepCoins. After the hike, he’s very hungry, so he visits a 
local sandwich shop and redeems a coupon worth 20 PeepCoins for a free BLT. As a result, 20 PeepCoins are deducted 
from the original balance, and not the updated balance, so he appears to have 100-20 = 80 PeepCoins. 
But he doesn’t see the update where 50 PeepCoins were also added from completing the hike. 

![Diagram:](https://github.com/n-shinde/PeakPeeps/assets/104091934/e576b0d7-f65a-48c8-837e-5958bd0130a9)

Solution:

To avoid lost updates with PeepCoin balances, we have created a separate table called user_peepcoin_ledger that keeps records of every transaction that involves changing the PeepCoin balance of a user. When any function that executes any transaction involving PeepCoins is called, the user_peepcoin_ledger is updated, with a “change” column that stores the amount added or subtracted from executing the transaction. Then, if the balance of the user needs to be retrieved, the “change” column is summed up and returned as the current balance, instead of storing the balance in a variable and adding or subtracting from it. This prevents lost updates as every transaction is being stored in the ledger with the changes in real time. 

**Case 2: Phantom Read**

Problem:

Jane wants to see what the most popular routes are before she goes hiking. So she calls the /routes/popular endpoint and sees 4 routes on the page. A few seconds after, Bob posts a 4 star review on a route that was previously not reviewed, so this route now qualifies as a popular route according to our logic. After packing some items for her trip, Jane refreshes the popular routes page, sending another call to /routes/popular. This time she sees 5 popular routes on the page instead of the 4 routes she saw originally.

![Diagram:](https://github.com/n-shinde/PeakPeeps/assets/104091934/4b66759a-b791-4a50-97c7-7e41a0f6a9a3)

Solution:

To prevent a phantom read, we would have to set the isolation level to serializable, which would not be useful in our case because we want users to see the changes to the popular routes page in real time, so that they have the most current version of popular routes available. We don’t want users to not be able to write a review just because someone else is viewing the popular routes. If we had a frontend application of this, we think that most users would be viewing the popular routes page simultaneously, so having transactions run one-by-one would drastically slow down the responsiveness of our app. So we chose to keep this functionality intact instead of an issue that must be solved.

**Case 3: Non Repeatable Read**

Problem:

We run the check peep coins balance to compare against the balance of a coupon to ensure the purchaser has sufficient funds to cover the price. Then later we read the price of the coupon again to deduct the coins from the person's account balance. If the business changes the price of the coupon between these two statements, the purchaser could end up with a negative account balance.

![Diagram:](https://github.com/n-shinde/PeakPeeps/assets/104091934/6e3140c2-8c29-4e81-9e93-f018c01e2c4b)


Solution:

We set the isolation level for the purchase_peepcoin endpoint to be read_repeatable, so the second time the price of the coupon is read, it returns the  same read as the first time.
