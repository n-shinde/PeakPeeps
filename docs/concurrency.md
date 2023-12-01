**Case 1: Lost Updates with Editing Coupons**

Problem:

Robin and Alex are both co-owners for their smash burger truck and they are offering a coupon for half off a burger and shake combo. At nearly the same time, Alex edits the coupon to change the price to be 30 PeepCoins and Robin edits the coupon to be 40 PeepCoins. When these two requests interleave, there’s a chance for the first update that goes through to be lost.

![Diagram:](https://github.com/n-shinde/PeakPeeps/assets/71895570/768cbae5-cce2-46ec-bf94-aa0d56943366)

Solution:

We put a write lock on the code so that the second user can’t update the table at the same time as the first user, and returns an error saying “Could not find a coupon from business {request.business_name} for coupon {request.coupon_name}”.

**Case 2: Read skew**

**Problem:** Josh checks all the coupons for his favorite burger joint, Fried and Loaded. It returns a valid coupon for BOGO loaded tots and a valid coupon for half off a milkshake. While Josh is making up his mind on what to get, the owner of Fried and Loaded invalidates the coupon for BOGO loaded tots. Unfortunately, Josh then goes to buy this coupon. When it errors saying that the coupon is invalid, he’s frustrated at the PeakPeeps App, since he thought it was valid.

![Diagram:](https://github.com/n-shinde/PeakPeeps/assets/114194038/7e1ef596-4dad-4280-8973-abc7ae35ba10)

**solution:** Use versioning for coupon updates instead of modifying the row directly. If a user tries to buy a coupon with an outdated version (within some reasonable limit, like 10 minutes), we use the outdated version of the coupon instead of the most recent version.

**Case 3: Non Repeatable Read**

Problem:

We run the check peep coins balance to compare against the balance of a coupon to ensure the purchaser has sufficient funds to cover the price. Then later we read the price of the coupon again to deduct the coins from the person's account balance. If the business changes the price of the coupon between these two statements, the purchaser could end up with a negative account balance.

![Diagram:](https://github.com/n-shinde/PeakPeeps/assets/104091934/6e3140c2-8c29-4e81-9e93-f018c01e2c4b)

Solution:

We set the isolation level for the purchase_peepcoin endpoint to be read_repeatable, so the second time the price of the coupon is read, it returns the same read as the first time.
