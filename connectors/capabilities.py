# SPDX-License-Identifier: Apache-2.0
"""Versioned, vendor-neutral connector capability manifests."""
from __future__ import annotations

from copy import deepcopy
from types import MappingProxyType

CAPABILITY_MANIFEST_VERSION = "1"
_ALLOWED_SUPPORT = frozenset({"supported", "unsupported"})


def validate_capability_manifest(manifest: dict) -> None:
    """Fail closed when a connector advertises an ambiguous capability contract."""
    if not isinstance(manifest, dict):
        raise ValueError("capability_manifest_must_be_object")
    if manifest.get("manifest_version") != CAPABILITY_MANIFEST_VERSION:
        raise ValueError("unsupported_capability_manifest_version")
    provider = manifest.get("provider")
    if not isinstance(provider, str) or not provider.strip() or provider != provider.lower():
        raise ValueError("invalid_capability_provider")
    capabilities = manifest.get("capabilities")
    if not isinstance(capabilities, dict) or not capabilities:
        raise ValueError("capabilities_must_be_non_empty_object")
    for name, declaration in capabilities.items():
        if not isinstance(name, str) or "." not in name or name != name.lower():
            raise ValueError("invalid_capability_name")
        if not isinstance(declaration, dict) or set(declaration) != {"support"}:
            raise ValueError("invalid_capability_declaration")
        if declaration["support"] not in _ALLOWED_SUPPORT:
            raise ValueError("invalid_capability_support")


def capability_manifest(provider: str, capabilities: dict[str, str]) -> dict:
    """Build and validate one explicit manifest; absence never means unsupported."""
    manifest = {
        "manifest_version": CAPABILITY_MANIFEST_VERSION,
        "provider": provider,
        "capabilities": {name: {"support": support} for name, support in capabilities.items()},
    }
    validate_capability_manifest(manifest)
    return manifest


def capability_support(manifest: dict, capability: str) -> str | None:
    """Return declared support, preserving unknown/absent as None."""
    validate_capability_manifest(manifest)
    declaration = manifest["capabilities"].get(capability)
    return declaration["support"] if declaration is not None else None
