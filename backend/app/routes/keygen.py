"""
License validation routes for the Keygen.sh API integration.
"""
import json
import requests
from typing import Dict, Any

from fastapi import APIRouter, Response, Form
from fastapi.responses import JSONResponse

from app.config import settings
from app.utils.sessions import get_license_hash, create_session_cookie, clear_session_cookie

router = APIRouter(prefix="/api", tags=["license"])


@router.post("/validate-license")
async def validate_license(response: Response, license_key: str = Form(...)):
    """
    Validate a license key against the Keygen.sh API and create a session if valid.

    Args:
        response: FastAPI response object for setting cookies
        license_key: The license key to validate

    Returns:
        JSON response indicating success or failure
    """
    # Validate the license with Keygen API
    is_valid = await check_key(license_key)

    if is_valid:
        # Create a session with the valid license
        license_hash = get_license_hash(license_key)
        create_session_cookie(license_hash, response)

        return {"success": True, "message": "License validated successfully"}
    else:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "Invalid license key"}
        )


@router.post("/logout")
async def logout(response: Response):
    """
    Clear the session cookie (logout).

    Args:
        response: FastAPI response object for clearing cookies

    Returns:
        JSON response confirming logout
    """
    clear_session_cookie(response)
    return {"success": True, "message": "Logged out successfully"}


async def check_key(key: str) -> bool:
    """
    Validate a license key against the Keygen.sh API.

    Args:
        key: The license key to validate

    Returns:
        True if the license is valid, False otherwise
    """
    # Check if KEYGEN_ACCOUNT_ID is set
    if not settings.KEYGEN_ACCOUNT_ID:
        print("KEYGEN_ACCOUNT_ID not set, using development mode validation")
        # In development, accept any key that's not empty
        return bool(key and len(key) > 0)

    # Construct API endpoint
    api_endpoint = f"https://api.keygen.sh/v1/accounts/{settings.KEYGEN_ACCOUNT_ID}/licenses/actions/validate-key"

    # Prepare request data
    request_data = json.dumps({
        "meta": {
            "key": key
        }
    })

    # Make the API request
    try:
        response = requests.post(
            api_endpoint,
            headers={
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json"
            },
            data=request_data
        )

        validation = response.json()

        # Check for errors
        if "errors" in validation:
            errs = validation["errors"]
            error_messages = '\n'.join(map(lambda e: f"{e['title']} - {e['detail']}".lower(), errs))
            print(f"License validation failed: {error_messages}")
            return False

        # Return validation result
        valid = validation["meta"]["valid"]
        print(f"License validation result: {valid}")
        return valid

    except Exception as e:
        print(f"Exception during license validation API request: {str(e)}")
        return False