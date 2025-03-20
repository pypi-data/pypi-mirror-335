# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable, Optional
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from ..._utils import PropertyInfo

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


class ProxyAirtopProxyConfiguration(TypedDict, total=False):
    country: str
    """
    Country to exit from, in
    [ISO 3166-1 alpha-2 format](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).
    Or `global` to get IP addresses from random countries. We do not guarantee an
    available proxy in all countries.
    """

    sticky: bool
    """
    Try to maintain the same IP address for the duration for up to a maximum of 30
    minutes. `true` by default. <Note>Stickiness is on a best-effort basis; we
    cannot guarantee that the same IP address will be available for 30 minutes at a
    time.</Note>
    """


class ProxyProxyCredentials(TypedDict, total=False):
    url: Required[str]

    password: str

    username: str


class ProxyProxyConfigurationItemRelayAirtopProxyConfiguration(TypedDict, total=False):
    country: str
    """
    Country to exit from, in
    [ISO 3166-1 alpha-2 format](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).
    Or `global` to get IP addresses from random countries. We do not guarantee an
    available proxy in all countries.
    """

    sticky: bool
    """
    Try to maintain the same IP address for the duration for up to a maximum of 30
    minutes. `true` by default. <Note>Stickiness is on a best-effort basis; we
    cannot guarantee that the same IP address will be available for 30 minutes at a
    time.</Note>
    """


class ProxyProxyConfigurationItemRelayProxyCredentials(TypedDict, total=False):
    url: Required[str]

    password: str

    username: str


ProxyProxyConfigurationItemRelay: TypeAlias = Union[
    str, ProxyProxyConfigurationItemRelayAirtopProxyConfiguration, ProxyProxyConfigurationItemRelayProxyCredentials
]


class ProxyProxyConfigurationItem(TypedDict, total=False):
    domain_pattern: Required[Annotated[str, PropertyInfo(alias="domainPattern")]]

    relay: Required[ProxyProxyConfigurationItemRelay]
    """Configuration for a single custom proxy."""


Proxy: TypeAlias = Union[
    bool, str, ProxyAirtopProxyConfiguration, ProxyProxyCredentials, Iterable[ProxyProxyConfigurationItem]
]


class SessionConfigV1(TypedDict, total=False):
    base_profile_id: Annotated[str, PropertyInfo(alias="baseProfileId")]
    """Deprecated: Use profileName instead."""

    extension_ids: Annotated[Optional[List[str]], PropertyInfo(alias="extensionIds")]
    """Google Web Store extension IDs to be loaded into the session."""

    persist_profile: Annotated[bool, PropertyInfo(alias="persistProfile")]
    """Deprecated: use Save Profile On Termination API instead."""

    profile_name: Annotated[str, PropertyInfo(alias="profileName")]
    """Name of a profile to load into the session."""

    proxy: Proxy
    """Proxy configuration."""

    timeout_minutes: Annotated[int, PropertyInfo(alias="timeoutMinutes")]
    """
    Number of minutes of inactivity (idle timeout) after which the session will
    terminate. The idle timeout is reset when a user makes an incoming HTTP request,
    AI request, or new WebSocket connection to the session. Thus, when using drivers
    like Puppeteer, Selenium or Playwright, the timeout reset depends on the nature
    of the driver request. If not specified, defaults to 10 minutes.
    """
