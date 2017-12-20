import requests
from nwastdlib.api_client import ApiClientProxy
from werkzeug.exceptions import Unauthorized

AUTH_RESOURCE_SERVER = "auth_resource_server"
SCOPES = ["read", "write", "admin"]

req_session = requests.Session()


def obtain_client_credentials_token(app, oauth2_token_url, oauth2_client_id, oauth2_secret, force=False):
    if not force and AUTH_RESOURCE_SERVER in app.config and "access_token" in app.config[AUTH_RESOURCE_SERVER]:
        return

    app.config[AUTH_RESOURCE_SERVER] = dict(
        oauth2_token_url=oauth2_token_url,
        oauth2_client_id=oauth2_client_id,
        oauth2_secret=oauth2_secret
    )
    response = req_session.post(url=oauth2_token_url,
                                data={"grant_type": "client_credentials"},
                                auth=(oauth2_client_id, oauth2_secret),
                                timeout=5)
    if not response.ok:
        raise Unauthorized(description=f"Response for obtaining access_token {response.json()}")

    json = response.json()
    # Spec dictates that client credentials should not be allowed to get a refresh token
    app.config[AUTH_RESOURCE_SERVER]["access_token"] = json["access_token"]


def add_client_credentials_token_header(client, app):
    if AUTH_RESOURCE_SERVER in app.config and "access_token" in app.config[AUTH_RESOURCE_SERVER]:
        access_token = app.config[AUTH_RESOURCE_SERVER]["access_token"]
        return ApiClientProxy(client, {"Authorization": f"bearer {access_token}"})
    return client


def refresh_client_credentials_token(app):
    config = app.config[AUTH_RESOURCE_SERVER]
    return obtain_client_credentials_token(app,
                                           config["oauth2_token_url"],
                                           config["oauth2_client_id"],
                                           config["oauth2_secret"],
                                           force=True)
