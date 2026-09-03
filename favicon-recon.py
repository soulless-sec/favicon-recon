#!/usr/bin/env python3

import argparse
import codecs
import hashlib
import re
import sys
from urllib.parse import urljoin, urlparse

import mmh3
import requests

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box


console = Console()


# ─────────────────────────────────────────────────────────────
# Banner
# ─────────────────────────────────────────────────────────────

BANNER = r"""
[bold cyan]
   ███████╗ █████╗ ██╗   ██╗██╗ ██████╗ ██████╗ ███╗   ██╗
   ██╔════╝██╔══██╗██║   ██║██║██╔════╝██╔═══██╗████╗  ██║
   █████╗  ███████║██║   ██║██║██║     ██║   ██║██╔██╗ ██║
   ██╔══╝  ██╔══██║╚██╗ ██╔╝██║██║     ██║   ██║██║╚██╗██║
   ██║     ██║  ██║ ╚████╔╝ ██║╚██████╗╚██████╔╝██║ ╚████║
   ╚═╝     ╚═╝  ╚═╝  ╚═══╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝

        F A V I C O N   R E C O N [/bold cyan] | [bold yellow] by soulless
[/bold yellow]
[bold magenta]          Shodan • FOFA • Censys Hash Generator[/bold magenta]
"""


USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/139.0.0.0 Safari/537.36"
)


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def normalize_url(target):

    if not target.startswith(("http://", "https://")):
        target = "https://" + target

    parsed = urlparse(target)

    if not parsed.netloc:
        raise ValueError("Invalid URL")

    return target


def fetch(session, url, timeout):

    try:

        return session.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )

    except requests.RequestException:
        return None


# ─────────────────────────────────────────────────────────────
# Favicon Discovery
# ─────────────────────────────────────────────────────────────

def find_favicons(session, target, timeout):

    candidates = []

    response = fetch(session, target, timeout)

    if response and response.ok:

        html = response.text

        patterns = [

            r'<link[^>]+rel=["\'][^"\']*icon[^"\']*["\']'
            r'[^>]+href=["\']([^"\']+)["\']',

            r'<link[^>]+href=["\']([^"\']+)["\']'
            r'[^>]+rel=["\'][^"\']*icon[^"\']*["\']',

        ]

        for pattern in patterns:

            for match in re.findall(pattern, html, re.I):

                candidates.append(
                    urljoin(response.url, match)
                )

    parsed = urlparse(
        response.url if response else target
    )

    origin = f"{parsed.scheme}://{parsed.netloc}"

    candidates.extend([

        urljoin(origin, "/favicon.ico"),
        urljoin(origin, "/favicon.png"),
        urljoin(origin, "/images/favicon.ico"),
        urljoin(origin, "/images/favicon.png"),
        urljoin(origin, "/apple-touch-icon.png"),
        urljoin(origin, "/apple-touch-icon-precomposed.png"),

    ])

    return list(dict.fromkeys(candidates))


# ─────────────────────────────────────────────────────────────
# Download Favicon
# ─────────────────────────────────────────────────────────────

def download_favicon(session, candidates, timeout):

    for url in candidates:

        response = fetch(
            session,
            url,
            timeout
        )

        if not response:
            continue

        if not response.ok:
            continue

        data = response.content

        if not data:
            continue

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if "text/html" in content_type:
            continue

        return (
            url,
            data,
            content_type
        )

    return None, None, None


# ─────────────────────────────────────────────────────────────
# Shodan Hash
# ─────────────────────────────────────────────────────────────

def shodan_mmh3_hash(data):

    encoded = codecs.encode(
        data,
        "base64"
    )

    return mmh3.hash(encoded)


# ─────────────────────────────────────────────────────────────
# Hashes
# ─────────────────────────────────────────────────────────────

def calculate_hashes(data):

    return {

        "mmh3": shodan_mmh3_hash(data),

        "md5": hashlib.md5(data).hexdigest(),

        "sha1": hashlib.sha1(data).hexdigest(),

        "sha256": hashlib.sha256(data).hexdigest(),

    }


# ─────────────────────────────────────────────────────────────
# Main Output
# ─────────────────────────────────────────────────────────────

