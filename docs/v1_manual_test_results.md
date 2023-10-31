Victor, a busy software engineer at Apple, during one long weekend decides to come to SLO because he has heard of many cool sites to see from his co-workers. After a 3 hour drive, he finally arrives in SLO, but doesn’t know which sites to see and try first. He then remembered an app called Peak Peeps, which helps find sites/routes to try that one of his-coworkers mentioned. So, he downloaded Peak Peeps from the App Store. First, Victor requests to view popular routes to see which are the best routes to try by calling GET /routes/popular.

A couple minutes later, he decided to go with one of the 2 popular routes with a rating of at least 4 stars - the P Hike.

After he hiked to the P, he was amazed by the scenery and wanted to leave a review. So, he called POST /reviews/new and entered his username/name and the “rating” for that route.

# Added route - Steve
Curl Statement:

curl -X 'POST' \
  'https://peak-peeps.onrender.com/routes/add' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Steve",
  "user_id": 2,
  "location": "The P",
  "coordinates": [
    100,100
  ],
  "length": 0.9,
  "difficulty": 5,
  "activities": "Took pictures"
}'

Response: 
"OK"

# Added route - Genshin Impacter
Curl Statement:

curl -X 'POST' \
  'https://peak-peeps.onrender.com/routes/add' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Genshin Impacter",
  "user_id": 4,
  "location": "Bishop Peak",
  "coordinates": [
    50,0
  ],
  "length": 8,
  "difficulty": 8,
  "activities": "Boulder climbing, pretty views"
}'

Response: 
"OK"

# Added route - Lucas 
Curl Statement:

curl -X 'POST' \
  'https://peak-peeps.onrender.com/routes/add' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Lucas Pierce",
  "user_id": 5,
  "location": "Madonna",
  "coordinates": [
    25,69
  ],
  "length": 12.8,
  "difficulty": 6,
  "activities": "Ate cake and hiked"
}'

Response: 
"OK"

# Added review on his route - Steve
Curl Statement:

curl -X 'POST' \
  'https://peak-peeps.onrender.com/reviews/add' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "author_name": "Steve",
  "route_id": 7,
  "description": "Great view of Cal Poly! Easy hike, kind of crowded though.",
  "rating": 4
}'

Response: 
"OK"

# Added review on his route - Genshin Impacter
Curl Statement:

curl -X 'POST' \
  'https://peak-peeps.onrender.com/reviews/add' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "author_name": "Genshin Impacter",
  "route_id": 8,
  "description": "Hardest hike of my life! Beautiful view at the top, had to climb some rocks beware!!! :0 ",
  "rating": 3
}'

Response: 
"OK"

# Added review on his route - Lucas 
Curl Statement:

curl -X 'POST' \
  'https://peak-peeps.onrender.com/reviews/add' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "author_name": "Lucas Pierce",
  "route_id": 9,
  "description": "Grabbed some cake from Madonna Inn to fuel my hike. Beautiful area, recommend bringing picnic items!",
  "rating": 5
}'

Response:
"OK"

# Victor retrieves popular routes
Curl Statement:

curl -X 'GET' \
  'https://peak-peeps.onrender.com/routes/popular' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!'

Response:
[
  "The P",
  "Madonna"
]

# Victor posts route
Curl Statement:

curl -X 'POST' \
  'https://peak-peeps.onrender.com/routes/add' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Victor",
  "user_id": 3,
  "location": "The P",
  "coordinates": [
    100,100
  ],
  "length": 0.9,
  "difficulty": 5,
  "activities": "Took pictures"
}'

Response:
"OK"

# Victor posts review on the P Hike
Curl Statement:

curl -X 'POST' \
  'https://peak-peeps.onrender.com/reviews/add' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "author_name": "Victor",
  "route_id": 7,
  "description": "Lived up to the hype! Met some great students on the way there.",
  "rating": 5
}'

Response:
"OK"

