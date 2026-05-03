# Play Console App Access

Updated: 2026-05-02

Use this file when filling the Play Console `App access` section and preparing reviewer instructions.

## Access Model

- The app requires sign-in to access core features.
- Reviewers must be provided with a reusable test account.
- The test account should not require SMS, email OTP, invitation approval, or region-specific access.

## Reviewer Credential Template

Fill these values before submission:

- Username: `<reviewer_username>`
- Password: `<reviewer_password>`
- Account state: `Pre-created reusable account with enough balance for chat, image, and video tests`

## Reviewer Instructions

Paste and adapt this in Play Console:

```text
This app requires login.

Reviewer test account
- Username: <reviewer_username>
- Password: <reviewer_password>

How to access key features
1. Open the app and sign in with the test account above.
2. On the main chat page, send a normal text prompt to verify AI chat.
3. Tap the "+" button in chat and upload an image to verify image understanding.
4. Send a prompt requesting image generation to verify AI drawing.
5. Send a prompt requesting a short video to verify AI video generation.
6. Long press an AI response and select "Report" to verify the AI report function.
7. Open the Profile tab to review Support, Privacy Policy, and Account Deletion information.

Important reviewer notes
- The current AI video output is a silent clip and does not include audio.
- Camera and photo permissions are used only for user-initiated image upload.
- If a generation request takes longer than normal, please allow extra time for the response to return.
```

## Minimum Reviewer Balance

Make sure the reviewer account has enough balance before submission:

- Text chat: at least `20`
- AI drawing: at least `20`
- AI video: at least `100`
- Recommended reviewer balance before submission: `200+`

Reason:

- Reviewer paths are not deterministic and they may retry failed generations.

## Suggested Reviewer Prompts

These prompts are simple, safe, and reviewer-friendly:

- Text chat:
  - `Summarize the benefits of daily exercise in 5 bullet points.`
- Image understanding:
  - Upload a normal household or landscape image and ask:
  - `Describe what is shown in this image.`
- AI drawing:
  - `Create an illustration of a lighthouse at sunset in a warm oil painting style.`
- AI video:
  - `Create a short video of clouds moving over a mountain lake at sunrise.`

## Public Links Reviewers May Need

- Website: `https://lihoulang.github.io/genieai-toolbox/index.html`
- Support: `https://lihoulang.github.io/genieai-toolbox/support.html`
- Privacy Policy: `https://lihoulang.github.io/genieai-toolbox/privacy.html`
- Account Deletion: `https://lihoulang.github.io/genieai-toolbox/account-deletion.html`

## Pre-Submission Checks

- Test account login works in the release build
- Test account balance is sufficient
- Public legal pages are accessible without login
- Privacy policy, support, and account deletion URLs in the app match Play Console exactly
- App access instructions are written in English

