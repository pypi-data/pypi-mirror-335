"""
Copyright (c) 2025 G2M Insights Inc
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

TOKEN_REFRESH_DAYS = 10  # Refresh token after 10 days if you like
MAX_ATTEMPTS = 3         # number of login attempts if a request fails

class SnowflakeAuthClient:
    """
    A simplified client that retrieves a Snowflake token via /login-client/
    and injects it into the Authorization header for subsequent calls.
    """

    def __init__(self, host=None, verbose=False):
        self.host = host.rstrip("/") if host else None
        self.token = None
        self.token_acquired_at = None
        self.verbose = verbose

    def login(
        self,
        user,
        account,
        endpoint,
        role,
        snowflake_account_url,
        lifetime=59,
        renewal_delay=54
    ):
        """
        POST to <host>/login-client/ with JSON body containing
        the necessary Snowflake params. Store the returned token
        for use in subsequent requests.
        """
        if self.verbose:
            log.info("[LOGIN] Requesting Snowflake token...")
        uri = f"{self.host}/login-client/"
        payload = {
            "user": user,
            "account": account,
            "endpoint": endpoint,
            "role": role,
            "snowflake_account_url": snowflake_account_url,
            "lifetime": lifetime,
            "renewal_delay": renewal_delay,
        }

        try:
            resp = requests.post(uri, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("token")
                self.token_acquired_at = datetime.now()
                if self.verbose:
                    partial_token = f"{self.token[:10]}..." if self.token else "None"
                    log.info(f"[LOGIN] Acquired Snowflake token: {partial_token}")
                return True
            else:
                log.error(f"[LOGIN] Failed with status {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            log.error(f"[LOGIN] Exception: {str(e)}")
            return False

    def logout(self):
        """
        Call <host>/logout-client/ if you have a logout endpoint.
        Clears local token.
        """
        if self.verbose:
            log.info("[LOGOUT] Logging out...")
        uri = f"{self.host}/logout-client/"
        try:
            resp = requests.post(uri)
            if self.verbose:
                log.info(f"[LOGOUT] Response: {resp.status_code} {resp.text}")
        except Exception as e:
            log.error(f"[LOGOUT] Exception: {str(e)}")
        finally:
            self.token = None
            self.token_acquired_at = None

    def refresh_token_if_needed(self):
        """
        If you want to refresh automatically after X days, do that here.
        Or call a separate endpoint if you have a /refresh-snowflake-token/.
        """
        if not self.token or not self.token_acquired_at:
            return
        if datetime.now() > self.token_acquired_at + timedelta(days=TOKEN_REFRESH_DAYS):
            log.info("[REFRESH] Token is stale — re-login or call refresh if you have it.")
            # If you have a refresh endpoint, call it here (similar to login).
            # Or simply re-login.

    def _headers(self):
        """
        Return the headers, including Authorization with Snowflake token.
        """
        if self.token:
            return {
                "Authorization": f'Snowflake Token="{self.token}"'
            }
        return {}

    def get(self, path, params=None):
        """
        Example GET with Snowflake token in Authorization header.
        """
        self.refresh_token_if_needed()
        url = f"{self.host}{path}"
        try:
            r = requests.get(url, headers=self._headers(), params=params)
            return self._process_response(r)
        except Exception as e:
            log.error(f"GET Exception: {str(e)}")
            return None

    def post(self, path, data=None):
        """
        Example POST with Snowflake token in Authorization header.
        """
        self.refresh_token_if_needed()
        url = f"{self.host}{path}"
        try:
            r = requests.post(url, json=data, headers=self._headers())
            return self._process_response(r)
        except Exception as e:
            log.error(f"POST Exception: {str(e)}")
            return None

    def _process_response(self, r):
        if 200 <= r.status_code < 300:
            try:
                return r.json()
            except json.JSONDecodeError:
                return r.text
        else:
            log.error(f"Request failed [{r.status_code}]: {r.text}")
            return None
