import httpx
from datetime import datetime, timedelta
import asyncio
from io import BytesIO
import json
from typing import Dict

# SIGNUP_URL = "https://dropdash-server.onrender.com/signup"
# LOGIN_URL = "https://dropdash-server.onrender.com/login"
# REFRESH_URL = "https://dropdash-server.onrender.com/token/refresh"
# USER_DATA_URL = "https://dropdash-server.onrender.com/users/me/"
# LOGOUT_URL = "https://dropdash-server.onrender.com/logout"
# GET_AIRDROP_URL = "https://dropdash-server.onrender.com/get_airdrop"
# POST_AIRDROP_URL = "https://dropdash-server.onrender.com/post_airdrop"
# ENCRYPT_URL = "https://dropdash-server.onrender.com/encrypt"
# DECRYPT_URL = "https://dropdash-server.onrender.com/decrypt"


SIGNUP_URL = "http://localhost:8000/signup"
LOGIN_URL = "http://localhost:8000/login"
REFRESH_URL = "http://localhost:8000/token/refresh"
USER_DATA_URL = "http://localhost:8000/users/me/"
USER_TRACKED_AIRDROP_COUNT_URL = "http://localhost:8000/tracked_airdrops/count"
USER_TRACKED_AIRDROP_URL = "http://localhost:8000/tracked_airdrops"
REFERRAL_DATA_URL = "http://localhost:8000/users/me/referrals"
LOGOUT_URL = "http://localhost:8000/logout"
GET_AIRDROPS_URL = "http://localhost:8000/airdrops"
POST_AIRDROP_URL = "http://localhost:8000/post_airdrop"
TRACK_AIRDROP_URL = "http://localhost:8000/track_airdrop"
ENCRYPT_URL = "http://localhost:8000/encrypt"
DECRYPT_URL = "http://localhost:8000/decrypt"
HOME_PAGE_AIRDROPS_URL = "http://localhost:8000/homepage_airdrops"
BASE_URL = 'http://localhost:8000'



tokens = {
    "access_token": None,
    "refresh_token": None,
    "token_expiry": None  # Stored as ISO formatted string
}


# TOKEN_KEYS = {
#     "access": "dapptrack.access_token",
#     "refresh": "dapptrack.refresh_token",
#     "access_expiry": "dapptrack.access_expiry"
# }


# # Token management functions
# async def store_tokens(access_token, refresh_token, token_expiry):

#     async with httpx.AsyncClient() as client:
#         try:
#             payload = {
#                 "access_token": access_token
#             }

#             if refresh_token:
#                 payload["refresh_token"] = refresh_token

#             response = await client.post(ENCRYPT_URL, json=payload)

#             if response.status_code == 200:
#                 result = response.json()
#                 if 'error' in result:
#                     return result['error']
#                 else:
#                     print('Token store success')
#             else:
#                 return f" {response.json().get('detail', 'Unknown error')}"
#         except httpx.HTTPStatusError as e:
#             return f"HTTP error occurred: {e}"

#     """ store tokens """
#     tokens["access_token"] = result.get('access_token')
#     tokens["refresh_token"] = result.get('refresh_token')
#     tokens["token_expiry"] = token_expiry.isoformat()
#     # print(f"The tkns {tokens}")

# Token management functions
async def store_tokens(access_token, refresh_token, token_expiry):

    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "access_token": access_token
            }

            if refresh_token:
                payload["refresh_token"] = refresh_token

            response = await client.post(ENCRYPT_URL, json=payload)

            if response.status_code == 200:
                result = response.json()
                if 'error' in result:
                    return result['error']
                else:
                    print('Token store success')
            else:
                return f" {response.json().get('detail', 'Unknown error')}"
        except httpx.HTTPStatusError as e:
            return f"HTTP error occurred: {e}"

    """ store tokens """
    # page.client_storage.set(TOKEN_KEYS["access"], result.get('access_token'))
    # page.client_storage.set(TOKEN_KEYS["refresh"], result.get('refresh_token'))
    # page.client_storage.set(TOKEN_KEYS["access_expiry"], token_expiry.isoformat())
    tokens["access_token"] = result.get('access_token')
    tokens["refresh_token"] = result.get('refresh_token')
    tokens["token_expiry"] = token_expiry.isoformat()
    
    # print(
    #     f'{tokens["access_token"]}'
    # )
    # print(f"The tkns {tokens}")



