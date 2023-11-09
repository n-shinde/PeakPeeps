# Routes

## Get Friends Routes
Curl:

curl -X 'GET' \
  'https://peak-peeps.onrender.com/routes/friends?friend_username=Biker_Dave' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!'

## Report Route:
Curl:

curl -X 'POST' \
  'https://peak-peeps.onrender.com/routes/report' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Steve",
  "user_id": 0,
  "location": "string",
  "coordinates": [
    0
  ],
  "length": 0,
  "difficulty": 0,
  "activities": "string"
}'


# Reviews

## Add Review
Curl:

curl -X 'POST' \
  'https://peak-peeps.onrender.com/reviews/add' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": 3,
  "route_id": 7,
  "description": "Horrible time ong",
  "rating": 1
}'

# Peepcoins

## Buy Coupon
Curl:

curl -X 'POST' \
  'https://peak-peeps.onrender.com/peepcoins/purchase/coupon' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "coupon_id": 1,
  "user_id": 1
}'

## Put PeepCoins
Curl Statement:

curl -X 'PUT' \
  'https://peak-peeps.onrender.com/peepcoins/add' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": 1,
  "change": 10
}'


# Businesses

## Put Business
Curl:

curl -X 'PUT' \
  'https://peak-peeps.onrender.com/business/add' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Starbucks",
  "address": "Chorro St"
}'

# Coupons

## Put Coupon
Curl:

curl -X 'PUT' \
  'https://peak-peeps.onrender.com/coupons/add' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "business_id": 5,
  "name": "Free Pastry",
  "cost": 50
}'

# Users

## Create Account
Curl:

curl -X 'POST' \
  'https://peak-peeps.onrender.com/users/create_account' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "Steve"
}'

## Add Follower
Curl:

curl -X 'POST' \
  'https://peak-peeps.onrender.com/users/add_follower' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_to_update": {
    "username": "Lucas"
  },
  "follower_to_add": {
    "username": "Steve"
  }
}'

## Follow User
Curl:

curl -X 'POST' \
  'https://peak-peeps.onrender.com/users/follow' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_requesting_follow": {
    "username": "string1"
  },
  "other_user": {
    "username": "Steve"
  }
}'

## Remove Follower
Curl:

curl -X 'POST' \
  'https://peak-peeps.onrender.com/users/remove_follower' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_to_update": {
    "username": "Lucas"
  },
  "follower_to_remove": {
    "username": "Steve"
  }
}'
