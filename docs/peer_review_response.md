# Code Feedback

1. Changed functions to return "OK" where necessary
2. Changed coordinates to be array of float data types
3. Deleted report route endpoint (covers all feedback related to this one) - we don’t actually have functionality to deal with reported routes, so it doesn't make sense to have this.
4. Changed admin.py to have reset functionality
5. Made usernames unique
6. Made create user account return user id
7. Combined  user_follows_other_user and update_followers endpoints that didn’t make sense to have separated
8. Get popular/followers routes now returns actual information about the route
9. Added a filtering mechanism for getting popular routes, so it only returns the top 10
10. Added a search endpoint to the routes
11. Made “get_user_id_from_username” and “get_route_id_from_name” functions as we make these calls frequently
12. Fixed query parameters to just be in a dictionary, not also a list
13. Fixed coupon logic to accurately assess validity of coupons, and added ability for businesses to edit their coupons.
14. Added condition to check if a review has already been posted for a route by the same user - not perfect logic but keeps someone from spamming the same review to one route for peepcoins.
15. Fixed get friends routes to only return a limit of 10. Added a check to make sure you are friends with a user before you can see their routes (i.e. you both follow each other).
16. Made route names unique, and added a check for similar route names by the same user to eliminate spamming of adding the same route.
17. Added completed_route_ledger to keep track of who completed what route. Allows us to check things like if a user has done a route before posting a review.
18. Added completed route endpoint to give you peepcoins and see what routes you have finished. Only lets you complete each route once. (Ideally we’d have a gps track to determine if you actually completed the route, but for now this logic prevents spamming of completing a route)
19. Added update review endpoint to allow a user to edit their review. Not adding a delete review endpoint as it may get complicated with peepcoins.
20. Added a user peepcoin endpoint to return a users total peepcoins
21. Fixed formatting to have consistent indenting and SQL query style
22. Made sure a follower is actually following the user before removing them

# API Spec/Schema Feedback

1. Updated schema.sql to match our updated tables in the database
2. Made foreign key reference for user_id in followers, routes, and the ledgers
3. Made naming conventions consistent (such as usernames, followers, etc.)
4. Updated the API Spec to match our current endpoints
5. Fixed redundancy in the reviews table with users
6. Not splitting routes table, would just create unnecessary redundancy and harm readability
7. We removed the /routes/report endpoint entirely because it didn’t add much value to user functionality, and creating logic to process reports and block users is a tedious process that doesn’t need to be added.
8. For get_popular_routes, we now return routes that have at least 10 reviews and an average rating >= 4. In the API spec, we got rid of the popularity index and number of five star reviews to determine if a route was popular. Then we return top 10 popular routes in that endpoint and sort in decreasing order by average rating.
9. Fixed update_followers - we made primary key be the user_id, so we just have user id and follower id. We also added usernames to the table for our own sanity so we know which id is associated with which name.
10. Endpoints that return lists of JSONs (/routes/popular and /routes/followers) are not formatted correctly in APISpec; we fixed the APISpec to return a correctly formatted version.
11. Updated the API Spec to just return “OK” if a transaction went through, and included a comment specifying that a string will be returned if the transaction didn’t go through.
