## Feature Name

Allow users to update password after login

### 1. What it does

It allows user to update password after login. This is not for forget and reset password.

### 2. Why I implement it this way

This is pretty straightforward. Just allow the user to update password and it does not allow reusing the same password. Password rule is same as before.

### 3. Limitations / Trade offs

- This only check if the user is using current password but does not check again a list of all previous passwords.
- User is not logged out after changing password. Old tokens remain valid.
- No other way of validating user identity. Whoever gets the token can change password.

### 4. Future Considerations

- I can add more security measures like 2 factor authentication in general for important changes like changing password.
- Consider logging user out on other devices after password change.
- Set up notification so that user is notified when password change.
