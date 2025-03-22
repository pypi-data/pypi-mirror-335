import datetime
import http.server
import json
import logging
import random
import threading
import time
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Any, Literal

import requests
from pydantic import BaseModel, ValidationError

from earthscale.v1.exceptions import (
    AuthenticationError,
    EarthscaleClientError,
    NotFoundError,
    TokenRefreshRequired,
    ValidationFailedError,
)
from earthscale.v1.models import Credentials, ErrorResponse
from supabase import Client, ClientOptions

logger = logging.getLogger(__name__)

_SUCCESSFUL_LOGIN_HTML = b"""
    <html>
        <head>
            <style>
                body {
                    background-color: #f0f0f0;
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    color: #333;
                }
                .message {
                    text-align: center;
                    border-radius: 15px;
                    padding: 50px;
                    background-color: #fff;
                    box-shadow: 0px 0px 10px 0px rgba(0,0,0,0.1);
                }
                h1 {
                    margin-bottom: 20px;
                    font-size: 24px;
                }
                p {
                    font-size: 18px;
                }
            </style>
        </head>
        <body>
            <div class="message">
                <h1>You have successfully logged in to Earthscale!</h1>
                <p>You can now close this tab.</p>
            </div>
        </body>
    </html>
"""


def _is_webbrowser_supported() -> bool:
    """Check if webbrowser is supported."""
    try:
        webbrowser.get()
        return True
    except webbrowser.Error:
        return False


