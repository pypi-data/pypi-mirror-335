"""
Copyright (c) 2025 Go2Market Insights Inc
All rights reserved.
https://g2m.ai

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import requests
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ApiClient")

TOKEN_REFRESH_DAYS = 10  # Refresh token after 10 days
MAX_ATTEMPTS = 3         # Number of login attempts if we get a timeout, etc.

class SnowflakeAuthClient:
    """
    SnowflakeAuthClient manages low-level interactions with your API using a Snowflake-based token.
    Mirrors the structure of SamlSsoAuthClient (init, _login, _logout, etc.).
    """

    def __init__(self, host=None, verbose=False):
        """
        :param host: e.g. https://ftae4y-accountidenfitier.snowflakecomputing.app
        :param verbose: True for verbose output
        """
        if verbose:
            log.info("Starting: Init Snowflake Client")
        self.host = host.rstrip("/") if host else None
        self._token = {"token": ""}
        self._token_time = None
        self.verbose = verbose

    ###########################################################################
    #                          Basic API calls                                #
    ###########################################################################

    def _get(self, uri, params=None):
        """
        Protected GET request (mirrors the Saml version).
        """
        self._check_token()
        if self.verbose:
            log.info(f"[GET] {uri}")
        r = requests.get(uri, headers=self._headers(), params=params)
        return self._response(r)

    def _post(self, uri, json_obj=None):
        """
        Protected POST request (mirrors the Saml version).
        """
        self._check_token()
        if self.verbose:
            log.info(f"[POST] {uri}")
        r = requests.post(uri, json=json_obj, headers=self._headers())
        return self._response(r)

    def _response(self, r):
        """
        Standardized response format:
        {
          'status': <HTTP status>,
          'response': <parsed JSON or text or None>
        }
        """
        res = {
            'status': r.status_code,
            'response': None
        }
        if 200 <= r.status_code < 300:
            # Attempt to parse JSON
            try:
                res['response'] = r.json()
            except json.JSONDecodeError:
                res['response'] = r.text
        else:
            log.error(f"WARNING! Request returned status code: {r.status_code}")
        return res

    def _headers(self):
        """
        Return headers with Snowflake Token in the Authorization header.
        """
        if self.is_token:
            return {
                "Authorization": f'Snowflake Token="{self._token["token"]}"'
            }
        return {}

    ###########################################################################
    #                       Authentication methods                             #
    ###########################################################################

    def _login(
        self,
        user,
        account,
        endpoint,
        endpoint_path,
        role,
        snowflake_account_url,
        lifetime=59,
        renewal_delay=54,
        attempts=0
    ):
        """
        Acquire a Snowflake token via /login-client/.
        Mirrors SamlSsoAuthClient._login approach, but uses Snowflake endpoints.

        :param user: Snowflake user
        :param account: Snowflake account
        :param endpoint: e.g. xyz.snowflakecomputing.com
        :param endpoint_path: e.g. /my/path
            :default = "/"
        :param role: Snowflake role
        :param snowflake_account_url: e.g. xyz.snowflakecomputing.com
        :param lifetime: token lifetime in minutes
            :default = "59"
        :param renewal_delay: how soon to renew the token
            :default = "54"
        :param attempts: used to limit max number of login attempts
        """
        if self.verbose:
            log.info("Starting: _login for Snowflake token")

        uri = f"{self.host}/login-client/"

        payload = {
            "user": user,
            "account": account,
            "endpoint": endpoint,
            "endpoint_path": endpoint_path,
            "role": role,
            "snowflake_account_url": snowflake_account_url,
            "lifetime": lifetime,
            "renewal_delay": renewal_delay,
        }

        try:
            resp = requests.post(uri, json=payload)
            status_code = resp.status_code

            if status_code == 200:
                data = resp.json()
                self._save_token(data)  # Store token
                if self.verbose:
                    partial_token = (self._token['token'] or '')[:10] + '...'
                    log.info(f"[LOGIN] Acquired Snowflake token: {partial_token}")
            elif status_code == 408:
                if attempts < MAX_ATTEMPTS - 1:
                    if self.verbose:
                        log.info(f"[LOGIN] Timeout. Trying again... [{attempts+1}/{MAX_ATTEMPTS-1}]")
                    return self._login(
                        user,
                        account,
                        endpoint,
                        endpoint_path,
                        role,
                        snowflake_account_url,
                        lifetime,
                        renewal_delay,
                        attempts+1
                    )
                else:
                    log.error(f"Failed {status_code}: Login after multiple attempts.")
            else:
                log.error(f"[LOGIN] Failed with status {status_code}: {resp.text}")

            return status_code
        except Exception as e:
            log.error(f"[LOGIN] Exception: {str(e)}")
            return 400

    def _logout(self):
        """
        Log out via /logout-client/, then clear local token.
        """
        if self.verbose:
            log.info("Starting: _logout")

        uri = f"{self.host}/logout-client/"
        data = self._post(uri)
        resp = data.get('response')

        self.clean_token()  # Clear the token

        if resp and self.verbose:
            log.info(f"[LOGOUT] Response: {resp}")

    ###########################################################################
    #                          Token-related methods                           #
    ###########################################################################

    @property
    def is_token(self):
        return bool(self._token.get('token'))

    def clean_token(self):
        """
        Mirror SamlSsoAuthClient's cleanup approach
        """
        self._token = {"token": ""}
        self._token_time = None

    def _save_token(self, token_dict):
        """
        Save the new token, track the acquisition time.
        We'll assume the server's response is {"token": "<snowflake_token>"}.
        """
        self._token['token'] = token_dict.get('token', '')
        self._token_time = datetime.now()

    def refresh_token(self):
        """
        If you have a /refresh-snowflake-token/ endpoint, implement it here.
        Otherwise, re-login.
        """
        log.info("Starting: Refresh Token (no dedicated endpoint implemented).")
        return 501  # Not implemented

    def _check_token(self):
        """
        Check if token is older than TOKEN_REFRESH_DAYS.
        If so, attempt refresh or re-login.
        """
        if self._token_time and datetime.now() > self._token_time + timedelta(days=TOKEN_REFRESH_DAYS):
            status = self.refresh_token()
            if status != 200:
                self.clean_token()

"""
Usage:

client = SnowflakeAuthClient(host="https://your-api.example.com", verbose=True)

status_code = client._login(
    user="myuser",
    account="MYACCOUNT",
    endpoint="xyz.snowflakecomputing.com",
    endpoint_path="/my/path",
    role="DEV_ROLE",
    snowflake_account_url="xyz.snowflakecomputing.com",
    lifetime=59,
    renewal_delay=54,
)
if status_code == 200:
    # Make calls
    res = client._get("https://your-api.example.com/protected-endpoint/")
    print(res)

    # Logout when done
    client._logout()
"""
