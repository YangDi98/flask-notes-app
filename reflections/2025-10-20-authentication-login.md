## Feature Name
JWT Authentication, Login

### 1. What it does
Allow users to login and this generates a jwt access token, and a jwt refresh token for user. The refresh token is stored in cookie. The access token is returned in the response. Access token is set to expire in 30 minutes while refresh token is set to expire in 7 days. In the front end, if a request fails due to access token expired, it will use the refresh token (which is sent in cookies) to get a new access token. 

### 2. Why I implemented it this way
Refresh token creates a way a user can get new access token without entering their credentials again. Also this way the user would not be logged out in the middle of a session since the access token is usually short-lived (30 minutes). There are multiple ways of refreshing tokens including:
- Implicit refreshing: at the end of each request, refresh the token if the access token is nearly expired. There is an example of this on the doc. Basically this way we don't need a refresh token at all and just store and refresh the access token in cookies.
- Explicit refreshing: like the way I am doing it. I choose to store refresh token in cookies(HTTPOnly,frontend cannot access, reduces XSS risk) and access token returned in response (store in local storage in front end). This gives the front end more control about when to refresh token and avoid issues like multiple requests in parallel triggering the token to be refresh multiple times.

### 3. Trade-offs
- Security/Usability trade offs:
  - Access token is short lived, making it less risky for XSS attacks if stored in local storage. Can put it in local storage so that JS can access it, and it is not automatically sent always (like in cookies), offer more flexibility. It is also more risky to CSRF since the token is sent automatically in every request.
  - Refresh token is long lived, storing it in local storage would make it risky for XSS attacks, where the person gets the refresh tokena and can keep refreshing tokens. It is less CSRF because it verifies origin on the cookie and it is usually a POST request to refresh the token.

### 4. Future Improvements / Scaling Considerations


### 5. Related Security / Best Practices
Protect access tokens from attacks (XSS, CSRF, token theft).
  - OWASP A01: Access Control
  - OWASP A07: Authentication & Session Management