def print_results(
    target,
    favicon_url,
    content_type,
    data,
    hashes
):

    console.print()

    # Target information
    table = Table(
        title="🎯 TARGET INFORMATION",
        box=box.ROUNDED,
        border_style="cyan",
        title_style="bold cyan"
    )

    table.add_column(
        "Property",
        style="bold yellow",
        width=18
    )

    table.add_column(
        "Value",
        style="white"
    )

    table.add_row(
        "Target",
        target
    )

    table.add_row(
        "Favicon",
        favicon_url
    )

    table.add_row(
        "Content-Type",
        content_type
    )

    table.add_row(
        "Size",
        f"{len(data)} bytes"
    )

    console.print(table)

    # Hash table
    console.print()

    hash_table = Table(
        title="🔐 FAVICON HASHES",
        box=box.ROUNDED,
        border_style="green",
        title_style="bold green"
    )

    hash_table.add_column(
        "Algorithm",
        style="bold yellow"
    )

    hash_table.add_column(
        "Hash",
        style="bold white"
    )

    hash_table.add_row(
        "MurmurHash3",
        f"[bold cyan]{hashes['mmh3']}[/bold cyan]"
    )

    hash_table.add_row(
        "MD5",
        f"[bold magenta]{hashes['md5']}[/bold magenta]"
    )

    hash_table.add_row(
        "SHA1",
        f"[bold blue]{hashes['sha1']}[/bold blue]"
    )

    hash_table.add_row(
        "SHA256",
        f"[bold green]{hashes['sha256']}[/bold green]"
    )

    console.print(hash_table)

    # Shodan
    console.print()

    console.print(
        Panel(
            f"[bold white]http.favicon.hash:[/bold white]"
            f"[bold cyan]{hashes['mmh3']}[/bold cyan]",
            title="🔎 SHODAN",
            border_style="cyan"
        )
    )

    # FOFA
    console.print(
        Panel(
            f'[bold white]icon_hash="[/bold white]'
            f'[bold magenta]{hashes["mmh3"]}[/bold magenta]'
            f'[bold white]"[/bold white]',
            title="🔎 FOFA",
            border_style="magenta"
        )
    )

    # Censys
    console.print(
        Panel(
        f"""
[bold yellow]Legacy MD5[/bold yellow]

services.http.response.favicons.md5_hash="{hashes['md5']}"


[bold cyan]Platform Host MD5[/bold cyan]

host.services.endpoints.http.favicons.hash_md5="{hashes['md5']}"


[bold magenta]Platform Web MD5[/bold magenta]

web.endpoints.http.favicons.hash_md5="{hashes['md5']}"
        """,
        title="🔎 CENSYS",
        border_style="green"
        )
    )

    # Copy section
    console.print()

    copy_text = Text()

    copy_text.append(
        "Shodan\n",
        style="bold cyan"
    )

    copy_text.append(
        f"  http.favicon.hash:{hashes['mmh3']}\n\n",
        style="white"
    )

    copy_text.append(
        "FOFA\n",
        style="bold magenta"
    )

    copy_text.append(
        f'  icon_hash="{hashes["mmh3"]}"\n\n',
        style="white"
    )

    copy_text.append(
        "Censys\n",
        style="bold green"
    )

    copy_text.append(
        "\nLegacy MD5:\n",
        style="bold yellow"
    )

    copy_text.append(
        f'services.http.response.favicons.md5_hash="{hashes["md5"]}"\n',
        style="white"
    )

    copy_text.append(
        "\nPlatform Host MD5:\n",
        style="bold cyan"
    )

    copy_text.append(
        f'host.services.endpoints.http.favicons.hash_md5="{hashes["md5"]}"\n',
        style="white"
    )

    copy_text.append(
        "\nPlatform Web MD5:\n",
        style="bold magenta"
    )

    copy_text.append(
        f'web.endpoints.http.favicons.hash_md5="{hashes["md5"]}"',
        style="white"
    )

    console.print(
        Panel(
            copy_text,
            title="📋 READY TO COPY",
            border_style="yellow"
        )
    )


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():

    parser = argparse.ArgumentParser(
        description="Favicon Recon / Hash Generator"
    )

    parser.add_argument(
        "target",
        help="Website URL"
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=10,
        help="HTTP timeout (default: 10)"
    )

    args = parser.parse_args()

    console.print(BANNER)

    try:

        target = normalize_url(
            args.target
        )

    except ValueError as e:

        console.print(
            f"[bold red]✘ {e}[/bold red]"
        )

        sys.exit(1)

    session = requests.Session()

    session.headers.update({
        "User-Agent": USER_AGENT
    })

    console.print(
        f"[bold cyan][+] Target:[/bold cyan] "
        f"[white]{target}[/white]"
    )

    console.print(
        "[bold yellow][*] Searching for favicon...[/bold yellow]"
    )

    candidates = find_favicons(
        session,
        target,
        args.timeout
    )

    console.print(
        f"[bold green][+] Found "
        f"{len(candidates)} possible locations[/bold green]"
    )

    favicon_url, favicon_data, content_type = (
        download_favicon(
            session,
            candidates,
            args.timeout
        )
    )

    if not favicon_data:

        console.print(
            "[bold red][-] Favicon not found[/bold red]"
        )

        console.print(
            "\n[bold yellow]Checked locations:[/bold yellow]"
        )

        for url in candidates:

            console.print(
                f"  [red]•[/red] {url}"
            )

        sys.exit(1)

    console.print(
        f"[bold green][✓] Favicon found:[/bold green] "
        f"[white]{favicon_url}[/white]"
    )

    console.print(
        "[bold yellow][*] Calculating hashes...[/bold yellow]"
    )

    hashes = calculate_hashes(
        favicon_data
    )

    console.print(
        "[bold green][✓] Hash calculation completed[/bold green]"
    )

    print_results(
        target,
        favicon_url,
        content_type,
        favicon_data,
        hashes
    )


if __name__ == "__main__":
    main()
