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
  <summary>CRUD endpoints for "Note" </summary>



## Feature / Fix Name:

CRUD endpoints for `Note`

---

### 1. What could go wrong?
- Missing or invalid input data could cause server errors or inconsistent database state.
- Deleting an item that is referenced elsewhere could cause integrity issues.
- Large payloads or too many requests could impact performance.

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