Steve is a busy software engineer at Apple, during one long weekend he decides to come to San Luis Obispo because it is known for its outside activities. After the three hour drive, he finally arrives in SLO. Remembering the app, Peak Peeps, he wanted to document his experience to show his friends back home in the Bay Area. Victor uses the routes/add Post call to add the P-Hike to one of his hiked routes. He gives the length of the hike 0.9 miles and a difficulty of 5. He then fills out the activity of taking pictures.

# Testing results
Curl Statement:

curl -X 'POST' \                
  'https://peak-peeps.onrender.com/routes/add' \
  -H 'accept: application/json' \
  -H 'access_token: PeepCoins123!' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Steve",
  "user_id": 2,
  "location": "P-Hike",
  "coordinates": [
    100, 100
  ],
  "length": 0.9,
  "difficulty": 5,
  "activities": "Taking Pictures"
}'

Response:
"OK"%
