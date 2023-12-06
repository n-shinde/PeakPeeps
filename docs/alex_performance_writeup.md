## 1. Fake Data Modeling

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

## 2. Performance Testing Results

| route                             | time (ms) |
| --------------------------------- | --------- |
| /routes/popular                   | 259.68    |
| /coupons/purchase                 | 198.53    |
| /users/add_follower               | 167.12    |
| /users/add_follower               | 152.74    |
| /businesses/list                  | 152.74    |
| /routes/followers                 | 116.93    |
| /coupons/edit                     | 97.32     |
| /users/remove_follower            | 78.61     |
| /routes/search                    | 72.14     |
| /routes/complete                  | 70.99     |
| /reviews/add                      | 63.56     |
| /reviews/update                   | 63.56     |
| /coupons/add                      | 49.8      |
| /peepcoins/get                    | 43.79     |
| /users/get_following/{username}   | 34.22     |
| /coupons/business/{business_name} | 27.44     |
| /users/{username}                 | 26.45     |
| /users/create_account             | 25.14     |

## 3. Performance tuning

### /routes/popular

**query:**

```sql
EXPLAIN
WITH
  ranked_routes AS (
    SELECT
      routes.name,
      routes.city,
      routes.length_in_miles,
      AVG(review.rating) AS Rating,
      RANK() OVER (
        ORDER BY
          AVG(review.rating) DESC
      ) AS ranking
    FROM
      routes
      JOIN review ON routes.id = review.route_id
    GROUP BY
      routes.id,
      routes.name,
      routes.city,
      routes.length_in_miles
    HAVING
      COUNT(*) >= 5
  )
SELECT
  name,
  city,
  length_in_miles,
  Rating
FROM
  ranked_routes
WHERE
  ranking <= 10;
```

Explain:

```
Subquery Scan on ranked_routes  (cost=6128.49..6280.24 rows=5518 width=63) (actual time=131.387..131.402 rows=13 loops=1)
  ->  WindowAgg  (cost=6128.49..6225.06 rows=5518 width=75) (actual time=131.385..131.398 rows=13 loops=1)
        Run Condition: (rank() OVER (?) <= 10)
        ->  Sort  (cost=6128.49..6142.29 rows=5518 width=67) (actual time=131.355..131.358 rows=18 loops=1)
              Sort Key: (avg(review.rating)) DESC
              Sort Method: quicksort  Memory: 1832kB
              ->  HashAggregate  (cost=5537.22..5785.55 rows=5518 width=67) (actual time=119.632..126.144 rows=16014 loops=1)
                    Group Key: routes.id
                    Filter: (count(*) >= 5)
                    Batches: 1  Memory Usage: 4369kB
                    Rows Removed by Filter: 484
                    ->  Hash Join  (cost=673.49..4299.72 rows=165000 width=39) (actual time=7.705..79.658 rows=165001 loops=1)
                          Hash Cond: (review.route_id = routes.id)
                          ->  Seq Scan on review  (cost=0.00..3193.00 rows=165000 width=8) (actual time=0.019..11.788 rows=165001 loops=1)
                          ->  Hash  (cost=466.55..466.55 rows=16555 width=35) (actual time=7.651..7.652 rows=16500 loops=1)
                                Buckets: 32768  Batches: 1  Memory Usage: 1352kB
                                ->  Seq Scan on routes  (cost=0.00..466.55 rows=16555 width=35) (actual time=0.009..5.232 rows=16500 loops=1)
Planning Time: 0.292 ms
Execution Time: 132.265 ms
```

Because we aggregate over every row in our reviews and routes table, there's no benefit from adding an index. Most of the work is in the hash join and hash aggregate, which cannot be increased by an index. One option would be to create a materalized view. However, we believe a 10th of a second is acceptbly fast for our current scale

### /coupons/purchase

We have many queries in this route.

#### query 1:

```sql
SELECT id
FROM users
WHERE username = :name
```

explain:

```
Index Scan using users_username_key on users  (cost=0.29..8.30 rows=1 width=4) (actual time=1.274..1.275 rows=1 loops=1)
"  Index Cond: (username = 'username_1'::text)"
```

Because we're already using an index here, there's no room to tune by adding indexes

#### query 2:

```
SELECT id
FROM coupons
WHERE name = :name
```

explain:

```
Seq Scan on coupons  (cost=0.00..654.50 rows=1 width=4) (actual time=43.983..43.984 rows=1 loops=1)
"  Filter: (name = 'coupon_2'::text)"
  Rows Removed by Filter: 33001
Planning Time: 1.547 ms
Execution Time: 44.041 ms
```

Is that a sequential scan I see? This could be improved by adding an index on coupon name

Explain After adding an index:

```
Index Scan using my_coupon_name_idx on coupons  (cost=0.29..8.31 rows=1 width=4) (actual time=1.118..1.120 rows=1 loops=1)
"  Index Cond: (name = 'coupon_2'::text)"
Planning Time: 6.825 ms
Execution Time: 1.158 ms
```

A ~40x performance increase alright I guess, definetly going to keep this index

