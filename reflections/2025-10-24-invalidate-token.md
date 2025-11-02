## Feature Name
Invalidate token after logout

### 1. What it does
Save the last logout time of user so that I can use this to check token register time against this logout time to see if this token can still be used. It also checks if the user still exists and still active. 

### 2. Why I implemented it this way
Problem: Refresh token and access token might be still valid after user has logged out, there is no way to invalidate a token without some database/redis configuration.

Solution (I use the third):
- Maintain a blacklist of tokens in db/redis and check against the blacklist. 
Pros: Logging out in one device will not log out all other devices. 
 Cons: More configuration, needs db storage / redis.
- Use token versioning. Use a column like token_version on User and check against this. 
- Use a column last_logout_out for user and check token register time against this.
 Pros: Less configuration, easier to implement.
 Cons: Logging out from one device will log out all other devices.

### 3. Trade-offs
- This way logging out from one device will log out all other devices. This is probably fine or in some apps we even want this. 
- Database hit on every request to check user and there is no caching mechanism. This might lead to performance issue (if heavy traffic)
- This is not a proper blocklist/blacklist system, tokens are not immediately invalidated when users are disabed. Tokens remain valid until the next API call. 

### 4. Future Improvements / Scaling Considerations
Scalability:
- Can move to keep a blacklist of tokens in db/redis.
- Can add caching. 
- Can look into token versioning in user records to invalidate all tokens at once. 
### Security Practice:
 A(01) Broken Access Control