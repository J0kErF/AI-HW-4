"""Single source of truth for the code version (V3 §8.1, Table 2).

The application validates that the code version matches the configuration
versions (``setup.json``, ``rate_limits.json``) at startup; a mismatch is a
hard error so that a stale config can never silently drive a newer build.
"""

CODE_VERSION = "1.00"


def assert_config_compatible(config_version: str) -> None:
    """Raise if a config file's ``version`` does not match :data:`CODE_VERSION`.

    Args:
        config_version: The ``version`` field read from a config JSON file.

    Raises:
        ValueError: If the major version differs from the code version.
    """
    if config_version != CODE_VERSION:
        raise ValueError(
            f"Config version {config_version!r} != code version {CODE_VERSION!r}. "
            "Re-sync config/ with this build (V3 §8.1)."
        )
