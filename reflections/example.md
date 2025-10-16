# Feature Reflection Template

## Feature Name
E.g., JWT Authentication

---

### 1. What it does
- Briefly describe the feature and its role in the system.
- Example:
  - Provides secure login for users
  - Protects notes endpoints with user-specific access

---

### 2. Why I implemented it this way
- Explain your reasoning behind the implementation choices.
- Example:
  - Access token + refresh token for balance between UX and security
  - HttpOnly cookie for refresh token to prevent JS access
  - last_logout_at in DB for server-side revocation

---

### 3. Trade-offs / Limitations
- Describe compromises or things that are not ideal.
- Example:
  - Sliding token refresh keeps users logged in if active, but logs out after inactivity
  - Access token in cookie requires CSRF protection
  - Current implementation uses DB for revocation, not Redis (scalability concern)

---

### 4. Future Improvements / Scaling Considerations
- What you would do differently if the project grew or requirements changed.
- Example:
  - Use Redis for token blocklist for faster revocation
  - Add rate limiting to login endpoint
  - Add logging/monitoring for suspicious activity
  - Consider shorter access token lifetime with sliding refresh for higher security

---

### 5. Related Security / Best Practices
- Map this feature to relevant OWASP Top 10 items or other security considerations
- Example:
  - A01: Access Control
  - A07: Authentication & Session Management
  - A05: Misconfiguration (cookie flags)
