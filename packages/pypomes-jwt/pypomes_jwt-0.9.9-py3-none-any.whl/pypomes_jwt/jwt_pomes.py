import jwt
from base64 import urlsafe_b64decode
from flask import Request, Response, request
from logging import Logger
from pypomes_db import db_select, db_delete
from typing import Any

from . import (
    JWT_ACCESS_MAX_AGE, JWT_REFRESH_MAX_AGE,
    JWT_DEFAULT_ALGORITHM, JWT_DECODING_KEY,
    JWT_DB_TABLE, JWT_DB_COL_KID,
    JWT_DB_COL_ACCOUNT, JWT_DB_COL_ALGORITHM, JWT_DB_COL_DECODER
)
from .jwt_registry import JwtRegistry

# the JWT data object
__jwt_registry: JwtRegistry = JwtRegistry()


def jwt_needed(func: callable) -> callable:
    """
    Create a decorator to authenticate service endpoints with JWT tokens.

    :param func: the function being decorated
    """
    # ruff: noqa: ANN003
    def wrapper(*args, **kwargs) -> Response:
        response: Response = jwt_verify_request(request=request)
        return response if response else func(*args, **kwargs)

    # prevent a rogue error ("View function mapping is overwriting an existing endpoint function")
    wrapper.__name__ = func.__name__

    return wrapper


def jwt_verify_request(request: Request,
                       logger: Logger = None) -> Response:
    """
    Verify wheher the HTTP *request* has the proper authorization, as per the JWT standard.

    :param request: the request to be verified
    :param logger: optional logger
    :return: *None* if the request is valid, otherwise a *Response* object reporting the error
    """
    # initialize the return variable
    result: Response | None = None

    if logger:
        logger.debug(msg="Validate a JWT token")
    err_msg: str | None = None

    # retrieve the authorization from the request header
    auth_header: str = request.headers.get("Authorization")

    # was a 'Bearer' authorization obtained ?
    if auth_header and auth_header.startswith("Bearer "):
        # yes, extract and validate the JWT access token
        token: str = auth_header.split(" ")[1]
        if logger:
            logger.debug(msg="Bearer token was retrieved")
        errors: list[str] = []
        jwt_validate_token(errors=errors,
                           nature="A",
                           token=token)
        if errors:
            err_msg = "; ".join(errors)
    else:
        # no 'Bearer' found, report the error
        err_msg = "Request header has no 'Bearer' data"

    # log the error and deny the authorization
    if err_msg:
        if logger:
            logger.error(msg=err_msg)
        result = Response(response="Authorization failed",
                          status=401)
    return result


def jwt_assert_account(account_id: str) -> bool:
    """
    Determine whether access for *account_id* has been established.

    :param account_id: the account identification
    :return: *True* if access data exists for *account_id*, *False* otherwise
    """
    return __jwt_registry.access_registry.get(account_id) is not None


def jwt_set_account(account_id: str,
                    claims: dict[str, Any],
                    access_max_age: int = JWT_ACCESS_MAX_AGE,
                    refresh_max_age: int = JWT_REFRESH_MAX_AGE,
                    grace_interval: int = None,
                    logger: Logger = None) -> None:
    """
    Establish the data needed to obtain JWT tokens for *account_id*.

    The parameter *claims* may contain account-related claims, only. Ideally, it should contain,
    at a minimum, *iss*, *birthdate*, *email*, *gender*, *name*, and *roles*.
    It is enforced that the parameter *refresh_max_age* should be at least 300 seconds greater
    than *access-max-age*.

    :param account_id: the account identification
    :param claims: the JWT claimset, as key-value pairs
    :param access_max_age: access token duration, in seconds
    :param refresh_max_age: refresh token duration, in seconds
    :param grace_interval: optional time to wait for token to be valid, in seconds
    :param logger: optional logger
    """
    if logger:
        logger.debug(msg=f"Registering account data for '{account_id}'")

    # register the JWT service
    __jwt_registry.add_account(account_id=account_id,
                               claims=claims,
                               access_max_age=access_max_age,
                               refresh_max_age=max(refresh_max_age, access_max_age + 300),
                               grace_interval=grace_interval,
                               logger=logger)