#### Query 3:

```sql
SELECT valid FROM coupons WHERE name = :coupon_name
```

Explain:

```
Seq Scan on coupons  (cost=0.00..654.50 rows=1 width=1) (actual time=5.189..5.190 rows=1 loops=1)
"  Filter: (name = 'coupon_2'::text)"
  Rows Removed by Filter: 33001
Planning Time: 0.082 ms
Execution Time: 5.235 ms
```

Like last query, this can be improved by adding an index on coupon name

Explain after adding index:

```
Index Scan using my_coupon_name_idx on coupons  (cost=0.29..8.31 rows=1 width=1) (actual time=0.078..0.079 rows=1 loops=1)
"  Index Cond: (name = 'coupon_2'::text)"
Planning Time: 0.063 ms
Execution Time: 0.107 ms
```

Once again, we see massive performance gains. Admitedly, 5ms is already okay, but we're going to add that index anyways for the other queries.

#### Query 4:

```sql
SELECT (SELECT SUM(change) FROM user_peepcoin_ledger WHERE user_id = :user_id) >= price
FROM coupons
WHERE name = :coupon_name
```

Explain:

```
Seq Scan on coupons  (cost=6208.58..6863.08 rows=1 width=1) (actual time=117.461..119.499 rows=1 loops=1)
"  Filter: (name = 'coupon_2'::text)"
  Rows Removed by Filter: 33001
  InitPlan 1 (returns $1)
    ->  Finalize Aggregate  (cost=6208.57..6208.58 rows=1 width=8) (actual time=114.899..116.933 rows=1 loops=1)
          ->  Gather  (cost=6208.46..6208.57 rows=1 width=8) (actual time=114.773..116.924 rows=2 loops=1)
                Workers Planned: 1
                Workers Launched: 1
                ->  Partial Aggregate  (cost=5208.46..5208.47 rows=1 width=8) (actual time=103.938..103.939 rows=1 loops=2)
                      ->  Parallel Seq Scan on user_peepcoin_ledger  (cost=0.00..5208.44 rows=7 width=4) (actual time=33.577..103.922 rows=6 loops=2)
                            Filter: (user_id = 2)
                            Rows Removed by Filter: 189745
Planning Time: 0.205 ms
Execution Time: 119.625 ms
```

We're doing a sequential scan on coupons by name, which suggests giving adding an index for that a try, but we're also doing a sequential scan on user_peepcoin_ledger on the user id, so giving an index on that a try too should help

Explain after adding the 2 indexes:

```
Index Scan using my_coupon_name_idx on coupons  (cost=50.46..58.48 rows=1 width=1) (actual time=7.350..7.354 rows=1 loops=1)
"  Index Cond: (name = 'coupon_2'::text)"
  InitPlan 1 (returns $0)
    ->  Aggregate  (cost=50.16..50.17 rows=1 width=8) (actual time=7.305..7.306 rows=1 loops=1)
          ->  Bitmap Heap Scan on user_peepcoin_ledger  (cost=4.52..50.13 rows=12 width=4) (actual time=7.267..7.295 rows=14 loops=1)
                Recheck Cond: (user_id = 2)
                Heap Blocks: exact=14
                ->  Bitmap Index Scan on my_user_id_idx  (cost=0.00..4.51 rows=12 width=0) (actual time=7.253..7.253 rows=14 loops=1)
                      Index Cond: (user_id = 2)
Planning Time: 0.299 ms
Execution Time: 7.402 ms
```

Cool! We changed the scan types which tells us that the indexes are being used. Additionally, we also saw performance increase on the magnitude of 10, which is quite worth it

#### Query 5:

```sql
INSERT INTO user_peepcoin_ledger (user_id, change) VALUES (:user_id, -1 * (SELECT price FROM coupons where name = :coupon_name))
```

Explain:

```
Insert on user_peepcoin_ledger  (cost=654.50..654.51 rows=0 width=0) (actual time=2.986..2.987 rows=0 loops=1)
  InitPlan 1 (returns $0)
    ->  Seq Scan on coupons  (cost=0.00..654.50 rows=1 width=4) (actual time=2.341..2.342 rows=1 loops=1)
"          Filter: (name = 'coupon_2'::text)"
          Rows Removed by Filter: 33001
  ->  Result  (cost=0.00..0.01 rows=1 width=24) (actual time=2.350..2.351 rows=1 loops=1)
Planning Time: 0.083 ms
Trigger for constraint user_peepcoin_ledger_user_id_fkey: time=1.330 calls=1
Execution Time: 4.365 ms
```

Another case of sequential scan on coupon name probably slowing us down. Going to add an index for that

Explain after adding index:

```
Insert on user_peepcoin_ledger  (cost=8.31..8.32 rows=0 width=0) (actual time=0.129..0.129 rows=0 loops=1)
  InitPlan 1 (returns $0)
    ->  Index Scan using my_coupon_name_idx on coupons  (cost=0.29..8.31 rows=1 width=4) (actual time=0.018..0.019 rows=1 loops=1)
"          Index Cond: (name = 'coupon_2'::text)"
  ->  Result  (cost=0.00..0.01 rows=1 width=24) (actual time=0.022..0.022 rows=1 loops=1)
Planning Time: 0.076 ms
Trigger for constraint user_peepcoin_ledger_user_id_fkey: time=0.105 calls=1
Execution Time: 0.266 ms
```

