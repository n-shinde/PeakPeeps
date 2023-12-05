# API Specification - Peak Peeps

## 1. Users

### 1.1. Create Account - `/users/create_account` (POST)

Creates an account for a user.

**Request**:

```json
{
  "username": "string"
}
```

**Returns**:

```json
{
  "new_id": "int"     # returns id assigned to new user's account
}
```

### 1.2. Get User - `/users/{username}/` (GET)

Retrieves information of user (ID, username, number of followers) given the username.

**Request**:

```json
{
  "username": "string"
}
```

**Returns**:

```json
{
  "id": "int",
  "username": "str",
  "num_followers": "int"
}
```

### 1.3. Get Username - `/users/{user_id}/` (GET)

**Request**:

```json
{
  "user_id": "int"
}
```

**Returns**:

```json
{
  "username": "str"
}
```

### 1.4. Update Followers - `/users/add_follower/` (POST)

Add new follower to user's follower list and update user's follower count.

**Request**:

```json
[
  {
    "user_to_update": "string",    # the user making the request
    "follower_to_add": "string"   # the follower that the user now has in their followers list
  }
]
```

**Returns**:

```json
[
  {
    "success": "boolean"
  }
]
```

### 1.5. Get Friends - `/users/get_friends` (GET)

Returns all of the friends of a certain user. The qualifications of a "friend" means that
both users follow each other. There will be two rows in the follower table to represent this relationship.

**Request**:

```json
{
  "username": "string"
}
```

**Returns**:

```json
[
    {
     /* List of friends with the following attributes displayed:
        "username": "string"
    }
]
```

### 1.6. Remove Followers - `/users/remove_follower` (POST)

Removes follower from user's follower list. 

**Request**:

```json
{
  "user_to_update": "string",
  "follower_to_remove": "string"
}
```

**Returns**:

```json
[
  {
    "success": "boolean"
  }
]
```

## 2. Routes

### 2.1. Search for Routes - `/routes/search` (GET)

Returns a list of routes based on inputted search parameters

**Request**:

```json
/* Optional input search parameters and search order:

class search_sort_options(str, Enum): 
    route_name = "route_name"
    length_miles = "length_miles"
    city = "city"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc" 
```

**Returns**:

```json
[
    {
      "previous": prev_page,
      "next": next_page,
      "results": lst
    }
]
```

### 2.2. Add Route - `/routes/add` (POST)

Adds a route to the list of routes available to view on the app. 
Also rewards the user with 5 peepcoins for every new, unique route added.

**Request**:

```json
[
  {
    "name": "string",
    "username": "string",    # Optional[str] 
    "coordinates": "list[float]",     
    "address": "string"      # Optional[str] 
    "length": "float",
    "city": "string",        # Optional[str] 
    "state": "string"        # Optional[str] 
  }
]
```

**Returns**:

```json
[
  {
    "new_id": "int"    # id of route just added to the table
  }
]
```

### 2.3. Get Popular Routes - `/routes/popular` (GET)

Returns a list of the top 10 popular routes posted on the app.

```json
[
    {
     /* List of routes with the following attributes displayed:

        "name": "string",
        "date_added": "string",
        "location": "string",
        "coordinates": "list[float]",
        "length_in_miles": "double",
        "difficulty": "int"
    }
]
```

### 2.4. Get Followers' Routes - `/routes/followers` (GET)

Returns a list of routes a user's follower has visited on the app.

**Request**:

```json
[
  {
    "friend_username": "string",   /* The username of the follower being searched up
    "username" : "string"
  }
]
```

**Returns**:

```json
[
    {
      /* List of routes with the following attributes displayed:

        "name": "string",
        "address": "string",
        "length_in_miles": "float",
        "coordinates": "list[float]"
    }
]
```

### 2.5. Complete Route - `/routes/complete` (POST)