async def get_tokens():
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "access_token": tokens.get("access_token")
            }

            refresh_token = tokens.get("refresh_token")

            if refresh_token:
                payload["refresh_token"] = refresh_token

            response = await client.post(DECRYPT_URL, json=payload)
            

            if response.status_code == 200:
                result = response.json()
                if "error" in result:
                    return result["error"]
                    print(f"get tokens func error {result}")
                else:
                    print("decrypt done")
            else:
                print(
                    f" The get_token func response: {response.json().get('detail', 'Unknown error')}")
                return f" {response.json().get('detail', 'Unknown error')}"
        except httpx.HTTPStatusError as e:
            return f"HTTP error occurred: {e}"

    """ return the access token, refresh token, and token expiry"""
    try:
        decrypted_access_token = result.get("access_token")
        decrypted_refresh_token = result.get("refresh_token")
        token_expiry = datetime.fromisoformat(tokens.get("token_expiry"))
        return {
            "access_token": decrypted_access_token,
            "refresh_token": decrypted_refresh_token,
            "token_expiry": token_expiry
        }
    except Exception as e:
        print(f"Error retrieving tokens: {str(e)}")
        return None


# async def get_tokens():
#     decrypted_access_token = tokens.get("access_token")
#     decrypted_refresh_token = tokens.get("refresh_token")
#     token_expiry = tokens.get("token_expiry")

#     # If access token exists and has not expired, return it
#     if decrypted_access_token and token_expiry:
#         try:
#             expiry = datetime.fromisoformat(token_expiry)
#             if expiry > datetime.utcnow():
#                 return {
#                     "access_token": decrypted_access_token,
#                     "refresh_token": decrypted_refresh_token,
#                     "token_expiry": expiry
#                 }
#         except Exception as e:
#             print(f"Token expiry error: {str(e)}")

#     # Otherwise, decrypt new tokens from backend
#     async with httpx.AsyncClient() as client:
#         try:
#             payload = {
#                 "access_token": decrypted_access_token
#             }

#             if decrypted_refresh_token:
#                 payload["refresh_token"] = decrypted_refresh_token

#             response = await client.post(DECRYPT_URL, json=payload)

#             if response.status_code == 200:
#                 result = response.json()

#                 if "error" in result:
#                     print(f"Decryption error: {result['error']}")
#                     return None

#                 print("Token decryption successful.")

#                 # Store decrypted tokens
#                 tokens["access_token"] = result.get("access_token")
#                 tokens["refresh_token"] = result.get("refresh_token")

#                 # Convert expiry to datetime if needed
#                 expiry = datetime.fromisoformat(tokens["token_expiry"])

#                 return {
#                     "access_token": tokens["access_token"],
#                     "refresh_token": tokens["refresh_token"],
#                     "token_expiry": expiry
#                 }

#             else:
#                 print(f"Decryption failed: {response.text}")
#                 return None

#         except Exception as e:
#             print(f"Exception during token decryption: {str(e)}")
#             return None


################# USER AUTHENTICATION AND LOGIN #####################################

