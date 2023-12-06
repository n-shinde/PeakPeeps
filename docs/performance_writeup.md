# Fake Data Modeling

Data Populating Logic:
On average, every user writes 5 reviews and has 5 followers.
Every user completes 5 routes (5 lines to completed ledger)
For every 2 users, there is one unique route.
For every 2 users, there is one business.
For every business, there are two coupons.

On average, a user buys one coupon, adding one line to the coupon ledger. 
For every route added, review made, route completed (say 5 per person), and coupon purchased, a line is added to the peepcoin ledger. On average, this results in 11.5 lines added to the ledger per person. 

33,000 users
16,500 routes
16,500 businesses
165,000 reviews
165,000 followers
33,000 coupons
33,000 coupons purchased to coupon ledger
165,000 lines to completed route ledger
380,000 lines to peepcoin ledger 
- 20,000 for making routes, 200,000 for writing reviews, 40,000 for purchasing coupons, and 200,000 for completing routes

**CSV Files were made using a Jupyter Notebook, seen in docs/dataPopulatingScript.md**

# Performance results of hitting endpoints

# Performance tuning
