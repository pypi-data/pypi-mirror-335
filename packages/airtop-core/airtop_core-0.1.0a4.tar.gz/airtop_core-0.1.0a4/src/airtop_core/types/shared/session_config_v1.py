# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = [
    "SessionConfigV1",
    "Proxy",
    "ProxyAirtopProxyConfiguration",
    "ProxyProxyCredentials",
    "ProxyProxyConfigurationItem",
    "ProxyProxyConfigurationItemRelay",
    "ProxyProxyConfigurationItemRelayAirtopProxyConfiguration",
    "ProxyProxyConfigurationItemRelayProxyCredentials",
]


class ProxyAirtopProxyConfiguration(BaseModel):
    country: Optional[str] = None
    """
    Country to exit from, in
    [ISO 3166-1 alpha-2 format](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).
    Or `global` to get IP addresses from random countries. We do not guarantee an
    available proxy in all countries.
    """

    sticky: Optional[bool] = None
    """
    Try to maintain the same IP address for the duration for up to a maximum of 30
    minutes. `true` by default. <Note>Stickiness is on a best-effort basis; we
    cannot guarantee that the same IP address will be available for 30 minutes at a
    time.</Note>
    """


class ProxyProxyCredentials(BaseModel):
    url: str

    password: Optional[str] = None

    username: Optional[str] = None


class ProxyProxyConfigurationItemRelayAirtopProxyConfiguration(BaseModel):
    country: Optional[str] = None
    """
    Country to exit from, in
    [ISO 3166-1 alpha-2 format](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).
    Or `global` to get IP addresses from random countries. We do not guarantee an
    available proxy in all countries.
    """

    sticky: Optional[bool] = None
    """
    Try to maintain the same IP address for the duration for up to a maximum of 30
    minutes. `true` by default. <Note>Stickiness is on a best-effort basis; we
    cannot guarantee that the same IP address will be available for 30 minutes at a
    time.</Note>
    """


class ProxyProxyConfigurationItemRelayProxyCredentials(BaseModel):
    url: str

    password: Optional[str] = None

    username: Optional[str] = None


ProxyProxyConfigurationItemRelay: TypeAlias = Union[
    str, ProxyProxyConfigurationItemRelayAirtopProxyConfiguration, ProxyProxyConfigurationItemRelayProxyCredentials
]


class ProxyProxyConfigurationItem(BaseModel):
    domain_pattern: str = FieldInfo(alias="domainPattern")

    relay: ProxyProxyConfigurationItemRelay
    """Configuration for a single custom proxy."""


Proxy: TypeAlias = Union[
    bool, str, ProxyAirtopProxyConfiguration, ProxyProxyCredentials, List[ProxyProxyConfigurationItem]
]


class SessionConfigV1(BaseModel):
    base_profile_id: Optional[str] = FieldInfo(alias="baseProfileId", default=None)
    """Deprecated: Use profileName instead."""

    extension_ids: Optional[List[str]] = FieldInfo(alias="extensionIds", default=None)
    """Google Web Store extension IDs to be loaded into the session."""

    persist_profile: Optional[bool] = FieldInfo(alias="persistProfile", default=None)
    """Deprecated: use Save Profile On Termination API instead."""

    profile_name: Optional[str] = FieldInfo(alias="profileName", default=None)
    """Name of a profile to load into the session."""

    proxy: Optional[Proxy] = None
    """Proxy configuration."""

    timeout_minutes: Optional[int] = FieldInfo(alias="timeoutMinutes", default=None)
    """
    Number of minutes of inactivity (idle timeout) after which the session will
    terminate. The idle timeout is reset when a user makes an incoming HTTP request,
    AI request, or new WebSocket connection to the session. Thus, when using drivers
    like Puppeteer, Selenium or Playwright, the timeout reset depends on the nature
    of the driver request. If not specified, defaults to 10 minutes.
    """