def jwt_remove_account(account_id: str,
                       logger: Logger = None) -> bool:
    """
    Remove from storage the JWT access data for *account_id*.

    :param account_id: the account identification
    :param logger: optional logger
    return: *True* if the access data was removed, *False* otherwise
    """
    if logger:
        logger.debug(msg=f"Remove access data for '{account_id}'")

    return __jwt_registry.remove_account(account_id=account_id,
                                         logger=logger)


def jwt_validate_token(errors: list[str] | None,
                       token: str,
                       nature: str = None,
                       account_id: str = None,
                       logger: Logger = None) -> dict[str, Any] | None:
    """
    Verify if *token* ia a valid JWT token.

    Raise an appropriate exception if validation failed. Attempt to validate non locally issued tokens
    will not succeed. if *nature* is provided, validate whether *token* is of that nature.
    A token issued locally has the header claim *kid* starting with *A* (for *Access*) or *R* (for *Refresh*),
    followed by its id in the token database, or as a single letter in the range *[B-Z]*, less *R*.
    If the *kid* claim contains such an id, then the cryptographic key needed for validation
    will be obtained from the token database. Otherwise, the current decoding key is used.

    :param errors: incidental error messages
    :param token: the token to be validated
    :param nature: prefix identifying the nature of locally issued tokens
    :param account_id: optionally, validate the token's account owner
    :param logger: optional logger
    :return: The token's claims (header and payload) if if is valid, *None* otherwise
    """
    # initialize the return variable
    result: dict[str, Any] | None = None

    if logger:
        logger.debug(msg="Validate JWT token")
    op_errors: list[str] = []

    # extract needed data from token header
    token_header: dict[str, Any] | None = None
    try:
        token_header: dict[str, Any] = jwt.get_unverified_header(jwt=token)
    except Exception as e:
        op_errors.append(str(e))

    if not op_errors:
        token_kid: str = token_header.get("kid")
        token_alg: str | None = None
        token_decoder: bytes | None = None

        # retrieve token data from database
        if nature and not (token_kid and token_kid[0:1] == nature):
            op_errors.append("Invalid token")
        elif token_kid and len(token_kid) > 1 and \
                token_kid[0:1] in ["A", "R"] and token_kid[1:].isdigit():
            # token was likely issued locally
            where_data: dict[str, Any] = {JWT_DB_COL_KID: int(token_kid[1:])}
            if account_id:
                where_data[JWT_DB_COL_ACCOUNT] = account_id
            recs: list[tuple[str]] = db_select(errors=op_errors,
                                               sel_stmt=f"SELECT {JWT_DB_COL_ALGORITHM}, {JWT_DB_COL_DECODER} "
                                                        f"FROM {JWT_DB_TABLE}",
                                               where_data=where_data,
                                               logger=logger)
            if recs:
                token_alg = recs[0][0]
                token_decoder = urlsafe_b64decode(recs[0][1])
            else:
                op_errors.append("Invalid token")
        else:
            token_alg = JWT_DEFAULT_ALGORITHM
            token_decoder = JWT_DECODING_KEY

        # validate the token
        if not op_errors:
            try:
                # raises:
                #   InvalidTokenError: token is invalid
                #   InvalidKeyError: authentication key is not in the proper format
                #   ExpiredSignatureError: token and refresh period have expired
                #   InvalidSignatureError: signature does not match the one provided as part of the token
                #   ImmatureSignatureError: 'nbf' or 'iat' claim represents a timestamp in the future
                #   InvalidAlgorithmError: the specified algorithm is not recognized
                #   InvalidIssuedAtError: 'iat' claim is non-numeric
                #   MissingRequiredClaimError: a required claim is not contained in the claimset
                payload: dict[str, Any] = jwt.decode(jwt=token,
                                                     options={
                                                         "verify_signature": True,
                                                         "verify_exp": True,
                                                         "verify_nbf": True
                                                     },
                                                     key=token_decoder,
                                                     require=["iat", "iss", "exp", "sub"],
                                                     algorithms=token_alg)
                if account_id and payload.get("sub") != account_id:
                    op_errors.append("Token does not belong to account")
                else:
                    result = {
                        "header": token_header,
                        "payload": payload
                    }
            except Exception as e:
                op_errors.append(str(e))

    if op_errors:
        err_msg: str = "; ".join(op_errors)
        if logger:
            logger.error(msg=err_msg)
        if isinstance(errors, list):
            errors.extend(op_errors)
    elif logger:
        logger.debug(msg="Token is valid")

    return result


