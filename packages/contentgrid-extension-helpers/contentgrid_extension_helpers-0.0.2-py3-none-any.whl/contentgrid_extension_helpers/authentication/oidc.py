import logging
import os
import hyperlink
from typing import Annotated, Optional

from contentgrid_extension_helpers.authentication.user import ContentGridUser
import jwt
import requests
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# Load environment variables
load_dotenv()
load_dotenv(".env.secret")

# Default constants
DEFAULT_ALGORITHM = "RS256"


def _get_jwks_client_from_config_uri(config_uri: str) -> tuple[dict, jwt.PyJWKClient]:
    """
    Common helper function to retrieve JWKS client from a configuration URI.

    Args:
        config_uri: The URI to find the OAuth/OIDC configuration.

    Returns:
        Tuple of OAuth/OIDC configuration and JWKS client.
    """
    try:
        config = requests.get(config_uri).json()
        return config, jwt.PyJWKClient(config["jwks_uri"])
    except (requests.RequestException, KeyError) as e:
        logging.exception(f"Error retrieving configuration: {e}")
        raise

def get_oidc_jwks_client(
    oidc_issuer: str,
) -> tuple[dict, jwt.PyJWKClient]:
    """
    Retrieves the JWKS (JSON Web Key Set) client from the OIDC (OpenID Connect) issuer configuration URI.
    
    Args:
        oidc_issuer (str): The OIDC issuer URL. The issuer URL is used to retrieve the JWKS URI.
                            The url is adjusted to point to the .well-known/openid-configuration path, based on the OpenID Connect specification.
                            If not on the default endpoint, use function _get_jwks_client_from_config_uri instead.
    
    Returns:
        Tuple[dict, jwt.PyJWKClient]: A tuple containing the OIDC configuration and the JWKS client.
    """
    oidc_issuer_url: hyperlink.URL = hyperlink.parse(oidc_issuer)
    assert oidc_issuer_url.absolute

    oidc_config_uri = oidc_issuer_url.replace(
        path=oidc_issuer_url.path + (".well-known", "openid-configuration") 
    ).to_iri().to_text()

    return _get_jwks_client_from_config_uri(oidc_config_uri)

def get_oauth_jwks_client(
    oauth_issuer: str,
    oauth_config_uri: Optional[str] = None,
) -> tuple[dict, jwt.PyJWKClient]:
    """
    Retrieve JWKS client from a generic OAuth 2.0 issuer.  Constructs the configuration URI if not provided.

    Args:
        oauth_issuer: OAuth issuer used to construct the configuration URI.
        oauth_config_uri: Optional URI to find the OAuth config. If not provided, will be derived from oauth_issuer.

    Returns:
        Tuple of OAuth configuration and JWKS client.
    """
    if not oauth_issuer:
        oauth_issuer = os.environ.get("OAUTH_ISSUER", None) 
    assert oauth_issuer
    oauth_issuer_url = hyperlink.parse(oauth_issuer)
    assert oauth_issuer_url.absolute

    if oauth_config_uri is None:
        oauth_config_uri = oauth_issuer_url.replace(
            path=(".well-known", "oauth-authorization-server") + oauth_issuer_url.path
        ).to_iri().to_text()

    return _get_jwks_client_from_config_uri(oauth_config_uri)

def decode_and_verify_token(
    access_token: str, 
    jwks_client: jwt.PyJWKClient, 
    issuer: str, 
    algorithms: Optional[list[str]] = None,
    audience: Optional[str] = None,
    verify_exp: bool = True,
    verify_aud: bool = True,
    verify_iss: bool = True,
    verify_nbf: bool = False,
    verify_iat: bool = False,
) -> dict:
    """
    Decode and verify the access token with flexible configuration.
    """
    if not issuer:
        issuer = os.environ.get("OIDC_ISSUER", None)

    if not audience:
        audience = os.environ.get("AUDIENCE", None)

    if verify_iss and issuer is None:
        raise Exception("Issuer not provided while expecting to verify the issuer.")
    
    if verify_aud and audience is None:
        raise Exception("Audience not provided while expecting to verify the audience.")
    
    if algorithms is None:
        algorithms = [os.environ.get("ALGORITHM", DEFAULT_ALGORITHM)]
    
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(access_token)
        data = jwt.decode(
            access_token,
            signing_key.key,
            algorithms=algorithms,
            issuer=issuer,
            audience=audience,
            options={
                "verify_exp": verify_exp,
                "verify_aud": verify_aud,
                "verify_iss": verify_iss,
                "verify_iat": verify_iat,
                "verify_nbf": verify_nbf
            },
        )
        data["access_token"] = access_token
        return data
    except jwt.PyJWTError as e:
        logging.exception(f"Token verification failed: {e}")
        raise

