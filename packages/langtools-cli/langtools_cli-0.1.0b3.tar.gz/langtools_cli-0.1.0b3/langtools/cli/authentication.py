import logging
import re

from typing import Any, Dict, Optional, Tuple
import msal
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CLIENT_ID = "fb8f0ad0-4eaa-4b76-8868-4d8fff685341"
TENANT_ID = "common"
APP_SCOPES = [f"api://{CLIENT_ID}/User.Read"]
GRAPH_SCOPES = ["User.Read"]
GRAPH_URL = "https://graph.microsoft.com/v1.0/me/memberOf"

OBO_CLIENT_ID = "e020db6e-37c2-40a7-aca6-4b8b5e6495cc"
OBO_TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"
OBO_SCOPES = ['api://a5a4de99-713c-42c4-a09b-7553cebbe1d7/.default']

HOST_FOR_AUTHENTICATION_PATTERN = re.compile(
    r"serverlessplatform\..*\.binginternal\.com"
)

# See more options in https://msal-python.readthedocs.io/en/latest/#tokencache
GLOBAL_TOKEN_CACHE = msal.TokenCache()  # The TokenCache() is in-memory.

global_app = msal.PublicClientApplication(
    CLIENT_ID, authority=f"https://login.microsoftonline.com/{TENANT_ID}"
)

obo_app = msal.PublicClientApplication(
    OBO_CLIENT_ID, 
    authority=f"https://login.microsoftonline.com/common"
)


def acquire_access_token(scopes):
    # initialize result variable to hole the token response
    result = None

    # Firstly, check the cache to see if this end user has signed in before
    accounts = global_app.get_accounts()
    if accounts:
        logger.info("Account(s) already signed in:")
        for a in accounts:
            logger.info(a["username"])
        chosen = accounts[0]  # Assuming the end user chose this one to proceed
        logger.info("Proceed with account: %s" % chosen["username"])
        # Now let's try to find a token in cache for this account
        result = global_app.acquire_token_silent(scopes, account=chosen)
    if not result:
        logger.info(
            "A local browser window will be open for you to sign in. "
            "CTRL+C to cancel."
        )
        result = global_app.acquire_token_interactive(scopes)

    if "access_token" in result:
        return result["access_token"]
    else:
        logger.info("access_token acquisition failed")
        return None


def acquire_user_groups():
    access_token = acquire_access_token(GRAPH_SCOPES)
    group_list = []

    if access_token is not None:
        # why nextlink? graph REST API only return 100 result,
        # we need to check nextlink odata to get next page results,
        # to finally get full group list
        nextlink = GRAPH_URL
        while nextlink:
            # Calling a web API using the access token
            api_result = requests.get(
                nextlink,
                headers={"Authorization": "Bearer " + access_token},
            ).json()  # the response is JSON
            group_list.extend([item["id"] for item in api_result["value"]])

            if "@odata.nextLink" in api_result:
                nextlink = api_result["@odata.nextLink"]
            else:
                nextlink = None

    if len(group_list) == 0:
        group_list = None
    return group_list


def update_header_with_authentication(
    address: Optional[str] = None, headers: Optional[Dict[str, Any]] = None
):

    if address is None:
        return

    hostname = urlparse(address).hostname
    if not HOST_FOR_AUTHENTICATION_PATTERN.match(hostname):
        logger.info(f"Authentication is not required for address {address}.")
        return headers

    if headers is None:
        headers = {}

    # clear "X-User-Info" to avoid group injection,
    # "Authorization" injection should only be used by our trust app
    headers["X-User-Info"] = ""

    if "Authorization" in headers:
        logger.info(
            "Customized authentication is found in headers, "
            "skip getting authentication."
        )
        return headers

    logger.info(
        f"Authentication is required for address {address}. "
        "Start getting authentication."
    )
    app_token = acquire_access_token(APP_SCOPES)
    group_list = acquire_user_groups()

    # add header to signed user token
    if app_token is not None:
        headers["Authorization"] = f"Bearer {app_token}"
    # add user group list
    if group_list is not None:
        headers["X-User-Info"] = ",".join(group_list)
    
    return headers

def acquire_obo_tokens(scopes=OBO_SCOPES) -> Tuple[str, str]:
    # initialize result variable to hole the token response
    result = None

    # Firstly, check the cache to see if this end user has signed in before
    accounts = obo_app.get_accounts()
    if accounts:
        logger.info("Account(s) already signed in:")
        for a in accounts:
            logger.info(a["username"])
        chosen = accounts[0]  # Assuming the end user chose this one to proceed
        logger.info("Proceed with account: %s" % chosen["username"])
        # Now let's try to find a token in cache for this account
        result = obo_app.acquire_token_silent(scopes, account=chosen)
    if not result:
        logger.info(
            "A local browser window will be open for you to sign in. "
            "CTRL+C to cancel."
        )
        result = obo_app.acquire_token_interactive(scopes)

    if "access_token" in result:
        return result["access_token"], result["refresh_token"]
    else:
        logger.info("access_token acquisition failed")
        return None, None