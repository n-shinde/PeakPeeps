# API Specification - Peak Peeps

## 1. User Social Network

### 1.1. Add Friend - `/socials/{friend}/add` (POST)

Makes a request to add another user as a friend. 

**Request**:

```json
{
  "username": "string",
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
    "date_added": "string",
    "user_added": "string",
    "location": "string",
    "coordinates": [lat, long],
    "length_in_miles": "double",
    "difficulty": "string",
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

### 2.1. Log Route

