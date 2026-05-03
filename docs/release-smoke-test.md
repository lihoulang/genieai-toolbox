# Release Smoke Test

Updated: 2026-05-02

Use this checklist on a release build before Google Play submission.

## Environment Checks

- Verify the build is a release build, not a local debug build
- Verify the app points to the production backend
- Verify the production backend uses valid HTTPS in the final submission build
- Verify the app opens public support, privacy, and account deletion pages correctly

## Account Flow

- Register a new account
- Log in with the new account
- Force-close and reopen the app, then verify the session is still valid
- Log out and verify the app returns to the login page
- Try accessing an authenticated page after logout and verify the app requires login

## Chat Flow

- Create a new conversation
- Send a normal text prompt
- Verify the assistant returns a response
- Reopen the conversation and verify the message history is still present
- Create a second conversation and verify histories do not mix

## Image Understanding Flow

- Upload an image from the gallery
- If supported on the device, test camera capture as well
- Ask the app to describe the image
- Verify the result returns successfully
- Verify the image appears in conversation history

## AI Drawing Flow

- Send a safe image-generation prompt
- Verify an image is returned
- Verify balance is deducted correctly
- If generation fails, verify balance refund behavior is acceptable

## AI Video Flow

- Send a safe video-generation prompt
- Verify a video result is returned
- Verify the result can be opened or downloaded
- Verify reviewer-visible copy or support materials explain that current output is silent
- Verify balance is deducted correctly
- If generation fails or times out, verify refund behavior is acceptable

## AI Report Flow

- Long press an AI response
- Tap `Report`
- Submit one report reason
- Verify the success message appears

## Privacy and Account Deletion

- Open the Profile tab
- Open the support link
- Open the privacy policy link
- Open the account deletion link
- Trigger account deletion with a test account
- Verify the account is deleted and cannot log in again

## Error Handling

- Try a request with insufficient balance and verify the app shows a clear message
- Try a request after token expiry or invalidation and verify the app redirects to login
- Verify the app does not get stuck in a broken loading state after a failed request

## Review Readiness

- Reviewer account is prepared and reusable
- Reviewer account has enough balance for all required steps
- Store screenshots match current shipped features
- AI video is described as a silent clip wherever relevant
- Public URLs in Play Console exactly match the URLs used in the app

## Sign-Off

- Smoke test completed by: `<name>`
- Build tested: `<versionName/versionCode>`
- Test date: `<YYYY-MM-DD>`
- Result: `Pass / Fail`
- Blocking issues:
  - `<fill if any>`

