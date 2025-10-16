# SECURITY_NOTES.md

## Project Overview
**Project Name:** Notes App  
**Main Features:** JWT auth, refresh tokens, CSRF protection, user-specific notes.  
**Primary Security Concerns:** Access control, authentication, sensitive data protection.

---

## Security Checklist (OWASP Top 10 Mapping)
| Risk | Status | Notes / TODO |
|------|--------|--------------|
| A01: Broken Access Control | X | Ensure each note is only accessible by its owner |
| A02: Cryptographic Failures | ⬜ | Passwords hashed with bcrypt, TLS enabled for prod |
| A03: Injection | ⬜ | Validate/sanitize input, use ORM to avoid SQL injection |
| A04: Insecure Design | ⬜ | Review endpoint logic for unsafe assumptions |
| A05: Security Misconfiguration | ⬜ | Check CORS, headers, cookie flags, error messages |
| A06: Vulnerable Components | ⬜ | Keep dependencies up to date, audit requirements.txt |
| A07: Auth & Session Failures | ⬜ | JWT token expiry, CSRF protection, logout, refresh |
| A08: Software & Data Integrity | ⬜ | Verify code signing if applicable |
| A09: Logging & Monitoring | ⬜ | Log failed logins, invalid tokens; monitor alerts |
| A10: SSRF | ⬜ | Avoid server making uncontrolled requests |

---

## Current Implementation
- JWT access token: 30 min  
- JWT refresh token: 7 days, HttpOnly cookie  
- CSRF token implemented on refresh endpoint  
- Logout sets `last_logout_at`  
- UTC used for timestamps  
- Password reset flow planned with single-use tokens

---

## To-Do / Improvements
- [ ] Add rate limiting on login endpoint (A07)  
- [ ] Ensure all error messages do not reveal stack traces (A05)  
- [ ] Consider Redis for refresh token blocklist (A01/A07)  
- [ ] Add logging for suspicious activity (A09)  
- [ ] Review headers (CSP, HSTS, X-Frame-Options) (A05)  

---

## Notes / Learnings
- Refresh token in cookie avoids frontend manual handling  
- CSRF header required to protect refresh endpoint  
- JWT `iat` timestamps are UTC — must align DB timestamps  
- Logout revokes prior tokens via `last_logout_at`  
- Single-use password reset tokens require storing `jti` or `last_password_reset_at`
