"""
Session management utilities for the backend.
Handles secure cookie-based sessions with itsdangerous.
"""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import Request, Response
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired

from app.config import settings

# Create a signer with the secret key
signer = TimestampSigner(settings.SECRET_KEY)

# Constants for session management
LICENSE_COOKIE_NAME = "splitter_session"


def get_license_hash(key: str) -> str:
    """
    Create a secure hash of the license key.

    Args:
        key: The license key to hash

    Returns:
        The hashed license key
    """
    # Add a salt from settings for additional security
    salt = settings.SECRET_KEY[:16]
    return hashlib.sha256((key + salt).encode()).hexdigest()


async def validate_session(request: Request) -> bool:
    """
    Check if a session is valid.

    Args:
        request: The FastAPI request object

    Returns:
        True if the session is valid, False otherwise
    """
    # Get the signed session cookie
    session_cookie = request.cookies.get(LICENSE_COOKIE_NAME)
    if not session_cookie:
        return False

    try:
        # Unsign the cookie and check if it's expired
        unsigned_value = signer.unsign(
            session_cookie,
            max_age=settings.SESSION_EXPIRY_HOURS * 3600
        )

        # Decode the payload
        session_data = json.loads(unsigned_value.decode())

        # Check expiry (double-check even though TimestampSigner already checks)
        if "expires" in session_data:
            expiry = datetime.fromisoformat(session_data["expires"])
            if datetime.now() > expiry:
                return False

        return True
    except (SignatureExpired, BadSignature, json.JSONDecodeError, ValueError):
        return False


def create_session_cookie(
        license_hash: str,
        response: Response,
        expiry_hours: Optional[int] = None
) -> None:
    """
    Create a signed session cookie with the license hash.

    Args:
        license_hash: The hashed license key
        response: The FastAPI response object to set the cookie on
        expiry_hours: Optional override for session expiry in hours
    """
    if expiry_hours is None:
        expiry_hours = settings.SESSION_EXPIRY_HOURS

    # Create session data with expiry
    expires = (datetime.now() + timedelta(hours=expiry_hours)).isoformat()
    session_data = {
        "hash": license_hash,
        "expires": expires
    }

    # Sign the session data
    signed_value = signer.sign(json.dumps(session_data).encode())

    # Set the cookie
    response.set_cookie(
        key=LICENSE_COOKIE_NAME,
        value=signed_value.decode(),
        httponly=True,
        max_age=expiry_hours * 3600,
        samesite="lax",
        secure=settings.ENV != "development"  # Secure in production
    )


def clear_session_cookie(response: Response) -> None:
    """
    Clear the session cookie.

    Args:
        response: The FastAPI response object
    """
    response.delete_cookie(
        key=LICENSE_COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=settings.ENV != "development"
    )