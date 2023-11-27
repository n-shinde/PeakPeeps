# Code Review Comments

(From Logan)

1. Accept Friend Request - Return "OK"

2. Should routes url be /routes/{route_id}/add (POST)

3. Coordinates are lat, long data types or should they just be floats and specify lat long

4. I don't think you need list (only need a dictionary) - in reference to parameters in add_coupon, post_add_review

5. In peepcoins.py - This code is a little hard to read. Using the traditional SQL spacing and indenting may help.
   Also mentioned in coupons: This function is really dense and the formatting is hard to follow. Have consistency in writing queries. I've noticed that other queries are in proper SQL format.

6. At the end of buy_coupons: You could combine these two SQL statements. they use the same dictionary, so you could do WITH insert AS ( [THE INSERT INTO STATEMENT] RETURNING id ) [THE SECOND STATEMENT]

7. In reviews.py and routes.py - I think its best to define constants at the top of the file.

8. In add_routes - This follows a very similar structure to the code doing the same thing for review. Could you have a function or something that means you don't have to repeat it?

9. In get_popular_routes - Should do list comprehension to be quicker or route_list = list(popular_routes)

10. In get friends routes - route_list = [item for item in friends]
    return route_list

11. In report route - might not need list

12. In report route - If you are setting these status and success variables just before returning, could you just return those values?

(From Luke) 13. add_peepcoins_query = text() - For readability, I would add this in the connection.execute() parameter to show where it is being used. If it is a global variable, it would look like it is being used somewhere else.
Follow up note: Now I see the usage of the global variable. I'd say there is no harm is rewriting queries just to make it more readable.

14. It looks like when the queries need more variables, you change the format of the json to insert strings. For consistency, I would keep the same format. Whether it needs two or ten variables, I'd keep the same format to make it cleaner

15. Not the biggest fan of separating "query" and then redefining it after each query. It would be easier to read if they were put into the text() and reduce the redundancy.

16. For def report_route(route_to_report: Routes) - This part seems like it is asking for too much. It takes in the 'Routes' object but only uses 'location'.

17. In reviews.py - Could you make the queries more compact in terms of formatting. Very large function just for two queries. Also, I don't see a point to have PEEP_COINS_FROM_POSTING_REVIEW if it will be 5 every call.

18. Fix indenting in users.py and routes.py - Fix the indenting here to make it seem more uniform. Other queries look good.

19. (One of the routes.py queries?) - I'd say that this query is quite large. You can potentially create different tables for organization.

20. If the admin.py file will not be used, you can just delete it.

21. In report routes - Will this output always be "True" and "Reported"? If so, I don't see the use in having those variables.

22. Commit messages like 'done maybe???' and 'try test again' is too vague. not enough info from those commit messages.

(Parshana)
Users.py

Post_create_account -
Include checking for if a user has already been added to not add again.

User_follows_other_user -
Honestly was kinda of confused about update_followers and user_follows_other_users. Like could combine these two.

Remove_follower -
Checking if the user doesn’t exist to return couldn’t remove.
For example, they remove a user but then try to remove them again.

Routes.py

Post_add_route -
Include a check to make sure that coordinates are only a list of size 2 for coordinates.

- Include duplicate checking for routes maybe based on if name, location, and coordinates are similar to something that already exists then it should instead add a count to the route_id that has been visited.
- Instead of having a user input the length in miles would it be cool to have like starting and ending coordinates and then find the distance between the two? Not sure if this is a good idea but the potential to make sure that people are accurately putting in the distance.
- Also mentioning that the coordinates are the start of the route might be good and the location is the city that it is in.
- Get_popular_routes (Not returning the right thing just an array of names of users like ["Steve", "Steve", "Lucas Pierce", "Steve"]) -
- Add a check to make sure this isn’t a reported route. Only display not reported routes.
- Potentially adding the id for each route so that when people are reporting the route they can just provide the route_id.
- What happens if you have like 1,000 popular routes? Maybe adding some sort of filtering mechanism where users can filter by difficulty or by location for example.

Get_followers_routes -

- I kinda understand what is happening but how are you connecting a user to a friend? Might be better to have a connection between the user and the follower. So that you can only see your friends, not just any.
- Include some kind of pagination since what if you have a lot of friends?
- Have an endpoint that returns all my friends so that I can decide which friend/follower I want to look at.

Report_route -
Only putting in the route_id instead of all the info might make it better.