class CodeHandler(http.server.BaseHTTPRequestHandler):
    code: str | None = None
    credentials: Credentials | None = None
    client: Client | None = None

    def log_message(self, format: Any, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        code = params.get("code", [None])[0]

        if code is None:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Authentication failed! Did you use the right account?")
            return

        if CodeHandler.client is None:
            raise AuthenticationError("No client available for code exchange")
        session_response = CodeHandler.client.auth.exchange_code_for_session(
            {
                "auth_code": code,
                "redirect_to": "http://localhost:3000",  # Required hack for Supabase
            }
        ).session

        if session_response is None:
            raise AuthenticationError("No session returned from authentication service")

        # Store credentials from session
        CodeHandler.credentials = Credentials(
            access_token=session_response.access_token,
            refresh_token=session_response.refresh_token,
            expires_in=session_response.expires_in,
            expires_at=session_response.expires_at,
            user_id=session_response.user.id,
            user_email=session_response.user.email,
        )

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(_SUCCESSFUL_LOGIN_HTML)
        CodeHandler.code = code


class _EarthscaleHttpClient:
    """Private HTTP client for the Earthscale API.

    This class handles all HTTP-related functionality including:
    - Session management
    - Authentication
    - Request handling and error processing
    - Header management
    """

    def __init__(
        self,
        api_url: str,
        auth_url: str,
        anon_key: str,
        email: str | None = None,
        password: str | None = None,
        credentials_file: Path | None = None,
        session: requests.Session | None = None,
    ):
        """Initialize the HTTP client.

        Args:
            api_url: The URL of the Earthscale API.
            auth_url: URL for authentication service.
            anon_key: The anon key for the authentication service.
            email: Email for authentication.
            password: Password for authentication.
            credentials_file: Path to the credentials file.
            session: Optional custom requests session to use.
        """
        self.api_url: str = api_url.rstrip("/")
        self.auth_url: str = auth_url.rstrip("/")
        self.anon_key: str = anon_key
        self._email: str | None = email
        self._password: str | None = password
        self._credentials_file: Path = (
            credentials_file or Path.home() / ".earthscale" / "credentials.json"
        )
        self._session: requests.Session | None = session
        self._owns_session: bool = False
        self._credentials: Credentials | None = None

    def _save_credentials(self, credentials: Credentials) -> None:
        """Save credentials to file and update headers/session."""
        self._credentials_file.parent.mkdir(exist_ok=True, parents=True)
        with self._credentials_file.open("w") as f:
            f.write(credentials.model_dump_json(indent=2))
        self._credentials = credentials
        if self._session is not None:
            self._session.headers.update(self._headers)

    def _load_credentials(self) -> Credentials | None:
        """Load credentials from file."""
        if not self._credentials_file.exists():
            return None

        with self._credentials_file.open() as f:
            data = json.load(f)
            return Credentials.model_validate(data)

    def _authenticate_with_oauth(self) -> None:
        """Authenticate using OAuth flow."""
        random_port = random.randint(1024, 49151)

        # Initialize Supabase client
        client = Client(
            self.auth_url,
            self.anon_key,
            options=ClientOptions(
                flow_type="pkce",
                auto_refresh_token=False,
            ),
        )

        # Add client to CodeHandler for use during code exchange
        CodeHandler.client = client

        server = http.server.HTTPServer(("localhost", random_port), CodeHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        # Get OAuth URL using Supabase client
        oauth_response = client.auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {
                    "redirect_to": f"http://localhost:{random_port}/auth/callback",
                    "query_params": {
                        "response_type": "code",
                    },
                },
            },
        )
        webbrowser.open(oauth_response.url)

        # Wait for authentication
        timeout_s = 120
        start_time = time.time()
        while CodeHandler.code is None and time.time() - start_time < timeout_s:
            time.sleep(0.5)

        server.shutdown()
        server.server_close()

        if CodeHandler.code is None:
            raise AuthenticationError(
                f"Authentication timed out after {timeout_s} seconds"
            )

        if CodeHandler.credentials is None:
            raise AuthenticationError("No credentials returned from authentication")

        self._save_credentials(CodeHandler.credentials)

    def _authenticate_with_email_password(self) -> None:
        """Authenticate using email and password credentials.

        Raises:
            AuthenticationError: If authentication fails.
        """
        session = self._get_session()
        response = session.post(
            f"{self.auth_url}/auth/v1/token?grant_type=password",
            json={
                "email": self._email,
                "password": self._password,
            },
        )

        if not response.ok:
            raise AuthenticationError(
                f"Login failed, status code: {response.status_code}, response: "
                f"{response.text}"
            )

        auth_data = response.json()
        credentials = Credentials(
            access_token=auth_data["access_token"],
            refresh_token=auth_data["refresh_token"],
            expires_in=auth_data["expires_in"],
            expires_at=auth_data["expires_at"],
            user_email=self._email,
            password=self._password,
        )
        self._save_credentials(credentials)

    def login(self) -> None:
        """Login using service account credentials or OAuth.

        Raises:
            AuthenticationError: If authentication fails.
        """
        # Prioritize email/password authentication
        if self._email and self._password:
            self._authenticate_with_email_password()
        elif _is_webbrowser_supported():
            self._authenticate_with_oauth()
        else:
            raise AuthenticationError(
                "No email or password provided and webbrowser is not supported."
                "Please provide email and password via the EARTHSCALE_EMAIL and"
                "EARTHSCALE_PASSWORD environment variables, or use a supported"
                "browser to authenticate via OAuth."
            )

    def initialize_session(self) -> None:
        """Initialize the session if it doesn't exist."""
        if self._session is None:
            self._session = requests.Session()
            self._owns_session = True

        # Set the default headers
        if self._session.headers is None:
            self._session.headers = {}

        self._session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        # Try to load previous credentials
        self._credentials = self._load_credentials()

        # Refresh the token
        if self._is_token_expired():
            self.refresh_token()

    def _is_token_expired(self) -> bool:
        """Check if the token is expired."""
        if not self._credentials:
            return True
        return (
            self._credentials.expires_at is not None
            and self._credentials.expires_at.replace(tzinfo=datetime.timezone.utc)
            < datetime.datetime.now(datetime.timezone.utc)
        )

    def refresh_token(self) -> None:
        """Refresh the JWT token using the refresh token.

        Raises:
            AuthenticationError: If token refresh fails.
        """
        if not self._credentials or not self._credentials.refresh_token:
            # If refresh token is not available, try to log in again
            self.login()
            return

        session = self._get_session()

        response = session.post(
            f"{self.auth_url}/auth/v1/token?grant_type=refresh_token",
            headers=self._headers,
            json={
                "refresh_token": self._credentials.refresh_token,
            },
        )

        if not response.ok:
            # If refresh fails, try logging in again
            self.login()
            return

        auth_data = response.json()
        credentials = Credentials(
            access_token=auth_data["access_token"],
            refresh_token=auth_data["refresh_token"],
            expires_in=auth_data["expires_in"],
            expires_at=auth_data["expires_at"],
            user_id=auth_data.get("user_id"),
            user_email=auth_data.get("user_email"),
        )
        self._save_credentials(credentials)

    @property
    def _headers(self) -> dict[str, str]:
        """Get the headers for the API request."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self._credentials and self._credentials.access_token:
            headers["Authorization"] = f"Bearer {self._credentials.access_token}"

        if self.anon_key:
            headers["apiKey"] = self.anon_key

        return headers

    def _get_session(self) -> requests.Session:
        """Get the current session or create a new one if none exists."""
        if self._session is None:
            return requests.Session()
        return self._session

    @staticmethod
    def _handle_response(response: requests.Response) -> bytes:
        """Handle the API response.

        Args:
            response: The response from the API.

        Returns:
            Raw response content.

        Raises:
            TokenRefreshRequired: If authentication fails and token refresh is needed.
            AuthenticationError: If authentication fails.
            NotFoundError: If the resource is not found.
            ValidationFailedError: If validation fails.
            ServerError: If the server returns an error.
        """
        # Check for authentication errors that might require token refresh
        if response.status_code == 401:
            raise TokenRefreshRequired("Authentication token expired or invalid")

        # Map status codes to exception types
        error_classes = {
            401: AuthenticationError,
            404: NotFoundError,
            400: ValidationFailedError,
        }

        if not response.ok:
            # Try to parse the error response
            error_class = error_classes.get(
                response.status_code,
                EarthscaleClientError,
            )

            try:
                error = ErrorResponse.model_validate_json(response.text)
                raise error_class(error.message, error.error_class)
            except ValidationError:
                # If we can't parse the error response, use a generic message
                message = (
                    "Authentication failed"
                    if response.status_code == 401
                    else "Resource not found"
                    if response.status_code == 404
                    else "Validation failed"
                    if response.status_code == 400
                    else "Server error"
                    if response.status_code >= 500
                    else f"Request failed with status code {response.status_code}"
                )
                raise error_class(message) from None

        return response.content

    def _make_request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        url: str,
        **kwargs: Any,
    ) -> requests.Response:
        """Make a request with the given method and URL.

        Args:
            method: The HTTP method to use.
            url: The URL to request.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response from the request.
        """
        session = self._get_session()

        if self._session is None:
            # If we're not using a persistent session, we need to set headers manually
            kwargs["headers"] = kwargs.get("headers", {})
            kwargs["headers"].update(self._headers)
            response = session.request(method, url, **kwargs)
            if not self._owns_session:
                session.close()
        else:
            # If we're using a persistent session, headers are already set
            response = session.request(method, url, **kwargs)

        return response

    def request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        endpoint: str,
        data: BaseModel | None = None,
        api_version: str = "v1",
    ) -> bytes:
        """Make a request to the API with automatic retries and token refresh.

        Args:
            method: The HTTP method to use.
            endpoint: The API endpoint to call (without the base URL and version).
            data: Optional data to send with the request.
            api_version: The API version to use. This is basically url prefix.

        Returns:
            Raw response content
        """
        # Ensure we have a token before making the request
        if not self._credentials or not self._credentials.access_token:
            self.login()

        api_version = api_version.strip("/") + "/" if api_version else ""
        url = f"{self.api_url}/{api_version}{endpoint.lstrip('/')}"

        # Prepare request kwargs
        kwargs = {}
        if data is not None:
            kwargs["data"] = data.model_dump_json()

        try:
            response = self._make_request(method, url, **kwargs)
            return self._handle_response(response)
        except TokenRefreshRequired:
            # Token is expired, refresh it and retry the request once
            self.refresh_token()
            response = self._make_request(method, url, **kwargs)
            return self._handle_response(response)

    def close_session(self) -> None:
        """Close the session if we own it."""
        if self._owns_session and self._session is not None:
            self._session.close()
            self._session = None
            self._owns_session = False
