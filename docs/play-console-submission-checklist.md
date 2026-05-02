# Google Play Submission Checklist

Updated: 2026-05-02

## 1. Release Package

- Confirm final Android package name / `appid`
  Chosen for this project:
  - uni-app `appid`: `__UNI__3617C61`
  - Android package name: `com.genieai.toolbox`
- Prepare release signing key and backup
- Build release `.aab`
- Verify version name and version code
- Verify target API level matches current Play requirement

## 2. App Access

- Test account username
- Test account password
- Any OTP / special steps needed by reviewer
- Notes for reviewer describing the main path:
  - register or login
  - start a new conversation
  - test image upload
  - test AI report
  - find privacy policy
  - find account deletion

## 3. Store Listing

- App name
- Short description
- Full description
- App icon
- Feature graphic
- Phone screenshots
- Tablet screenshots if applicable
- Category
- Contact email
- Support URL
- Privacy policy URL

## 4. Policy Declarations

- Data safety form completed
- Account creation declared
- Account deletion link filled
- Ads declaration completed
- AI-generated or user-generated content risk reviewed
- Content rating questionnaire completed

## 5. URLs That Must Be Public HTTPS Pages

- Privacy policy URL
- Account deletion / support URL
- Optional website / landing page

## 6. Functional Validation

- Login works on release build
- Token expires and logout flow behave correctly
- User cannot read other users' data
- Chat works
- Image upload works
- Balance changes correctly
- AI report works
- Delete account works
- App can recover from backend failure without broken state

## 7. Pre-Submission Blocking Questions

- Is the backend domain already HTTPS with a valid certificate?
- Are public legal documents deployed and matching the in-app text?
- Is the current developer account subject to closed testing before production?
- Are you intentionally shipping AI video in v1.0?
- Do you have a fallback plan if the AI provider is unavailable?

## 8. Current Release Decision

- `AI 视频` is hidden in `v1.0`
- Reviewer guidance, screenshots, feature list, and store description should not present AI video as a launch feature
