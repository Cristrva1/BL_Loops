import httpx
import pytest

from sales_curator.connectors.network import (
    NetworkDisabled,
    NetworkPolicy,
    NetworkPolicyError,
    SafeHttpClient,
    system_resolver,
)


def _public_resolver(_host: str) -> tuple[str, ...]:
    return ("142.250.72.14",)


def _policy(**overrides) -> NetworkPolicy:
    values = {
        "network_enabled": True,
        "runtime_network": True,
        "real_connectors_enabled": True,
        "allowed_domains": ("openlibrary.org", "googleapis.com"),
        "max_bytes": 100_000,
        "max_url_budget": 10,
        "user_agent": "BL-Loops-SalesCurator/0.2 educational-research",
    }
    values.update(overrides)
    return NetworkPolicy(**values)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("network_enabled", False),
        ("runtime_network", False),
        ("real_connectors_enabled", False),
    ],
)
def test_network_requires_all_configuration_gates(field: str, value: bool) -> None:
    with pytest.raises(NetworkDisabled):
        _policy(**{field: value}).authorize(run_authorized=True, url_budget=1)


def test_network_requires_explicit_authorization_for_each_run() -> None:
    with pytest.raises(NetworkDisabled, match="corrida"):
        _policy().authorize(run_authorized=False, url_budget=1)


def test_configured_url_budget_is_a_fail_closed_cap() -> None:
    with pytest.raises(NetworkDisabled, match="MAX_URLS_PER_RUN"):
        _policy(max_url_budget=0).authorize(run_authorized=True, url_budget=1)
    with pytest.raises(NetworkDisabled, match="supera"):
        _policy(max_url_budget=2).authorize(run_authorized=True, url_budget=3)


def test_https_allowlist_accepts_exact_host_and_subdomain() -> None:
    policy = _policy().authorize(run_authorized=True, url_budget=2)
    assert (
        policy.validate_url(
            "https://openlibrary.org/search.json?q=ventas", resolver=_public_resolver
        )
        == "https://openlibrary.org/search.json?q=ventas"
    )
    assert policy.validate_url(
        "https://www.googleapis.com/books/v1/volumes", resolver=_public_resolver
    ).startswith("https://www.googleapis.com/")


@pytest.mark.parametrize(
    "url",
    [
        "http://openlibrary.org/search.json",
        "https://openlibrary.org.evil.example/search.json",
        "https://user:secret@openlibrary.org/search.json",
        "https://127.0.0.1/private",
        "https://169.254.169.254/latest/meta-data",
    ],
)
def test_url_policy_rejects_unsafe_targets(url: str) -> None:
    policy = _policy().authorize(run_authorized=True, url_budget=1)
    with pytest.raises(NetworkPolicyError):
        policy.validate_url(url, resolver=_public_resolver)


def test_dns_rebinding_to_private_address_is_rejected() -> None:
    policy = _policy().authorize(run_authorized=True, url_budget=1)
    with pytest.raises(NetworkPolicyError, match="privada"):
        policy.validate_url(
            "https://openlibrary.org/search.json", resolver=lambda _host: ("10.0.0.8",)
        )


def test_outside_allowlist_is_rejected_before_dns_resolution() -> None:
    policy = _policy().authorize(run_authorized=True, url_budget=1)
    resolved = False

    def resolver(_host: str) -> tuple[str, ...]:
        nonlocal resolved
        resolved = True
        return ("142.250.72.14",)

    with pytest.raises(NetworkPolicyError, match="allowlist"):
        policy.validate_url("https://evil.example/data", resolver=resolver)
    assert resolved is False


def test_system_resolver_is_public_and_malformed_port_fails_as_policy_error() -> None:
    assert callable(system_resolver)
    policy = _policy().authorize(run_authorized=True, url_budget=1)
    with pytest.raises(NetworkPolicyError, match="puerto"):
        policy.validate_url("https://openlibrary.org:not-a-port/search.json")


def test_json_client_rechecks_redirect_domain() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "https://evil.example/data.json"})

    client = SafeHttpClient(
        _policy().authorize(run_authorized=True, url_budget=2),
        transport=httpx.MockTransport(handler),
        resolver=_public_resolver,
    )
    with pytest.raises(NetworkPolicyError, match="allowlist"):
        client.get_json("https://openlibrary.org/search.json")
    client.close()


def test_json_client_enforces_streamed_size_and_mime() -> None:
    def too_large(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "application/json"}, content=b"x" * 80)

    client = SafeHttpClient(
        _policy(max_bytes=32).authorize(run_authorized=True, url_budget=1),
        transport=httpx.MockTransport(too_large),
        resolver=_public_resolver,
    )
    with pytest.raises(NetworkPolicyError, match="tamaño"):
        client.get_json("https://openlibrary.org/search.json")
    client.close()

    def html(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/html"}, text="<html></html>")

    client = SafeHttpClient(
        _policy().authorize(run_authorized=True, url_budget=1),
        transport=httpx.MockTransport(html),
        resolver=_public_resolver,
    )
    with pytest.raises(NetworkPolicyError, match="JSON"):
        client.get_json("https://openlibrary.org/search.json")
    client.close()


def test_json_client_rejects_malformed_content_length_as_policy_error() -> None:
    def malformed(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/json", "content-length": "not-a-number"},
            content=b"{}",
        )

    client = SafeHttpClient(
        _policy().authorize(run_authorized=True, url_budget=1),
        transport=httpx.MockTransport(malformed),
        resolver=_public_resolver,
    )
    with pytest.raises(NetworkPolicyError, match="Content-Length"):
        client.get_json("https://openlibrary.org/search.json")
    client.close()
