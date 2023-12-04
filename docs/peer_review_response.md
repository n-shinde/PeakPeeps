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
17. 

# API Spec/Schema Feedback

1. Updated schema.sql to match our updated tables in the database
2. Made foreign key reference for user_id in followers, routes, and the ledgers
3. Made naming conventions consistent (such as usernames, followers, etc.)
4. Updated api spec to match our current endpoints
5. Fixed redundancy in the reviews table with users
6. 
