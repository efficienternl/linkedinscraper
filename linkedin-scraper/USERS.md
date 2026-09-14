# Streamlit Login System - User Management

This LinkedIn Scraper app now includes a simple authentication system. Users must log in before accessing any scraping features.

## Setup

### 1. Configure Users in `.env`

Create a `.env` file (copy from `.env.example`) and add the `STREAMLIT_USERS` variable:

```bash
STREAMLIT_USERS=admin:password123,user:testpass
```

**Format:** `username1:password1,username2:password2`

- Usernames and passwords are separated by colons `:`
- Multiple user pairs are separated by commas `,`
- Whitespace around usernames/passwords is automatically trimmed

### 2. Start the App

```bash
streamlit run app.py
```

The app will show a login screen first. Enter any configured username and password.

---

## Adding Users

### Quick Add (edit `.env` directly)

```bash
# Add to the STREAMLIT_USERS line:
STREAMLIT_USERS=admin:password123,user:testpass,newuser:newpass
```

Restart the Streamlit app to apply changes.

### Example Configurations

**Single user:**
```
STREAMLIT_USERS=admin:mypassword
```

**Multiple users:**
```
STREAMLIT_USERS=admin:admin123,rens:renspass,team:teampass
```

**With special characters (URL-safe):**
```
STREAMLIT_USERS=admin:MyP@ss123,user:Test_Pass2024
```

---

## Session Management

- **Login:** Credentials are checked against configured users. Success redirects to the main app.
- **Session Persistence:** Login state persists during the Streamlit session (until browser refresh or logout).
- **Logout:** Click the "Logout" button in the sidebar to clear your session and return to the login screen.
- **Invalid Credentials:** An error message appears if username/password don't match.

---

## Security Notes

- **Hardcoded for now:** Credentials are stored in `.env` as plain text. For production, consider:
  - Using a proper database (Supabase, Firebase)
  - Hashing passwords with `bcrypt` or similar
  - Adding role-based access control (RBAC)

- **Never commit `.env`:** Make sure `.env` is in `.gitignore` to avoid exposing credentials.

- **Development only:** This system is suitable for internal/team use. For public-facing apps, implement proper authentication.

---

## Troubleshooting

### "No users configured. Set STREAMLIT_USERS in .env"
- Ensure `.env` exists in the project root
- Verify `STREAMLIT_USERS` is set with at least one username:password pair
- Restart the Streamlit app

### Login button doesn't work
- Check that the username and password match exactly (case-sensitive)
- Verify `.env` is loaded (restart the app)
- Ensure no trailing spaces in the `.env` file

### Can't logout
- The logout button is in the sidebar. Click it to clear your session.
- If stuck, refresh the browser or close/reopen the tab.

---

## Future Improvements

- Add password hashing (bcrypt)
- Implement token-based auth (JWT)
- Add user roles/permissions
- Use a database for user management
- Add "Remember Me" functionality
- Rate limiting for failed login attempts
