# API Specification - Peak Peeps

## 1. User Social Network

### 1.1. Add Friend - `/socials/{friend}/add` (POST)

Makes a request to add another user as a friend.

**Request**:

```json
{
  "username": "string"
}
```

**Returns**:

```json
{
  "success": "boolean"
}
```

### 1.2. Accept Friend Request - `/socials/{friend}/` (PUT)

Accepts or deletes a given friend request based on user's decision.
If accepted, both users can view each other's profiles.

**Request**:

```json
{
  "username": "string",
  "request_status": "boolean"
}
```

**Returns**:

```json
{
  "success": "boolean"
}
```

### 1.3. Friend Request Status - `/socials/{friend}/` (GET)

Returns a message to the user notifying them if a friend request was accepted or denied.

```json
{
  "request_status": "string"
}
```

## 2. Routes

### 2.1. Add Route - `/routes/add` (POST)

Adds a route to the list of routes available to view on the app.

**Request**:

```json
[
  {
    "name": "string",
    "user_id": "string",   # id of user who added the route
    "location": "string",
    "coordinates": [lat, long],
    "length": "float",
    "difficulty": "int",
    "activities": "string",
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

### 2.2. Report Route - `/routes/report` (POST)

Reports a route by flagging it as inappropriate, returns a status confirming the report has been made.

**Request**:

```json
[
  {
    "route_name": "string",
    "date_added": "string",
    "date_reported": "string",
    "report_author": "string",
    "coordinates": [lat, long],
    "description": "string",
  }
]
```

**Returns**:

```json
[
  {
    "report_status": "string",
    "flagged": "boolean"
  }
]
```

### 2.3. View Popular Routes - `/routes/popular` (GET)

Returns a list of popular routes posted on the app.

```json
[
    {
     /* List of routes with the following attributes displayed:

        "name": "string",
        "date_added": "string",
        "user_added": "string",
        "location": "string",
        "coordinates": [lat, long],
        "length_in_miles": "double",
        "difficulty": "string",
        "activities": "string",
        "popularity_index": int,
        "five_star_reviews": int
    }
]
```

### 2.4. View Followers' Routes - `/routes/followers` (GET)

Returns a list of routes a user's follower has visited on the app.

**Request**:

```json
[
  {
    "friend_username": "string"   /* The username of the follower being searched up
  }
]
```

**Returns**:

```json
[
    {
      /* List of routes with the following attributes displayed:

        "name": "string",
        "user_id": "string",
        "location": "string",
        "coordinates": [lat, long],
        "length_in_miles": "double",
        "difficulty": "string",
        "activities": "string",
    }
]
```

### 2.5. Search for Routes - `/routes/search` (GET)

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
      /* List of routes with the following attributes displayed:

        "name": "string",
        "length_miles": "double",
        "location": "string",
        "user": "string",
    }
]
```

## 3. Reviews

### 3.1. Add New Review - `/reviews/add` (POST)

Creates a new review and posts it on the route page.

**Request**:

```json
[
  {
    "author_name": "string"
    "rating": "integer"   /* On a scale of 1 - 5 (ints only)
    "description: "string"
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

## 4. Customer Purchasing

### 4.1. Add PeepCoins - `/peepcoins/add` (PUT)

Adds PeepCoins to user's account balance.

**Request**:

```json
{
  "user_id": "integer",
  "change": "integer"
}
```

**Returns**:

```json
{
  "success": "boolean"
}
```

### 4.2. Buy Coupon with PeepCoins - `/peepcoins/purchase/coupon` (POST)

Executes coupon transaction using available PeepCoins.

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
  "success": "boolean",
  # Returns a string with a message if the transaction didn't go through (lack of money or invalid coupon)
}
```