Logs when a user completes a route, giving them peepcoins. A user can
only complete a route once, to avoid spamming for peepcoins (the logic isn't perfect, but it
will do for our resources). If a user has already completed this route, an error message is returned.

**Request**:

```json
[
  {
    "route_name": "string",
    "username": "string"
  }
]
```

**Returns**:

```json
[
  {
    "success": "boolean"
  }
]
```


## 3. Reviews

### 3.1. Add Review - `/reviews/add` (POST)

Creates a new review and posts it on the route page.
A user can only add one review to each route (to prohibit spamming of reviews for peepcoins).
If a review has already been submitted by the user, an error message is returned.

**Request**:

```json
[
  {
    "username": "string",
    "route_name": "string",
    "description": "string",
    "rating": "int",       # On a scale of 1 - 5 (only ints)
    "difficulty": "int"     # on a scale of 1-5
  }
]
```

**Returns**:

```json
[
    {
      "review_id": "int"    # ID of review that was just entered in the table
    }
]
```

### 3.2. Update Review - `/reviews/update` (POST)

Updates a user's review if they would like to change the information already posted.

**Request**:

```json
[
  {
    "username": "string",
    "route_name": "string",
    "new_description": "Optional[string]",
    "new_rating": "Optional[int]",
    "new_difficulty": "Optional[int]"
  }
]
```

**Returns**:

```json
[
  {
    "success": "boolean"
  }
]
```


## 4. PeepCoins

### 4.1. Add PeepCoins - `/peepcoins/add` (PUT)

Adds PeepCoins to user's account balance.

**Request**:

```json
{
  "username": "string",
  "change": "integer"
}
```

**Returns**:

```json
{
  "success": "boolean"
}
```

### 4.2. Get PeepCoins - `/peepcoins/get` (GET)

Retrieves PeepCoin balance of a user.

**Request**:

```json
{
  "username": "string"
}
```

**Returns**:

```json
{
  "balance": "int"
}
```

## 5. Coupons

### 5.1. Add Coupon - `/coupons/add` (PUT)

Adds a coupon from a business to the coupons table.

**Request**:

```json
{
  "business_id": "int",
  "name": "string",
  "cost": "int"
}
```

**Returns**:

```json
{
  "success": "boolean"
}
```

### 5.2. Edit Coupon - `/coupons/edit` (POST)

Updates information on a coupon for a business.

**Request**:

```json
{
  "business_id": "int",
  "coupon_name": "string",
  "new_coupon_name": "Optional[string]",
  "is_valid": "Optional[string]",
  "price": "Optional[int]"
}
```

**Returns**:

```json
{
  "success": "boolean"
}
```

### 5.3. Get Coupon - `/coupons/get` (GET)

Retrieves a coupon given the business ID and the coupon name.
Returns an error message if the coupon is not found.

**Request**:

```json
{
  "business_id": "int",
  "coupon_name": "string"
}
```

**Returns**:

```json
{
  "coupon_name": "string",
  "id": "int"
}
```

### 5.3. Buy Coupon - `/coupons/purchase` (POST)

Allows user to buy a coupon if the coupon is valid and user has enough PeepCoins to spend.
Returns error messages if these conditions are not met.

**Request**:

```json
{
  "coupon_id": "int",
  "user_id": "int"
}
```

**Returns**:

```json
{
  "success": "boolean"
}
```

## 6. Businesses

### 6.1. Add Business - `/businesses/add` (PUT)

Add a business to the businesses table. 

**Request**:

```json
{
  "name": "str",
  "address": "str"
}
```

**Returns**:

```json
{
  "success": "boolean"
}
```

### 6.2. List Businesses - `/businesses/list` (GET)

Returns a list of all businesses that offer valid coupons.  

**Request**:

```json
{
   "should_have_valid_coupon": bool
}
```

**Returns**:

```json
[
  {
     /* List of businesses with the following attributes displayed:
     "id": "int",
     "name": "string",
     "address": "string
  }
]
```