def jwt_revoke_token(errors: list[str] | None,
                     account_id: str,
                     token: str,
                     logger: Logger = None) -> bool:
    """
    Revoke the *refresh_token* associated with *account_id*.

    Revoke operations require access to a database table defined by *JWT_DB_TABLE*.

    :param errors: incidental error messages
    :param account_id: the account identification
    :param token: the token to be revoked
    :param logger: optional logger
    :return: *True* if operation could be performed, *False* otherwise
    """
    # initialize the return variable
    result: bool = False

    if logger:
        logger.debug(msg=f"Revoking token of account '{account_id}'")

    op_errors: list[str] = []
    token_claims: dict[str, Any] = jwt_validate_token(errors=op_errors,
                                                      token=token,
                                                      account_id=account_id,
                                                      logger=logger)
    if not op_errors:
        token_kid: str = token_claims["header"].get("kid")
        if token_kid[0:1] not in ["A", "R"]:
            op_errors.append("Invalid token")
        else:
            db_delete(errors=op_errors,
                      delete_stmt=f"DELETE FROM {JWT_DB_TABLE}",
                      where_data={
                          JWT_DB_COL_KID: int(token_kid[1:]),
                          JWT_DB_COL_ACCOUNT: account_id
                      },
                      logger=logger)
    if op_errors:
        if logger:
            logger.error(msg="; ".join(op_errors))
        if isinstance(errors, list):
            errors.extend(op_errors)
    else:
        result = True

    return result


def jwt_issue_token(errors: list[str] | None,
                    account_id: str,
                    nature: str,
                    duration: int,
                    grace_interval: int = None,
                    claims: dict[str, Any] = None,
                    logger: Logger = None) -> str:
    """
    Issue or refresh, and return, a JWT token associated with *account_id*, of the specified *nature*.

    The parameter *nature* must be a single letter in the range *[B-Z]*, less *R*
    (*A* is reserved for *access* tokens, and *R* for *refresh* tokens).
    The parameter *duration* specifies the token's validity interval (at least 60 seconds).
    These claims are ignored, if specified in *claims*: *iat*, *iss*, *exp*, *jti*, *nbf*, and *sub*.

    :param errors: incidental error messages
    :param account_id: the account identification
    :param nature: the token's nature, must be a single letter in the range *[B-Z]*, less *R*
    :param duration: the number of seconds for the token to remain valid (at least 60 seconds)
    :param claims: optional token's claims
    :param grace_interval: optional interval for the token to become active (in seconds)
    :param logger: optional logger
    :return: the JWT token data, or *None* if error
    """
    # inicialize the return variable
    result: str | None = None

    if logger:
        logger.debug(msg=f"Issuing a JWT token for '{account_id}'")
    op_errors: list[str] = []

    try:
        result = __jwt_registry.issue_token(account_id=account_id,
                                            nature=nature,
                                            duration=duration,
                                            claims=claims,
                                            grace_interval=grace_interval,
                                            logger=logger)
        if logger:
            logger.debug(msg=f"Token is '{result}'")
    except Exception as e:
        # token issuing failed
        op_errors.append(str(e))

    if op_errors:
        if logger:
            logger.error("; ".join(op_errors))
        if isinstance(errors, list):
            errors.extend(op_errors)

    return result


def jwt_issue_tokens(errors: list[str] | None,
                     account_id: str,
                     account_claims: dict[str, Any] = None,
                     logger: Logger = None) -> dict[str, Any]:
    """
    Issue the JWT token pair associated with *account_id*, for access and refresh operations.

    These claims are ignored, if provided in *account_claims*: *iat*, *iss*, *exp*, *jti*, *nbf*, and *sub*.
    Other claims specified therein may supercede currently registered account-related claims.

    Structure of the return data:
    {
      "access-token": <jwt-token>,
      "created-in": <timestamp>,
      "expires-in": <seconds-to-expiration>,
      "refresh-token": <jwt-token>
    }

    :param errors: incidental error messages
    :param account_id: the account identification
    :param account_claims: if provided, may supercede currently registered account-related claims
    :param logger: optional logger
    :return: the JWT token data, or *None* if error
    """
    # inicialize the return variable
    result: dict[str, Any] | None = None

    if logger:
        logger.debug(msg=f"Issuing a JWT token pair for '{account_id}'")
    op_errors: list[str] = []

    try:
        result = __jwt_registry.issue_tokens(account_id=account_id,
                                             account_claims=account_claims,
                                             logger=logger)
        if logger:
            logger.debug(msg=f"Token data is '{result}'")
    except Exception as e:
        # token issuing failed
        op_errors.append(str(e))

    if op_errors:
        if logger:
            logger.error("; ".join(op_errors))
        if isinstance(errors, list):
            errors.extend(op_errors)

    return result