async def signup_user(username, full_name, email, referral_code, password, confirm_password):
    if password != confirm_password:
        return "Passwords do not match!"

    data = {
        "full_name": full_name,
        "username": username,
        "email": email,
        "referral_code": referral_code,
        "password": password,
        "confirm_password": confirm_password
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(SIGNUP_URL, data=data)
            print('User Data:', data)
            print(f"Response status code: {response.status_code}")
            server_response = response.json()
            print(f"Response content: {server_response}")

            response.raise_for_status()
            if response.status_code == 200:
                result = response.json()
                if 'error' in result:
                    return result['error']
                else:
                    return "Signup successful!, Please Login"

            else:
                return f"Signup failed: {response.json().get('detail', 'Unknown error')}"
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors here
            try:
                error_message = e.response.json().get('detail', str(e))
            except (ValueError, AttributeError):
                error_message = str(e)  # Fall back to generic error message
            return error_message
        except Exception as e:
            # Catch other errors
            return str(e)


#  <coroutine object signup_user at 0x7f6788265940> ioefheifhoesd


async def login_user(username, password, remember_me):
    """
    Attempts to log the user in and set tokens.

    :param username: Username for login
    :param password: Password for login
    :param remember_me: Boolean, if true, keep the user logged in longer 
    :return: Dictionary with access_token, token_expiry, or an error message 
    """
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "username": username,
                "password": password,
                "remember_me": remember_me
            }

            response = await client.post(
                LOGIN_URL,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            print('Client Side Response:', response.status_code)

            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                refresh_token = response.cookies.get("refresh_token")

                if not access_token:
                    return {"error": "Login failed. No tokens returned from the server."}

                token_expiry = datetime.now() + (timedelta(days=7)
                                                 if remember_me else timedelta(minutes=30))
                
                # page.client_storage.set(TOKEN_KEYS["access"], data["access_token"])
                # page.client_storage.set(TOKEN_KEYS["refresh"], data["refresh_token"])
                # page.client_storage.set(TOKEN_KEYS["access_expiry"], str(expiry_time))

                # await store_tokens(access_token, refresh_token, token_expiry)
                await store_tokens(access_token, refresh_token, token_expiry)

                return "Login successful!"

            elif response.status_code == 401:
                return "Invalid username or password."
            else:
                return {"error": f"Login failed with status code {response.status_code}."}

        except httpx.RequestError as e:
            return {"error": f"Error: {str(e)}"}


async def logout_user():
    try:
        async with httpx.AsyncClient() as client:
            tokens = await get_tokens()
            if tokens is None:
                return 'Error retrieving tokens'
            access_token = tokens.get('access_token')
            refresh_token = tokens.get('refresh_token')

            response = await client.post(LOGOUT_URL, headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            })

            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")

            response.raise_for_status()

            if response.status_code == 200:
                return "Logout successful"
            else:
                return f"Logout failed: {response.json().get('detail', 'Unknown error')}"

    except httpx.HTTPStatusError as e:
        return f"HTTP error occurred: {e}"
    except httpx.RequestError as e:
        return f"Request error occurred: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


async def refresh_access_token():
    """
    Refreshes the access token using the refresh token.
    """
    tokens_data = await get_tokens()
    if tokens_data is None:
        return {"error": "No tokens available for refreshing."}

    refresh_token = tokens_data["refresh_token"]
    if not refresh_token:
        return {"error": "No refresh token available."}

    try:
        response = httpx.post(
            REFRESH_URL,
            cookies={"refresh_token": refresh_token}
        )

        if response.status_code == 200:
            data = response.json()
            new_access_token = data.get("access_token")

            if not new_access_token:
                return {"error": "Failed to refresh access token. No access token returned."}

            # Update token expiry
            new_token_expiry = datetime.now() + timedelta(minutes=30)

            # Encrypt and store new access token
            tokens["access_token"] = encrypt_token(new_access_token)
            tokens["token_expiry"] = new_token_expiry.isoformat()

            return {
                "message": "Access token refreshed!"
            }

        elif response.status_code == 401:
            # The refresh token has expired or is invalid
            return {"error": "Session expired. Please log in again."}

        else:
            return {"error": f"Failed to refresh access token with status code {response.status_code}."}

    except httpx.RequestError as e:
        return {"error": f"Error refreshing token: {str(e)}"}


