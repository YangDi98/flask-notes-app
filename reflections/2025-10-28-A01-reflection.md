## Name:
OWASP A01 Reflection

## Details
 - Basically owasp 01 is about:
 User should be given the least permission possible to do their job.
 Every action has to check permissions and never trust client side checks or assumptions. 
 - It is mostly a backend security concern.
 - I already do:
   - "Model access controls should enforce record ownership rather than accepting that the user can create, read, update, or delete any record." I am already doing this. Each user can only access/modify their own resources and not other users'. 
   - "Stateful session identifiers should be invalidated on the server after logout." I think I am already doing this by keeping track of last log out time and compare against token issued time.

 ## Future Considerations:
 - minimizing Cross-Origin Resource Sharing (CORS) usage
 - validate token signature, Attackers can modify jwt tokens such as changing role from user to admin to access more privileged endpoints.Log access control failures, alert admins when appropriate (e.g., repeated failures).
 - Rate limit API