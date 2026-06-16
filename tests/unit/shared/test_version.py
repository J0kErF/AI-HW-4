"""Tests for the version-compatibility guard (V3 §8.1)."""

import pytest

from graphquest.shared.version import CODE_VERSION, assert_config_compatible


def test_matching_version_passes() -> None:
    """A config version equal to the code version must not raise."""
    assert_config_compatible(CODE_VERSION)  # should not raise


def test_mismatched_version_raises() -> None:
    """A divergent config version must raise ValueError (fail-fast)."""
    with pytest.raises(ValueError, match="!= code version"):
        assert_config_compatible("0.99")
