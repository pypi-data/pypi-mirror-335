import logging
import os
import jwt
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jwt import ExpiredSignatureError, InvalidIssuedAtError, InvalidKeyError, PyJWTError

from zmp_manual_backend.models.auth import TokenData
from zmp_manual_backend.models.exceptions import AuthenticationException, ErrorCode

logger = logging.getLogger("appLogger")

# KeyCloak Configuration (default values for development, override in production)
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080/auth")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "master")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "zmp-manual-backend")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
ALGORITHM = "RS256"
KEYCLOAK_REDIRECT_URI = os.getenv(
    "KEYCLOAK_REDIRECT_URI", "http://localhost:8000/auth/callback"
)

HTTP_CLIENT_SSL_VERIFY = os.getenv("HTTP_CLIENT_SSL_VERIFY", "True").lower() == "true"

# KeyCloak Endpoints
KEYCLOAK_REALM_ROOT_URL = (
    f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect"
)
KEYCLOAK_JWKS_ENDPOINT = f"{KEYCLOAK_REALM_ROOT_URL}/certs"
KEYCLOAK_AUTH_ENDPOINT = f"{KEYCLOAK_REALM_ROOT_URL}/auth"
KEYCLOAK_TOKEN_ENDPOINT = f"{KEYCLOAK_REALM_ROOT_URL}/token"
KEYCLOAK_REFRESH_ENDPOINT = KEYCLOAK_TOKEN_ENDPOINT
KEYCLOAK_USER_ENDPOINT = f"{KEYCLOAK_REALM_ROOT_URL}/userinfo"
KEYCLOAK_END_SESSION_ENDPOINT = f"{KEYCLOAK_REALM_ROOT_URL}/logout"

# This will be initialized when KeyCloak is enabled
PUBLIC_KEY = None
oauth2_scheme = None


def initialize_keycloak():
    """Initialize KeyCloak authentication. Call this when KeyCloak is enabled."""
    global PUBLIC_KEY, oauth2_scheme

    if not all([KEYCLOAK_SERVER_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID]):
        logger.warning(
            "KeyCloak is not fully configured. Using fallback authentication method."
        )
        return False

    try:
        PUBLIC_KEY = get_public_key()

        if not PUBLIC_KEY:
            logger.error("Failed to retrieve KeyCloak public key.")
            return False

        oauth2_scheme = OAuth2AuthorizationCodeBearer(
            authorizationUrl=KEYCLOAK_AUTH_ENDPOINT,
            tokenUrl=KEYCLOAK_TOKEN_ENDPOINT,
            refreshUrl=KEYCLOAK_REFRESH_ENDPOINT,
            scheme_name="oauth2_keycloak",
        )

        logger.info(f"KeyCloak integration initialized for realm: {KEYCLOAK_REALM}")
        return True

    except Exception as e:
        logger.error(f"Error initializing KeyCloak: {str(e)}")
        return False


def get_public_key():
    """Retrieve the public key from KeyCloak."""
    try:
        response = requests.get(
            KEYCLOAK_JWKS_ENDPOINT, verify=HTTP_CLIENT_SSL_VERIFY, timeout=10
        )

        if response.status_code != 200:
            logger.error(f"Failed to retrieve JWKS: Status {response.status_code}")
            return None

        jwks = response.json()

        try:
            return jwt.algorithms.RSAAlgorithm.from_jwk(jwks["keys"][0])
        except InvalidKeyError as ike:
            logger.error(f"InvalidKeyError: {ike}")
            return None

    except Exception as e:
        logger.error(f"Error fetching public key: {str(e)}")
        return None


def verify_token(token: str) -> TokenData:
    """Verify a JWT token from KeyCloak and return the token data."""
    if not PUBLIC_KEY:
        raise AuthenticationException(
            error_code=ErrorCode.AUTHENTICATION_ERROR,
            detail="KeyCloak authentication is not configured",
        )

    try:
        payload = jwt.decode(
            jwt=token,
            key=PUBLIC_KEY,
            algorithms=[ALGORITHM],
            audience=KEYCLOAK_CLIENT_ID,
            options={"verify_aud": False, "verify_iat": False},
            leeway=60,
        )

        if payload is None:
            raise AuthenticationException(
                error_code=ErrorCode.INVALID_TOKEN, detail="JWT decode failed"
            )

        token_data = TokenData(
            username=payload.get("preferred_username"),
            email=payload.get("email"),
            full_name=payload.get("name"),
            roles=payload.get("realm_access", {}).get("roles", []),
            exp=payload.get("exp"),
            preferred_username=payload.get("preferred_username"),
        )
        return token_data

    except ExpiredSignatureError as ese:
        logger.error(f"ExpiredSignatureError: {ese}")
        raise AuthenticationException(
            error_code=ErrorCode.TOKEN_EXPIRED, detail="Token has expired"
        )
    except InvalidIssuedAtError as iiae:
        logger.error(f"InvalidIssuedAtError: {iiae}")
        raise AuthenticationException(
            error_code=ErrorCode.INVALID_TOKEN,
            detail="Token has an invalid issued at time",
        )
    except PyJWTError as jwte:
        logger.error(f"JWTError: {jwte}")
        raise AuthenticationException(
            error_code=ErrorCode.INVALID_TOKEN, detail="Could not validate credentials"
        )


async def get_current_user_from_keycloak(
    token: str = Depends(oauth2_scheme),
) -> TokenData:
    """Get the current user from KeyCloak token."""
    if not oauth2_scheme:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="KeyCloak authentication is not enabled",
        )
    return verify_token(token)
