# Play Console Data Safety Draft

Updated: 2026-05-03

This draft is based on the current repository code and public legal pages. It is meant to speed up Play Console entry, not replace your final legal and production review.

## Official References

- Data safety overview: `https://support.google.com/googleplay/android-developer/answer/10787469?hl=en`
- User Data policy: `https://support.google.com/googleplay/android-developer/answer/10144311?hl=en`
- Account deletion requirements: `https://support.google.com/googleplay/android-developer/answer/13327111?hl=en`
- AI-generated content policy: `https://support.google.com/googleplay/android-developer/answer/13985936?hl=en`
- App access login credential requirements: `https://support.google.com/googleplay/android-developer/answer/15748846?hl=en`

## Blocking Checks Before Final Submission

- Production backend has been switched to HTTPS. Verify the release build still points to the same HTTPS endpoint before submission.
- Reconfirm whether each model provider is acting as your `service provider` under Google Play's Data safety definitions. If yes, data sent to those providers is usually declared as `collected` but not `shared`. If not, switch those data types to `shared`.
- Reconfirm that no analytics, ads, crash reporting, or tracking SDKs were added after this draft was written.

## Recommended High-Level Answers

- Does the app collect user data? `Yes`
- Is all user data encrypted in transit? `Yes`
- Does the app provide a deletion request mechanism? `Yes`
- Is a privacy policy required? `Yes`

## Recommended Data Type Mapping

### Personal info > Name

- Recommended answer: `Collected`
- Shared: `No`
- Data is processed ephemerally: `No`
- Required or optional: `Required for username at sign-up/login; nickname is optional`
- Purpose:
  - App functionality
  - Account management

Why:
- The app stores a username and optional nickname in the `users` table.

### Personal info > User IDs

- Recommended answer: `Collected`
- Shared: `No`
- Data is processed ephemerally: `No`
- Required or optional: `Required`
- Purpose:
  - App functionality
  - Account management
  - Fraud prevention, security, and compliance

Why:
- The backend uses internal user IDs and session records to authenticate and scope access.

### Messages > Other in-app messages

- Recommended answer: `Collected`
- Shared: `No`, if model providers are treated as service providers acting on your behalf
- Data is processed ephemerally: `No`
- Required or optional: `Required for chat use`
- Purpose:
  - App functionality
  - Fraud prevention, security, and compliance

Why:
- User chat prompts and assistant responses are stored in message history.
- Chat prompts may also be transmitted to model providers when users request AI processing.

### Photos and videos > Photos

- Recommended answer: `Collected`
- Shared: `No`, if model providers are treated as service providers acting on your behalf
- Data is processed ephemerally: `No`
- Required or optional: `Optional`
- Purpose:
  - App functionality

Why:
- User-uploaded images are stored with message history and may be sent to image-capable model providers to fulfill the user request.

### App activity > Other user-generated content

- Recommended answer: `Collected`
- Shared: `No`
- Data is processed ephemerally: `No`
- Required or optional: `Optional`
- Purpose:
  - App functionality
  - Fraud prevention, security, and compliance

Why:
- The app stores conversation titles and AI report submissions created by the user.

## Recommended Data Types To Leave As Not Collected

Based on the current repository snapshot, these are not evident in code and should remain `No` unless production differs:

- Email address
- Phone number
- Precise location
- Approximate location
- Contacts
- Calendar
- Audio files
- User-provided videos
- Files and documents
- Financial info
- Health and fitness
- Web browsing history
- App performance and crash logs
- Device or other advertising IDs

## Security Practices

- Encryption in transit:
  - Final answer: `Yes`
  - Current basis: production API base URL is configured to use HTTPS

- Deletion request mechanism:
  - Final answer: `Yes`
  - Evidence:
    - In-app delete account flow exists
    - Public account deletion page exists

## Evidence From Current Code

- User accounts and profile fields are stored in `users`
- Chat content and uploaded image data are stored in `messages`
- Balance records are stored in `balance_logs`
- AI report submissions are stored in `ai_reports`
- Account deletion removes user record, messages, balance logs, AI reports, and sessions
- Android permissions currently include network, camera, and photo library image access

## File-Level Evidence

- Backend data tables and auth/session logic: `backend/main.py`
- Public privacy page: `docs/privacy.html`
- Public account deletion page: `docs/account-deletion.html`
- Public support page: `docs/support.html`
- Android permissions and package metadata: `frontend/manifest.json`

## Final Manual Checks In Play Console

- Verify the release build still points to the HTTPS production backend before answering `Encrypted in transit = Yes`
- Verify reviewer account credentials are reusable and provided in English
- Verify public legal page URLs match the exact links used in the app
- Verify the app description and screenshots mention that current AI video output is silent
- Verify no post-build SDKs add new data collection beyond this draft
