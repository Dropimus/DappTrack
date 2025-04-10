
POST /post_airdrop

Description:
This endpoint is used to create a new airdrop or update an existing airdrop based on the provided `external_airdrop_url`. It handles the file upload for the airdrop's image and processes the provided form data.

Request:
- image: (Required) The image associated with the airdrop (file upload).
- form_data: (Required) JSON string containing the details of the airdrop. Example:
  ```json
  {
    "name": "Airdrop Name",
    "chain": "Ethereum",
    "status": "active",
    "device": "mobile",
    "category": "DeFi",
    "funding": "1000",
    "description": "A detailed description",
    "expected_token_ticker": "ETH",
    "external_airdrop_url": "https://example.com",
    "project_socials": "{\"twitter\": \"https://twitter.com/example\"}",
    "airdrop_start_date": "2025-01-01T00:00:00",
    "airdrop_end_date": "2025-01-30T00:00:00"
  }
  ```

Response:
- If the airdrop already exists (based on `external_airdrop_url`), it updates the record and returns:
  ```json
  {
    "message": "Airdrop updated successfully",
    "id": <airdrop_id>
  }
  ```
- If the airdrop is new, it is created and the following response is returned:
  ```json
  {
    "message": "Airdrop stored successfully",
    "id": <airdrop_id>,
    "image_url": "/static/airdrop_image/<filename>"
  }
  ```
- Error Handling: In case of invalid JSON or any database issues, an error message will be returned.

---

GET /airdrops

Description:
Fetches a list of airdrops with optional filters and sorting.

Query Parameters:
- chain: Optional. Filter airdrops by blockchain chain.
- status: Optional. Filter by airdrop status.
- category: Optional. Filter by airdrop category.
- name: Optional. Search by airdrop name.
- sort_by: Optional. Sort results by `airdrop_start_date` or `created_at`. Default is `airdrop_start_date`.
- order: Optional. Sort order: `asc` or `desc`. Default is `asc`.
- limit: Optional. Number of results to return (default: 10).
- offset: Optional. Number of records to skip (default: 0).
- rating_gt: Optional. Minimum rating threshold to filter airdrops.

Response:
Returns a list of airdrops matching the provided filters:
```json
{
  "airdrops": [
    {
      "id": <airdrop_id>,
      "name": "Airdrop Name",
      "chain": "Ethereum",
      "status": "active",
      "funding": "1000",
      "category": "DeFi",
      "expected_token_ticker": "ETH",
      "external_airdrop_url": "https://example.com",
      "image_url": "/static/airdrop_image/<filename>",
      "airdrop_start_date": "2025-01-01T00:00:00",
      "airdrop_end_date": "2025-01-30T00:00:00",
      "created_at": "2025-01-01T00:00:00"
    }
  ]
}
```

---

GET /airdrops/{airdrop_id}

Description:
Fetches a specific airdrop by its `airdrop_id`.

Path Parameter:
- airdrop_id: (Required) The ID of the airdrop.

Response:
Returns the details of the specified airdrop:
```json
{
  "id": <airdrop_id>,
  "name": "Airdrop Name",
  "chain": "Ethereum",
  "status": "active",
  "funding": "1000",
  "category": "DeFi",
  "expected_token_ticker": "ETH",
  "external_airdrop_url": "https://example.com",
  "image_url": "/static/airdrop_image/<filename>",
  "airdrop_start_date": "2025-01-01T00:00:00",
  "airdrop_end_date": "2025-01-30T00:00:00",
  "created_at": "2025-01-01T00:00:00"
}
```

---

GET /homepage_airdrops

Description:
Fetches a list of airdrops for the homepage, categorizing them into trending, testnet, mining, and upcoming categories.

Query Parameters:
- limit: Optional. Number of results to return (default: 5).
- offset: Optional. Number of records to skip (default: 0).

Response:
Returns the categorized airdrops:
```json
{
  "trending": [
    {
      "id": <airdrop_id>,
      "name": "Airdrop Name",
      "rating": 50,
      "category": "DeFi",
      "airdrop_start_date": "2025-01-01T00:00:00",
      "image_url": "/static/airdrop_image/<filename>"
    }
  ],
  "testnet": [
    {
      "id": <airdrop_id>,
      "name": "Airdrop Name",
      "category": "Testnets",
      "airdrop_start_date": "2025-01-01T00:00:00",
      "image_url": "/static/airdrop_image/<filename>"
    }
  ],
  "mining": [
    {
      "id": <airdrop_id>,
      "name": "Airdrop Name",
      "category": "Mining",
      "airdrop_start_date": "2025-01-01T00:00:00",
      "image_url": "/static/airdrop_image/<filename>"
    }
  ],
  "upcoming": [
    {
      "id": <airdrop_id>,
      "name": "Airdrop Name",
      "category": "Upcoming",
      "airdrop_start_date": "2025-01-01T00:00:00",
      "image_url": "/static/airdrop_image/<filename>"
    }
  ]
}
```

---

GET /users/me/

Description:
Fetches the current logged-in user's information.

Response:
Returns the user's details:
```json
{
  "id": <user_id>,
  "username": "username",
  "email": "user@example.com",
  "referral_code": "abc123",
  "created_at": "2025-01-01T00:00:00"
}
```

---

GET /users/me/referrals

Description:
Fetches a list of users referred by the current user.

Response:
Returns a list of referred users:
```json
[
  {
    "id": <user_id>,
    "username": "referred_user",
    "email": "referred_user@example.com",
    "created_at": "2025-01-01T00:00:00"
  }
]
```

---

PUT /users/me/edit

Description:
Updates the current user's information.

Request:
- updated_info: A JSON object containing the fields to be updated (e.g., username, email).

Response:
Returns the updated user details:
```json
{
  "id": <user_id>,
  "username": "new_username",
  "email": "new_email@example.com",
  "referral_code": "abc123",
  "created_at": "2025-01-01T00:00:00"
}
```

---

PUT /users/me/password

Description:
Updates the current user's password.

Request:
- password_data: A JSON object containing the new password.

Response:
Returns a confirmation message:
```json
{
  "message": "Password updated successfully"
}
```