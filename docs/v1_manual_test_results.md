# Example workflow

Victor, a busy software engineer at Apple, during one long weekend decides to come to SLO because he has heard of many cool sites to see from his co-workers. After a 3 hour drive, he finally arrives in SLO, but doesn’t know which sites to see and try first. He then remembered an app called Peak Peeps, which helps find sites/routes to try that one of his-coworkers mentioned. So, he downloaded Peak Peeps from the App Store. First, Victor requests to view popular routes to see which are the best routes to try by calling GET /routes/popular. Victor sees that there are 3 routes with a high “popularity_index” and 9 “five_star_reviews”.

A couple minutes later, he decided to go with one of the 3 routes that was close to his hotel as described by the “location” attribute.

After he completed the route, he was amazed by the scenery and wanted to leave a review. So, he called POST /reviews/new and entered his username/name and the “rating” for that route.

# Testing results
<Repeated for each step of the workflow>
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
  'https://centralcoastcauldrons.vercel.app/catalog/' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.
