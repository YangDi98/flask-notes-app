## Feature Name

### 1. What it does
- Make all error responses use a consistent, predictable JSON structure.
- Use a standard custom error message instead of default msg from flask-jwt-extend

### 2. Why I implemented it this way
- Front end will know what to expect and handle error properly.
- API docs will be consistent.
- Use standard custom error message instead of raw message from extensions because
  - The default raw error messages are inconsistent.
  - They are too technical.
  - They might leak important internal information that users should not know. 

- Do both of:
  - using jwt callbacks like @jwt.unauthorized_loader to handle jwt-related errors before they reach flask level
  - using @app.errorhandler to handle errors raise by flask eg. abort(401)
  - Having a catch all handler for 500 errors. 

### 3. Trade-offs / Limitations

### 4. Future Improvements / Scaling Considerations

### 5. Related Security / Best Practices
| Field       | Type           | Description                                                             |
| ----------- | -------------- | ----------------------------------------------------------------------- |
| **status**  | int            | The HTTP status code (e.g., 400, 401, etc.)                             |
| **error**   | string         | Short, human-readable label (e.g., “Bad Request”, “Unauthorized”)       |
| **message** | string         | A clear message describing what went wrong                              |
| **details** | object or null | Optional field for extra info (validation errors, missing fields, etc.) |

