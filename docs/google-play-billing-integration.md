# Google Play Billing Integration

This project now includes a backend subscription verification flow for Google Play recurring memberships.

## What Is Implemented

- Protected client verify endpoint: `POST /billing/google-play/subscription/verify/{user_id}`
- Manual resync endpoint: `POST /billing/google-play/subscription/sync/{user_id}`
- Subscription debug list: `GET /billing/google-play/subscriptions/{user_id}`
- RTDN receiver: `POST /billing/google-play/rtdn`
- Google Play subscription persistence in SQLite
- Membership activation from verified Play subscription expiry time

## Backend Environment

Set these values in `backend/.env`:

```env
GOOGLE_PLAY_PACKAGE_NAME=com.example.app
GOOGLE_PLAY_SERVICE_ACCOUNT_FILE=/absolute/path/to/google-play-service-account.json
GOOGLE_PLAY_SUBSCRIPTION_MAP={"genie.monthly":{"level":1,"label":"Google Play 月度会员"},"genie.yearly":{"level":2,"label":"Google Play 年度会员"}}
GOOGLE_PLAY_RTDN_BEARER_TOKEN=replace-with-long-random-token
```

You can also use `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` instead of the file path.

## Product Mapping

`GOOGLE_PLAY_SUBSCRIPTION_MAP` maps Play products to your local membership levels.

- Key by `productId`
- Or key by `productId:basePlanId` when one subscription has multiple base plans

Example:

```json
{
  "genie.monthly": { "level": 1, "label": "Google Play 月度会员" },
  "genie.yearly": { "level": 2, "label": "Google Play 年度会员" },
  "genie.pro:annual-v2": { "level": 2, "label": "Google Play 年度会员 Pro" }
}
```

## Client Flow

1. Android client launches Google Play Billing subscription purchase.
2. Client receives `purchaseToken` and `productId`.
3. Client calls:

```http
POST /billing/google-play/subscription/verify/{user_id}
Authorization: Bearer <session-token>
Content-Type: application/json

{
  "purchase_token": "...",
  "product_id": "genie.monthly",
  "package_name": "com.example.app"
}
```

4. Backend verifies the purchase with the Google Play Developer API.
5. Backend acknowledges the subscription if needed.
6. Backend updates the user membership expiry from Google Play.

## RTDN Flow

Google Play Real-time Developer Notifications should point to:

`POST /billing/google-play/rtdn`

The current backend expects a Pub/Sub push body and optionally verifies:

`Authorization: Bearer <GOOGLE_PLAY_RTDN_BEARER_TOKEN>`

When an RTDN message includes a known `purchaseToken`, the backend will resync the subscription and update the membership state.

## Frontend Note

The repository now includes a local uni-app UTS plugin at:

`frontend/uni_modules/genie-google-play-billing`

The membership page already uses it to:

- query Google Play subscription product details
- launch the Android purchase flow
- restore active subscriptions

The main UI entry is in:

`frontend/pages/profile/profile.vue`

## Packaging Note

You still need to build an Android app package with HBuilderX or your uni-app Android pipeline, because Google Play Billing only works in a real Android app with:

- your real application ID
- a signed build
- a Google account that can access the Play track
- subscription products created in Play Console

H5 and non-Android environments will show the entry but cannot complete the purchase flow.

## Official References

- Google Play Billing integration:
  https://developer.android.com/google/play/billing/integrate
- Google Play Developer API `subscriptionsv2.get`:
  https://developers.google.com/android-publisher/api-ref/rest/v3/purchases.subscriptionsv2/get
- Google Play Developer API `subscriptions.acknowledge`:
  https://developers.google.com/android-publisher/api-ref/rest/v3/purchases.subscriptions/acknowledge
