# Test Credentials

## Google Auth (Emergent-managed)
This app uses Emergent Google OAuth for authentication.
- No manual test credentials needed for login
- Sign in with any Google account via the "Sign in with Google" button
- First-time users are automatically registered

## Test User for API Testing
For backend/curl testing purposes:
- Email: test.user.1787145713914@example.com
- User ID: test-user-1787145713914
- Session Token: test_session_1787145713914
- Expires: 7 days from creation

## Usage
```bash
# Test auth endpoint
curl -X GET "https://demat-dashboard-1.preview.emergentagent.com/api/auth/me" \
  -H "Authorization: Bearer test_session_1787145713914"
```