def is_token_expired(token_expiry):
    """
    Checks if the access token is expired.
    """
    return datetime.now() >= token_expiry


async def get_authorization_headers():
    tokens_data = await get_tokens()
    if tokens_data is None:
        return {"error": "No tokens available. Please log in."}

    access_token = tokens_data.get("access_token")
    token_expiry = tokens_data.get("token_expiry")

    # Check if access token is expired
    if not access_token or is_token_expired(token_expiry):
        # attempt to refresh the access token
        refresh_result = await refresh_access_token()
        if "error" in refresh_result:
            return refresh_result
        else:
            # Retrieve updated tokens
            tokens_data = await get_tokens()
            access_token = tokens_data.get("access_token")

    return {
        "Authorization": f"Bearer {access_token}",
        # "Content-Type": "application/json"
    }

############### USER DATA ####################

async def get_user_data():
    """
    Fetches protected data using the access token asynchronously.
    """
    headers = await get_authorization_headers()
    if "error" in headers:
        return {"error": headers["error"]}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(USER_DATA_URL, headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            return {"error": "Unauthorized. Access token is invalid or expired."}
        else:
            return {"error": f"Failed to fetch protected data, status code: {response.status_code}"}

    except httpx.RequestError as e:
        return {"error": f"Error fetching data: {str(e)}"}


async def get_referrals():
    headers = await get_authorization_headers()
    if "error" in headers:
        return {"error": headers["error"]}

    async with httpx.AsyncClient() as client:
        response = await client.get(REFERRAL_DATA_URL, headers=headers)

    if response.status_code == 200:
        return response.json()  # List of referred users
    else:
        print("Failed to fetch referrals:", response.status_code, response.text)
        return None


################### Airdrop Data ########################



def normalize_filters(filters: dict) -> dict:
    lowercase_fields = {"chain", "status", "category", "name", "sort_by", "order"}
    
    return {
        k: v.lower() if k in lowercase_fields and isinstance(v, str) else v
        for k, v in filters.items()
    }


async def post_airdrop(image_data, form_data):
    airdrop_name = form_data['name']
    headers = await get_authorization_headers()
    if "error" in headers:
        return {"error": headers["error"]}

    # Form data should be JSON stringified
    airdrop_json = json.dumps(form_data)

    files = {
        "image": (f"{airdrop_name}.jpg", image_data, "image/jpeg"),
    }

    data = {
        "form_data": airdrop_json
    }

    print(f"Posting to backend: {airdrop_json}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                POST_AIRDROP_URL,
                headers=headers,
                data=data,
                files=files
            )

            print(f"Status: {response.status_code}")
            print(f"Response content: {response.text}")

            response.raise_for_status()

            return response.json()
        except httpx.RequestError as e:
            print("Request Error:", e)
            return {"error": str(e)}
        except Exception as e:
            print("General Error:", e)
            return {"error": str(e)}




async def get_airdrops(filters: dict = None):
    """
    Retrieve airdrops from the backend with optional filtering.
    
    :param filters: A dictionary of query parameters, e.g.,
                    {
                      "chain": "Sui",
                      "status": "Active",
                      "name": "Test",
                      "sort_by": "airdrop_start_date",
                      "order": "asc",
                      "limit": 10,
                      "offset": 0
                    }
    :return: JSON response from the backend containing the list of airdrops or error info.
    """
    headers = await get_authorization_headers()
    if "error" in headers:
        return {"error": headers["error"]}
    
    # Normalize filters if provided
    params = normalize_filters(filters) if filters else {}
    print(f'Formatted params: {params}')
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                GET_AIRDROPS_URL,
                headers=headers,
                params=params  
            )
            print(f"Status: {response.status_code}")
            
            response.raise_for_status()
            airdrop_data = response.json()

            # Prepend base URL to image_url for each airdrop in the list
            for airdrop in airdrop_data.get("data", []):  # Adjust according to the structure of the response
                if "image_url" in airdrop:
                    airdrop["full_image_url"] = BASE_URL + airdrop["image_url"]
            
            return airdrop_data

        except httpx.RequestError as e:
            print("Request Error:", e)
            return {"error": str(e)}
        except Exception as e:
            print("General Error:", e)
            return {"error": str(e)}


