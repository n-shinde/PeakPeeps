**1. Cal Poly Student Example Flow**

Steve is a 3rd year Cal Poly physics major in desperate need of getting out of the lab. He heard from his friend Dave about this new app Peak Peeps that allows them to connect and see each other's favorite outdoor routes. When he first downloads the app, he calls /socials/add on the username Biker_Dave, his friend Dave’s account. 

While Steve waits for Dave to accept his request, he already knows of his favorite secret biking route that he wants to add to the site, especially to share with Dave and his other biker friends. He calls /routes/add and passes in the parameters: name, location, coordinates, length_in_miles, difficulty, and activities. 

The next day, Steve is bored and wants to go for a hike that he’s never tried before. Since he is still lacking many friends on the app, he decides to check out the popular routes with /routes/popular and decides to only filter by activities as he’s looking for a hike. He finds one he likes and heads out for the adventure of the day. Afterwards, he marks that he logged this hike, causing the app to call /peepcoins/add to add a balance to his account. 

A couple months later, Steve’s activity on the app has skyrocketed. Since he’s attending school in the area, he’s able to log many hours accomplishing trails nearby. As a result, his stock of Peep Coins has also skyrocketed, enough to purchase a coupon. Conveniently, there is currently a coupon to Old SLO BBQ co available, his favorite BBQ restaurant. He quickly calls /peepcoins/purchase/coupon to trade his Peep Coins in for the coupon, and he’s set for dinner tonight.


**2. SLO Visitor Example Flow**

Victor, a busy software engineer at Apple, during one long weekend decides to come to SLO because he has heard of many cool sites to see from his co-workers. After a 3 hour drive, he finally arrives in SLO, but doesn’t know which sites to see and try first. He then remembered an app called Peak Peeps, which helps find sites/routes to try that one of his-coworkers mentioned. So, he downloaded Peak Peeps from the App Store. First, Victor requests to view popular routes to see which are the best routes to try by calling GET /routes/popular. Victor sees that there are 3 routes with a high “popularity_index” and 9 “five_star_reviews”.

A couple minutes later, he decided to go with one of the 3 routes that was close to his hotel as described by the “location” attribute.

After he completed the route, he was amazed by the scenery and wanted to leave a review. So, he called POST /reviews/new and entered his username/name and the “rating” for that route.

**3. GateKeeper**

Zac, a born-and-raised local in San Luis Obispo (SLO), recently discovered that his favorite retreat, Ebb Tide Beach, had become overcrowded with the general public. Frustrated by the loss of his peaceful haven, Zac embarked on a quest to find a solution. His search led him to "Peak Peeps," an app designed to help users maintain the secrecy of their favorite spots while sharing them exclusively with close friends.

Now, Zac enjoys the company of his inner circle, including Robin, Julia, Nidhi, and Josh, as they explore the scenic trails he has revealed to them. Zac calls the insert a route with params as the name, location, coordinates, the length_in_miles, difficulty, and activities. With each shared route, Zac earns PeepCoins, a virtual currency that can be redeemed at local businesses. As he continues uncovering hidden gems in the Central Coast, Zac not only preserves the sanctity of his cherished spots but also supports the community through his PeepCoin ventures. Zac calls the buy a coupon with the amount of coins he has and the sku of the coupon that he wants to redeem. As Zac cashes out his coins, he then views his inner friends routes to also get an idea of where to hike next to get some more PeepCoins. He uses, his friends id, the location, and the difficult level to see what to hike next.