Sweet, we changed from using a sequential scan to an index scan, and saw a large performance increase. We'll keep the index (even though we were going to anyways)

#### Query 6:

```sql
INSERT INTO user_coupon_ledger (user_id, coupon_id, change) VALUES (:user_id, :coupon_id, 1)
```

Explain:

```
Insert on user_coupon_ledger  (cost=0.00..0.01 rows=0 width=0) (actual time=2.564..2.564 rows=0 loops=1)
  ->  Result  (cost=0.00..0.01 rows=1 width=24) (actual time=0.216..0.217 rows=1 loops=1)
Planning Time: 0.033 ms
Trigger for constraint user_coupon_ledger_coupon_id_fkey: time=0.396 calls=1
Trigger for constraint user_coupon_ledger_user_id_fkey: time=0.850 calls=1
Execution Time: 3.855 ms
```

We're not doing any scanning, just a simple insert, so there's no room for index-optimization here

### Users/add_follower

We have a few queries here too

#### Query 1

```sql
SELECT id
    FROM users
    WHERE username = :name
```

explain:

```
Index Scan using users_username_key on users  (cost=0.29..8.30 rows=1 width=4) (actual time=7.202..7.207 rows=1 loops=1)
"  Index Cond: (username = 'username_3'::text)"
Planning Time: 0.386 ms
Execution Time: 7.380 ms
```

This is already using an index scan so our job here is done

#### Query 2

```sql
SELECT user_id, follower_id
FROM followers
WHERE user_id = :user_id AND follower_id = :follower_id
```

explain:

```
Seq Scan on followers  (cost=0.00..3367.00 rows=1 width=8) (actual time=259.611..259.612 rows=0 loops=1)
  Filter: ((user_id = 2) AND (follower_id = 1))
  Rows Removed by Filter: 165001
Planning Time: 2.490 ms
Execution Time: 259.673 ms
```

This is a sequential scan on followers which is removing the vast majority of the rows, which suggests to us that we should use an index on both the user_id and the follower_id

Explain after adding the 2 indexes:

```
Bitmap Heap Scan on followers  (cost=8.93..12.95 rows=1 width=8) (actual time=0.149..0.151 rows=1 loops=1)
  Recheck Cond: ((follower_id = 2) AND (user_id = 1))
  Heap Blocks: exact=1
  ->  BitmapAnd  (cost=8.93..8.93 rows=1 width=0) (actual time=0.137..0.138 rows=0 loops=1)
        ->  Bitmap Index Scan on follower_id_idxcoupon  (cost=0.00..4.34 rows=6 width=0) (actual time=0.112..0.113 rows=3 loops=1)
              Index Cond: (follower_id = 2)
        ->  Bitmap Index Scan on user_id_idx  (cost=0.00..4.34 rows=6 width=0) (actual time=0.021..0.021 rows=10 loops=1)
              Index Cond: (user_id = 1)
Planning Time: 0.627 ms
Execution Time: 0.208 ms
```

God golly, that was like a ~500X times performance increase. I don't fully understand it, but it looks like it's doing some cool fancy things with bitmaps to get a really cool performance. Can we do better though? Since we're always going to be looking up on both the user_id and follower_id at the same time, I wonder if it's better to use a compound index (an index on user_id, follower_id) instead.

Explain with compound index:

```
Index Only Scan using compound_idx on followers  (cost=0.42..8.44 rows=1 width=8) (actual time=0.138..0.139 rows=1 loops=1)
  Index Cond: ((user_id = 1) AND (follower_id = 2))
  Heap Fetches: 1
Planning Time: 0.500 ms
Execution Time: 0.189 ms
```

This is really cool! It actually was faster, but most of the main was in the planning time instead of hte execution time, probably since it had to orchestrate less fancy bitmap stuff

However, since we need to look up on just the user id in other cases (like getting the number of followers for a person), and having the 2 indexes was practically just as fast as having a compound index, we'll stick to having the 2 seperate indexes

#### Query 3

```sql
INSERT INTO followers (user_id, follower_id)
VALUES (:id, :follower_id)
```

Explain:

```
Insert on followers  (cost=0.00..0.01 rows=0 width=0) (actual time=4.227..4.228 rows=0 loops=1)
  ->  Result  (cost=0.00..0.01 rows=1 width=84) (actual time=0.337..0.338 rows=1 loops=1)
Planning Time: 0.040 ms
Trigger for constraint followers_follower_id_fkey: time=0.767 calls=1
Trigger for constraint followers_user_id_fkey: time=0.201 calls=1
Execution Time: 5.252 ms
```

This is a simple insert statement that doesn't have any look ups (besides the foreign key checks), so it can't be improved by an index