async def get_airdrop_by_id(airdrop_id: int):
    headers = await get_authorization_headers()
    if "error" in headers:
        return {"error": headers["error"]}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
               f"{BASE_URL}/airdrops/{airdrop_id}",
               headers=headers
            )
            response.raise_for_status()  
            airdrop = response.json()
            if 'image_url' in airdrop:
                        airdrop['full_image_url'] = BASE_URL + airdrop['image_url']
            return airdrop
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}")
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
        return None


async def get_homepage_airdrops():
    headers = await get_authorization_headers()

    params = {
        "limit": 5,
        "offset": 0
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                HOME_PAGE_AIRDROPS_URL,
                headers=headers,
                params=params
            )

            response.raise_for_status()
            homepage_data = response.json()

            trending = homepage_data.get("trending", [])
            testnet = homepage_data.get("testnet", [])
            mining = homepage_data.get("mining", [])
            upcoming = homepage_data.get("upcoming", [])

            # Prepend base URL to image_url for each airdrop in the categories
            for category in [trending, testnet, mining, upcoming]:
                for airdrop in category:
                    # Add the full image URL for each airdrop if image_url exists
                    if 'image_url' in airdrop:
                        airdrop['full_image_url'] = BASE_URL + airdrop['image_url']

            # Accessing the full image URLs
            print("\nFull Image URLs:")
            for category_name, category in [("Trending", trending), ("Testnet", testnet), 
                                           ("Mining", mining), ("Upcoming", upcoming)]:
                print(f"\n{category_name} Airdrops:")
                for airdrop in category:
                    full_image_url = airdrop.get('full_image_url')
                    if full_image_url:
                        print(f"- {airdrop.get('name')}: {full_image_url}")
                    else:
                        print(f"- {airdrop.get('name')}: No image URL available")

            return homepage_data

        except httpx.RequestError as e:
            print(f"Request error: {e}")

        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

async def track_airdrop_by_id(airdrop_id):
    headers = await get_authorization_headers()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                TRACK_AIRDROP_URL,
                headers=headers,
                json={"airdrop_id": airdrop_id}  
            )

            print(f"Status: {response.status_code}")
            print(f"Response content: {response.text}")

            response.raise_for_status()
            return response.json()

        except httpx.RequestError as e:
            print("Request Error:", e)
            return {"error": str(e)}
        except Exception as e:
            print("General Error:", e)
            return {"error": str(e)}


async def get_user_tracked_airdrop():
    headers = await get_authorization_headers()
    if "error" in headers:
        return {"error": headers["error"]}

    async with httpx.AsyncClient() as client:
        response = await client.get(USER_TRACKED_AIRDROP_URL, headers=headers)

    if response.status_code == 200:
        return response.json() 
    else:
        print("Failed to fetch referrals:", response.status_code, response.text)
        return None


async def get_user_tracked_airdrop_count():
    headers = await get_authorization_headers()
    if "error" in headers:
        return {"error": headers["error"]}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(USER_TRACKED_AIRDROP_COUNT_URL, headers=headers)

            if response.status_code == 200:
                return response.json()  # {"total_tracked": count}
            else:
                print("Failed to fetch tracked airdrop count:", response.status_code, response.text)
                return {"error": "Failed to fetch tracked airdrop count"}
        except httpx.RequestError as e:
            print("Request Error:", e)
            return {"error": str(e)}
        except Exception as e:
            print("General Error:", e)
            return {"error": str(e)}