def create_oauth2_scheme(token_url: str = "token") -> OAuth2PasswordBearer:
    """
    Create OAuth2 password bearer scheme with configurable token URL.
    """
    return OAuth2PasswordBearer(tokenUrl=token_url)

def create_current_user_dependency(
    jwks_client: jwt.PyJWKClient,
    oidc_issuer: Optional[str] = None,
    audience: Optional[str] = None,
    user_model: type[BaseModel] = ContentGridUser,
    token_url: str = "token",
    algorithms: Optional[list[str]] = None,
    verify_exp: bool = True,
    verify_aud: bool = True,
    verify_iss: bool = True,
    verify_nbf: bool = False,
    verify_iat: bool = False,
):
    """
    Creates a FastAPI dependency for retrieving and verifying the current user from a JWT.

    This function sets up an OAuth2PasswordBearer scheme and a dependency that can be used
    in FastAPI endpoints to authenticate users based on JWTs (JSON Web Tokens). It handles
    token decoding, verification, and user data extraction.

    Args:
        jwks_client: The PyJWKClient instance used to verify the JWT signature.  This client
                     should be initialized with the correct JWKS (JSON Web Key Set) for your
                     authentication provider.
        oidc_issuer: The expected issuer of the JWT (e.g., "https://extensions.eu-west-1.contentgrid.cloud/authentication/external").  This value
                     is used to verify the `iss` (issuer) claim in the JWT.  If provided, the
                     `verify_iss` parameter must be True.
        audience: The expected audience of the JWT (e.g., "contentgrid:extension:extract").  This value is used to
                  verify the `aud` (audience) claim in the JWT. If provided, the `verify_aud`
                  parameter must be True.  This is a crucial security setting.
        user_model: The Pydantic model that represents the user data. Defaults to ContentGridUser.
                     This model will be used to deserialize the JWT payload after successful
                     verification.  It should match the structure of the claims in your JWT.
        token_url: The URL of the token endpoint. This is used by the OAuth2PasswordBearer
                   scheme for its OpenAPI documentation and is typically "/token".
        algorithms: A list of allowed algorithms for JWT verification (e.g., ["RS256", "ES256"]).
                    Defaults to None, which might use a default algorithm or an algorithm from the environment.
                    It's highly recommended to explicitly specify the allowed algorithms for security reasons.
        verify_exp: Whether to verify the 'exp' (expiration time) claim of the JWT. Defaults to True.
        verify_aud: Whether to verify the 'aud' (audience) claim of the JWT. Defaults to True.
        verify_iss: Whether to verify the 'iss' (issuer) claim of the JWT. Defaults to True.
        verify_nbf: Whether to verify the 'nbf' (not before) claim of the JWT. Defaults to False.
        verify_iat: Whether to verify the 'iat' (issued at) claim of the JWT. Defaults to False.

    Returns:
        A callable (dependency) that can be used with FastAPI's `Depends()` to inject
        the authenticated user into an endpoint.  The dependency raises an HTTPException
        with a 401 status code if authentication fails.

    Raises:
        HTTPException: If the token is invalid, expired, has an invalid signature, incorrect issuer or audience,
                       or if the user data cannot be extracted.

    Example:
        # Assuming you have a jwks_client and oidc_issuer configured:
        get_current_user = create_current_user_dependency(
            jwks_client=my_jwks_client,
            oidc_issuer="https://extensions.eu-west-1.contentgrid.cloud/authentication/external",
            audience="contentgrid:extension:extract"  # Important: Set the audience!
        )

        @app.get("/items/")
        async def read_items(current_user: ContentGridUser = Depends(get_current_user)):
            # current_user is now an instance of ContentGridUser, populated from the JWT
            return {"user": current_user}
    """
    oauth2_scheme = create_oauth2_scheme(token_url)

    async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> BaseModel:
        try:
            token_data = decode_and_verify_token(
                access_token=token, 
                jwks_client=jwks_client,
                audience=audience,
                issuer=oidc_issuer,
                algorithms=algorithms,
                verify_aud=verify_aud,
                verify_exp=verify_exp,
                verify_iss=verify_iss,
                verify_nbf=verify_nbf,
                verify_iat=verify_iat
            )
            return user_model(**token_data)
        except Exception:
            logging.exception("Exception thrown in user verification.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return get_current_user