Reviews.py

Post_add_review -

- Check to make sure that a user isn’t writing a review to the same route_id.
- Also, add checks to make sure that the user has even done the route to be able to write a review on it.
- Could potentially have an update instead of an insert in case people want to adjust a review that they made.
- Adding a delete review in case the user wanted to delete this? Not sure if this would include taking away from peep coins.

PeepCoins.py

Put_add_peepcoins - Not sure if this is needed as a user can then just add as many peep coins to their account. Maybe change this to a get method that just returns the user and the current peep coins total.

- Also I myself didn’t know what my user_id was when I was creating users

Post_buy_coupon -

- There is a valid column mentioned here but I didn’t see that in the schema. The follow-up question is how are you determining if a coupon is valid? [Love the error checking btw]
- Your schema calls the coupon column cost but your code calls it price. I would say double-check the schema with your tables in Supabase.

Coupons.py

Add_coupon (can move me to business.py to have one file)

General Improvement Recommendations:

- Adding more error checking to all the endpoints instead of just “OK”. Also giving detailed error messages.
  What happens if a route is reported? Can people still view this route? Do people still get peep coins from this route?
- For the rating integer, you can do something similar to the pagination that we did in the potion shop where it gave a dropdown for the options to sort by but use a rating scale here. Note: I mentioned some places below in the API spec/ schema where I thought a drop-down might be good to have could implement this for those instances as well.
- It was hard to know what to put in for each endpoint as there is only “OK” returned for almost all functions making it hard to figure out my user_id, the routes, the total peep coins, and things like that.
  - For example could have added the same route too many times.
  - Wasn’t sure how to get the route_id information of a route I added to write a review on it.

(Krishnanshu)
~~1. Consider removing admin.py since it’s just an empty file with no functionality.~~

2. Some of the commit messages didn’t have the appropriate information to describe the change. The best practice is to usually have an action-specific message, which some of your commits do have, but then there are others with titles like “try test again” and “done maybe??” which are harder to decipher.

~~3. Within peepcoins.py, there doesn't seem to be a valid reason to define the 'add_peepcoins_query' as a global variable outside the scope of the put_add_peepcoins method. Since the query is only being used once within that method, it should be defined in the same format as all of your other queries.~~

4. ~~In reviews.py, you're currently importing add_peepcoins_query from peepcoins.py within the post_add_review. Since the query text is quite short, there is no performance or memory improvement, so for the sake of comprehensibility, it would be more appropriate to just duplicate it within both files.~~
5. ~~Within users.py, this query: """ SELECT id FROM user_test WHERE username = :name """ is being repeated several times. Instead of duplication here, you can either make a new method that performs this function, example: "get_user_id_from_username" or make that query a global variable.~~

6. The structure and operation of the user_follows_other_user and update_followers methods in users.py seem to be almost identical, there is definitely potential here to refactor the code to avoid the unnecessary duplication.

7. ~~Additionally, in all 3 methods within users.py, within the update statements you perform a query for finding the ID of the user within the where clause. You have already found the id's of both users through the previous Select queries, so you should be passing in one of those id's as a parameter rather than finding it again.~~

8. Within post_add_review in reviews.py, there is no functionality to check whether a submitted review was valid or not. Since the user will receive peep coins for doing this operation, they could simply send unlimited duplicate requests of the same review to get unlimited peep coins.

9. ~~Within several of the files, like coupons.py, I'm not sure why the parameters for queries are being passed in as lists. [{"name": request.name, "address": request.address}], this should be changed to just {"name": request.name, "address": request.address} unless there's a good motivation for keeping them in the list format.~~

10. Within routes.py, for the get_followers_routes method, it might be appropriate to have some form of limit or pagination set in case there's too many routes to return.

11. ~~In peepcoins.py, this if is_valid == "FALSE": should be changed to be a boolean comparison, ex: if is_valid == False:~~

12. Many of the queries in the code could be prone to error faulting and exceptions, and it would be important to add error checking in the future to prevent this.

13. Also, a lot of the endpoints don't take in the proper information or return the necessary info to handle the necessary operation. For example, when creating a user, business, coupon, etc, no id is returned so there's no way to know what id to use while testing since there's also no GET methods in your implementation. Also, in /routes/followers for example, it doesn't take in the user's id, so how could it know whether the friend_username and the user are actually friends in the app or not. Several cases like this through the endpoints.
