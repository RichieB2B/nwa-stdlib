from urllib import parse

import requests
from flask import Blueprint
from flask import request, redirect, session, current_app
from flask import url_for
from nwastdlib.api_client import ApiClientProxy
from werkzeug.exceptions import Unauthorized

REDIRECT_STATE = 'redirect_state'
AUTH_SERVER = 'oauth2_server'
SCOPES = ["read", "write", "admin"]

oauth2 = Blueprint("oauth2", __name__, url_prefix="/oauth2")

req_session = requests.Session()


def add_oauth_remote(app, oauth2_base_url, oauth2_client_id, oauth2_secret):
    app.config[AUTH_SERVER] = dict(
        oauth2_client_id=oauth2_client_id,
        oauth2_secret=oauth2_secret,
        check_token_url=oauth2_base_url + '/oauth/check_token',
        access_token_url=oauth2_base_url + '/oauth/token',
        authorize_url=oauth2_base_url + '/oauth/authorize',
    )
    req_session.auth = (oauth2_client_id, oauth2_secret)

    def force_authorize():
        redirect_url = url_for('oauth2.callback', _external=True)
        intended_url = request.base_url
        if not session.get('user') and intended_url != redirect_url:
            config = current_app.config[AUTH_SERVER]
            state = parse.quote(request.base_url)
            session[REDIRECT_STATE] = state
            full_authorization_url = f"{config['authorize_url']}?" \
                                     f"response_type=code&" \
                                     f"state={state}&" \
                                     f"client_id={config['oauth2_client_id']}&" \
                                     f"scope={'+'.join(SCOPES)}&" \
                                     f"redirect_uri={redirect_url}"
            return redirect(full_authorization_url)

    app.register_blueprint(oauth2)
    app.before_request(force_authorize)


@oauth2.route('/callback')
def callback():
    stored_state = session.get(REDIRECT_STATE)
    callback_state = request.args.get('state')
    if not stored_state or parse.unquote(stored_state) != callback_state:
        raise Unauthorized(description=f"State does not match: {stored_state} vs {callback_state}")

    session.pop(REDIRECT_STATE, None)
    config = current_app.config[AUTH_SERVER]

    data = {'code': request.args.get('code'),
            'redirect_uri': url_for('oauth2.callback', _external=True),
            'grant_type': 'authorization_code'}

    response = req_session.post(url=config['access_token_url'], data=data,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=5)
    if not response.ok:
        raise Unauthorized(description=f"Response for access_token valid {response}")

    json = response.json()
    session['auth_tokens'] = (json['access_token'], json['refresh_token'])

    token_request = req_session.get(url=config['check_token_url'], params={'token': json['access_token']}, timeout=5)
    session['user'] = token_request.json()

    return redirect(callback_state)


def add_access_token_header(client):
    auth_tokens = session.get('auth_tokens')
    if auth_tokens:
        access_token = auth_tokens[0]
        return ApiClientProxy(client, {'Authorization': f"bearer {access_token}"})
    return client


def get_user():
    return session['user'] if 'user' in session else dict()
