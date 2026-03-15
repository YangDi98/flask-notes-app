### Title
ADR002: Set Up Proxy on CloudFront for API Calls
### Date
2026-03-11

### Status
Proposed

### Context
The front end of the app and the back end have different origins. The front end is served via cloudfront and the backend is hosted on render. Since the refresh token cookies are sent from the backend they are associated with the origin of the backend. The cookies contain the refresh_token (HttpOnly) and the csrf_refresh_token (not HttpOnly). The front end needs to get the csrf_refresh_token and send it in the header of requests. However it cannot get the `csrf_refresh_token` from `document.cookies` in JS because the cookies are associated with the backend origin. 

### Decision
- Set up proxy on cloudfront for API calls to the backend so that the frontend and backend appear under the same domain. Make cookies sameSite strict. 

### Alternatives
- Send csrf token in response body of `POST /auth/refresh`. However this way we will need to store it in the front end in some way, either in cookie, or in local storage, or in memory. 
  - In cookies: this cause one cookie to be associated with front end domain and one cookie to be associated with backend domain.
  - In local storage: Security guidelines discourage sensitive tokens in localStorage and this breaks the double-submit cookie pattern. 
  - In memory: It disappears from the front end on page load, and we cannot refresh token without it. 
- Accept CSRF gap on refresh: Rely on CORS protection: Usually csrf token is not required for refresh token endpoint because it is not state-changing and the response is protected by CORS. Usually it is for protecing state-changing requests like POST, PUT, DELETE etc. So technically we do not need CSRF token for our refresh endpoint and this is the only place we use cookies so we can disable CSRF protection. However this adds extra protection. 

### Consequences
- Will have to set up proxy on cloudfront. 
- **Will have to set up caching rules to make sure no caching happens on api paths.** 


### Future Considerations
- This does not protect our app against XSS. XSS vulnerability applies equally to memory/localStorage/cookies
- Not sure about what impact does this bring if we later adds caching for some reason in the backend. 

### Note
- After attempt to set up reverse proxy on cloud front failed (for some reason the request was not able to reach my backend and returns 503 even though my backend service is fine), I decided to disable using csrf token for now. This is acceptable since we only use the cookies for the refresh token endpoint which is not state alterning and the reponse is protected by CORS. 