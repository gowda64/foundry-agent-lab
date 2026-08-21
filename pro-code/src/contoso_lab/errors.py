from __future__ import annotations


class FoundryConfigurationError(RuntimeError):
    """Raised when the lab is run before Foundry resources are configured."""


def require_configured(value: str | None, setting_name: str) -> str:
    if value:
        return value
    raise FoundryConfigurationError(
        f"{setting_name} is not configured. Set it in pro-code/.env after creating the Foundry project, "
        "uploading the seed files to Foundry IQ / agent knowledge, and registering the required Foundry tools."
    )
