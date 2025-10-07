# 🧠 Dev Notes — Critical Thinking Warm-Up

## Feature / Fix Name:
*(e.g., Login route, User registration, Input validation update)*

---

<details>
  <summary>1. What could go wrong?</summary>

- *(Think bugs, bad data, security holes, user confusion, scalability issues)*

</details>

<details>
  <summary>2. Tester attack plan (try to break it)</summary>

- *(As a tester, what weird inputs or scenarios would you try? e.g., missing fields, huge payload, wrong type, malicious script)*

</details>

<details>
  <summary>3. After solving / adding this feature:</summary>

**Why does it work?**  
- *(Brief technical reason — “Password hash checked against stored hash in DB”)*

**What could break this?**  
- *(Dependencies, assumptions, future code changes)*

**What risk could this bring?**  
- *(Security, performance, user trust, maintainability)*

</details>

<details>
  <summary>4. Later / Research</summary>

- *(Things to improve or learn more about for future sprints)*

</details>

---

**Entry:**

<details>
<summary>Authorization</summary>

## Feature / Fix Name:
Adding authorization to the project

---
### 1. What could go wrong?
- Authorization not working and users cannot log in. 
- Users can edit notes that are not theirs. 
### 2. Tester attack plan (try to break it)

- Attempt to update an item with incorrect ID or unauthorized user.

</details>

<details>
<summary>Add Login</summary>

## Feature / Fix Name:
Add Login

---
### 1. What could go wrong?
- If emails are not consistently lowercased everywhere (including registration), users may be unable to log in with the email they registered.
- If the request is missing email or password, it could cause a 500 error if not handled.

### 2. Tester attack plan (try to break it)
- Try log in using email (all cases), correct and incorrect passwords, inactive users, deleted users.

### 3. What risks does this bring
- No rate limiting or lockout mechanism allows attackers to try many passwords.
- If JWTs are not properly invalidated on logout or password change, old tokens may remain valid.
- If JWTs are not securely stored on the client, they can be stolen and reused.
- Users may be unable to log in due to case mismatches or inactive accounts.

</details>

<details>
<summary>Add Register user endpoint</summary>

## Feature / Fix Name:
Add endpoint for register user

---
### 1. What could go wrong?
- Email is not verified and might not be valid
- Race condition: two requests with same email at the same time could bypass uniqueness check
- Email format: email may not be valid if schema validation is weak.
- Brute force registration: No rate limiting or CAPTCHA allows bots to spam registrations.
- Case sensitivity: Emails like Test@Email.com and test@email.com may be treated as different.
- Need to delete the test users without password and make password column non-nullable.

### 2. Tester attack plan (try to break it)
- Test all kinds of names, emails, passwords, duplicate emails (lower, upper case).
- Later have tests to ensure all test cases are covered and sensitive data is not leaked in response.

### 3. What risks does this bring
- Security: brute-force registration, or race conditions to create fake or duplicate accounts,
- Sensitive data exposure: If error handling or schemas are misconfigured, sensitive user data (like password hashes) could be leaked in responses
- Race conditions could result in duplicate accounts and cause data integrity issues. 

</details>

<details>
<summary>Restore deleted Note</summary>

## Feature / Fix Name:
Restore deleted note

---
### 1. What could go wrong?
- We have not verify user identity to access note yet.
- For all accessing notes, we have to make sure the user has access to the note. Not just the user exists, and the note exists, but the note must belong to the user.

### 2. Tester attack plan (try to break it)
- We have to test all cases of user does not exist, user not active, note does not exist, note does not belong to user, for each endpoint.

</details>

<details>
<summary>Add Category For Note</summary>

## Feature:
Adding category for note, nullable, each note can have at most one category

---
### 1. What could go wrong?
- Category can be deleted (soft deleted) and some notes are still linking to the deleted category. 
- We have not verify user identity for access category yet (user authentication later).
- Not sure what performance impact is of filtering notes based on categories.
---
### 2. Tester attack plan (try to break it)
- Test CRUD of categories.
- When deleting a category, its notes should be set to category None.
- When add/update category for note, verify the category exists (undeleted).
- Not sure how effecient of my loop of going through category's notes and remove category is if there is a large number of notes
---
### 4. Later / Research:
- Need to address the above issue about deleting category when implementing CRUD of category. 

</details>

<details>
  <summary>CRUD endpoints for "Note" </summary>



## Feature / Fix Name:

CRUD endpoints for `Note`

---

### 1. What could go wrong?
- Missing or invalid input data could cause server errors or inconsistent database state.
- Deleting an item that is referenced elsewhere could cause integrity issues.
- Large payloads or too many requests could impact performance.
- We have not verify user identity to access note yet. 

---

### 2. Tester attack plan:
- Try creating an item with missing required fields or invalid types.
- Send excessively large JSON payloads.
- Try deleting an item twice in rapid succession.
- Send malformed JSON or non-JSON content.
- Test for SQL injection or other malicious inputs.
---

### 3. After solving:
**Why does it work?**  
- Input schemas validate all required fields and data types.
- Database transactions ensure atomicity.
- Error handling returns proper HTTP status codes and messages.

**What could break this?**  
- Missing or outdated authorization logic on new endpoints.
- Schema changes not reflected in validation rules.
- Database deadlocks or connectivity issues.
- Unhandled exceptions if an edge case is missed.

**What risk could this bring?**  
- Security vulnerabilities if auth checks fail.
- Data corruption if input validation is bypassed.
- Poor user experience due to unclear error messages.
- Scalability problems under heavy load.

---

### 4. Later / Research:
- Implement rate limiting to protect against abuse.
- Add logging and monitoring for CRUD operations.
- Explore optimistic locking or versioning to handle concurrent edits.
- Improve error messages for client clarity.

</detail>