def jwt_refresh_tokens(errors: list[str] | None,
                       account_id: str,
                       refresh_token: str,
                       logger: Logger = None) -> dict[str, Any]:
    """
    Refresh the JWT token pair associated with *account_id*, for access and refresh operations.

    The claims in *refresh-token* are used on issuing the new tokens.

    Structure of the return data:
    {
      "access-token": <jwt-token>,
      "created-in": <timestamp>,
      "expires-in": <seconds-to-expiration>,
      "refresh-token": <jwt-token>
    }

    :param errors: incidental error messages
    :param account_id: the account identification
    :param refresh_token: the base refresh token
    :param logger: optional logger
    :return: the JWT token data, or *None* if error
    """
    # inicialize the return variable
    result: dict[str, Any] | None = None

    if logger:
        logger.debug(msg=f"Refreshing a JWT token pair for '{account_id}'")
    op_errors: list[str] = []

    # assert the refresh token
    if refresh_token:
        # is the refresh token valid ?
        account_claims = jwt_validate_token(errors=op_errors,
                                            token=refresh_token,
                                            nature="R",
                                            account_id=account_id,
                                            logger=logger)
        # if it is, revoke current refresh token
        if account_claims and jwt_revoke_token(errors=op_errors,
                                               account_id=account_id,
                                               token=refresh_token,
                                               logger=logger):
            # issue tokens
            result = jwt_issue_tokens(errors=op_errors,
                                      account_id=account_id,
                                      account_claims=account_claims,
                                      logger=logger)
    else:
        # refresh token not found
        op_errors.append("Refresh token was not provided")

    if op_errors:
        if logger:
            logger.error("; ".join(op_errors))
        if isinstance(errors, list):
            errors.extend(op_errors)

    return result


def jwt_get_claims(errors: list[str] | None,
                   token: str,
                   logger: Logger = None) -> dict[str, Any] | None:
    """
    Retrieve and return the claims set of a JWT *token*.

    Any valid JWT token may be provided in *token*, as this operation is not restricted to locally issued tokens.

    Structure of the returned data, for locally issued tokens:
      {
        "header": {
          "alg": "RS256",
          "typ": "JWT",
          "kid": "A1234"
        },
        "payload": {
          "valid-from": <YYYY-MM-DDThh:mm:ss+00:00>
          "valid-until": <YYYY-MM-DDThh:mm:ss+00:00>
          "birthdate": "1980-01-01",
          "email": "jdoe@mail.com",
          "exp": 1516640454,
          "iat": 1516239022,
          "iss": "my_jwt_provider.com",
          "jti": "Uhsdfgr67FGH567qwSDF33er89retert",
          "gender": "M",
          "name": "John Doe",
          "nbt": 1516249022
          "sub": "11111111111",
          "roles": [
            "administrator",
            "operator"
          ]
        }
      }

    :param errors: incidental error messages
    :param token: the token to be inspected for claims
    :param logger: optional logger
    :return: the token's claimset, or *None* if error
    """
    # initialize the return variable
    result: dict[str, Any] | None = None

    if logger:
        logger.debug(msg="Retrieve claims for token")

    try:
        header: dict[str, Any] = jwt.get_unverified_header(jwt=token)
        payload: dict[str, Any] = jwt.decode(jwt=token,
                                             options={"verify_signature": False})
        result = {
            "header": header,
            "payload": payload
        }
    except Exception as e:
        if logger:
            logger.error(msg=str(e))
        if isinstance(errors, list):
            errors.append(str(e))

    return result
