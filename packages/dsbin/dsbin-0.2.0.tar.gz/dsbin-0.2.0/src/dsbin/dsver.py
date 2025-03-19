#!/usr/bin/env python3

"""Show installed versions of DS packages."""

from __future__ import annotations

from typing import Any

from packaging import version

from dsbase.text import color
from dsbase.version import PackageSource, VersionChecker, VersionInfo


def format_version_info(versions: VersionInfo) -> tuple[str, str]:
    """Format package status and version display."""
    current_version = color(f"{versions.current}", "green")
    latest_version = color(f"{versions.latest}", "yellow")

    if not versions.current:
        symbol = color("✗", "red", attrs=["bold"])
        ver = color("Not installed", "red")
        if versions.latest:
            ver = f"{ver}\n     Latest version: {latest_version}"
        return symbol, ver

    if versions.latest and version.parse(versions.latest) > version.parse(versions.current):
        symbol = color("⚠", "yellow", attrs=["bold"])
        ver = f"{current_version} ({latest_version} available)"
        return symbol, ver

    symbol = color("✓", "green", attrs=["bold"])
    return symbol, current_version


def main() -> None:
    """Show versions of DS packages."""
    checker = VersionChecker()

    # Define packages and their sources
    pypi_source: PackageSource = "pypi"
    packages: list[dict[str, Any]] = [
        {"name": "dsbase", "source": pypi_source},
        {"name": "dsbin", "source": pypi_source},
    ]

    any_updates = False

    for pkg in packages:
        pkg_name = pkg.pop("name")
        source = pkg.pop("source")

        # Check version information
        info = checker.check_package(pkg_name, source=source, **pkg)

        # Format and display the information
        name = color(f"{pkg_name}:", "cyan", attrs=["bold"])
        symbol, version_str = format_version_info(info)

        print(f"{symbol} {name} {version_str}")
        any_updates = any_updates or info.update_available


if __name__ == "__main__":
    main()
