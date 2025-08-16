"""Vrm API."""

import json
import logging
from collections.abc import Generator
from pathlib import Path

import httpx

from vrm_cloud_mqtt.config import settings

logger = logging.getLogger(__name__)

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)


class VrmExceptionError(Exception):
    """Base exception for the Vrm API."""


class LoginFailedError(VrmExceptionError):
    """Exception raised when login fails."""


class TokenAlreadyExistsError(VrmExceptionError):
    """Exception raised when a token already exists."""


class VrmLogin:
    """VrmLogin class for interacting with the Victron Energy VRM API."""

    def __init__(self, username: str, password: str) -> None:
        """Initialize the VrmLogin object."""
        self.username = username
        self.password = password
        self._user_token = None
        self._access_token = None
        self.id_user = None
        self.base_url = "https://vrmapi.victronenergy.com/v2"
        self._load_cached_data()

    @property
    def token(self) -> str | None:
        """Return the token to use for the request."""
        if not self._access_token and not self._user_token:
            return None

        if self._access_token:
            return f"Token {self._access_token}"

        return f"Bearer {self._user_token}"

    def _load_cached_data(self) -> None:
        """Load cached token and idUser from disk if they exist."""
        cache_file = Path(".cache")
        if cache_file.exists():
            try:
                with cache_file.open("r") as f:
                    cache_data = json.load(f)
                    self._access_token = cache_data.get("access_token")
                    self.id_user = cache_data.get("idUser")
                    msg = (
                        f"Loaded cached auth data: t={self._access_token[:10]}..., u={self.id_user}"
                    )
                    logger.info(msg)
            except (OSError, json.JSONDecodeError) as e:
                msg = f"Error loading cached data: {e}"
                logger.exception(msg)

    def _save_data_to_cache(self, access_token: str, id_user) -> None:
        """Save token and idUser to disk cache."""
        cache_file = Path(".cache")
        try:
            cache_data = {"access_token": access_token, "idUser": id_user}
            with cache_file.open("w") as f:
                json.dump(cache_data, f)

            msg = f"Token and idUser cached to disk: t={access_token[:10]}..., u={id_user}"
            logger.info(msg)
        except OSError as e:
            msg = f"Error saving data to cache: {e}"
            logger.exception(msg)

    def login(self) -> None:
        """Login to the Victron Energy VRM API."""
        msg = f"Logging in with username: {self.username} and password: {self.password}"
        logger.info(msg)
        url = f"{self.base_url}/auth/login"
        result = httpx.post(url, json={"username": self.username, "password": self.password})
        response_data = result.json()

        # Cache token and idUser if login is successful
        if response_data.get("status") != "login_success":
            logger.error("Login failed or no token received")
            return

        self._user_token = response_data.get("token")
        self.id_user = response_data.get("idUser")

        token_id = self.get_access_token(settings.token_name)
        if token_id is not None:
            if not settings.revoke_duplicate_token:
                raise TokenAlreadyExistsError("Token already exists")

            msg = f"Revoking duplicate access token {token_id}"
            logger.info(msg)
            self.revoke_access_token(token_id)

        self.create_access_token()

    def revoke_access_token(self, token_id: str) -> None:
        """Revoke an access token."""
        url = f"{self.base_url}/users/{self.id_user}/accesstokens/{token_id}"
        result = httpx.delete(
            url,
            headers={"x-authorization": self.token},
        )
        response_data = result.json()

        if not response_data.get("success", False):
            raise VrmExceptionError("Failed to revoke access token")

    def get_access_token(self, name: str) -> str | None:
        """Check if a token with the given name exists"""
        tokens = self.list_access_token()
        return next(
            (token.get("idAccessToken") for token in tokens if token.get("name") == name),
            None,
        )

    def list_access_token(self) -> list[dict]:
        """List all access tokens for the user."""
        url = f"{self.base_url}/users/{self.id_user}/accesstokens"
        result = httpx.get(
            url,
            headers={"x-authorization": self.token},
        )
        response_data = result.json()

        if not response_data.get("success", False):
            raise LoginFailedError("Login failed or no token received")

        return [
            {"name": token.get("name"), "idAccessToken": token.get("idAccessToken")}
            for token in response_data.get("tokens", [])
        ]

    def create_access_token(self) -> dict:
        """Create an access token."""
        url = f"{self.base_url}/users/{self.id_user}/accesstokens"
        result = httpx.post(
            url,
            json={"name": settings.token_name},
            headers={"x-authorization": self.token},
        )
        response_data = result.json()

        if not response_data.get("success", False):
            raise VrmExceptionError("Failed to create access token")

        self._access_token = response_data.get("token")
        self._save_data_to_cache(self.token, self.id_user)
        return response_data

    def get_sites(self) -> Generator["VrmSite", None, None]:
        """Get the sites for the user."""
        url = f"{self.base_url}/users/{self.id_user}/installations"
        result = httpx.get(url, headers={"x-authorization": self.token})
        data = result.json()

        if not data.get("success", False):
            raise VrmExceptionError("Failed to get sites")

        for site in data.get("records", []):
            yield VrmSite(self, site.get("idSite"))


class VrmSite:
    """VrmSite class for interacting with the Victron Energy VRM API."""

    def __init__(self, login: VrmLogin, site_id: str) -> None:
        """Initialize the VrmSite object."""
        self.login = login
        self.site_id = site_id

    def get_devices(self) -> dict:
        """Get the devices for the site."""
        url = f"{self.login.base_url}/installations/{self.site_id}/diagnostics"
        result = httpx.get(url, headers={"x-authorization": self.login.token})
        data = result.json()

        return self.parse_diagnostics(data.get("records", []))

    def normalize_device_name(self, device_name: str) -> str:
        """Normalize the device name."""
        return device_name.replace(" ", "_").lower()

    def parse_diagnostics(self, data: list[dict]) -> dict:
        """Parse the diagnostics data into a dictionary of devices."""
        devices = {}
        for item in data:
            key = f"{self.normalize_device_name(item.get('Device'))}_{item.get('instance')}"
            if key not in devices:
                devices[key] = {}

            devices[key][self.normalize_device_name(item.get("description"))] = item.get("rawValue")

        return devices
