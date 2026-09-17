#!/usr/bin/env python3
"""Read the league site and save what it says.

Run this where the network allows `fantasysurvivorgame.com`. The remote
build environment does not; a local Claude Code session does.

The script does three jobs:

1. Saves the rules and FAQ pages, so the scoring constants stop being a
   guess. See docs/RULES.md.
2. Saves the standings, so the engine knows who it must beat.
3. Saves the pick form, so a later session can write the submitter against
   real HTML instead of invented selectors.

It writes to data/site/. It never writes a password anywhere.

Authentication, in order of preference:

  --profile PATH   Re-use a browser profile that is already signed in.
                   Nothing to type, no password stored. Preferred.
  environment      FSG_EMAIL and FSG_PASSWORD.
  --manual         Open a visible browser, you sign in, press Enter.

Usage:

    pip install playwright && playwright install chromium
    python3 tools/recon.py --profile ~/.config/google-chrome/Default
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "site"
BASE = "https://www.fantasysurvivorgame.com"
GROUP_CODE = "411E-3E80-5B0C"

PAGES = {
    "rules": f"{BASE}/rules.html",
    "faq": f"{BASE}/faq.html",
    "home": f"{BASE}/",
    "group": f"{BASE}/group-join.html?groupcode={GROUP_CODE}",
}


def need_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return True
    except ImportError:
        print("playwright is missing. Install it:\n"
              "    pip install playwright\n"
              "    playwright install chromium", file=sys.stderr)
        return False


def save(name: str, text: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    path.write_text(text, encoding="utf-8")
    print(f"  saved {path.relative_to(ROOT)}  ({len(text)} bytes)")


def dump(page, name: str, url: str) -> None:
    """Save one page as readable text and as HTML."""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(1500)
    except Exception as exc:                      # noqa: BLE001
        print(f"  {name}: could not load ({exc.__class__.__name__})")
        return
    save(f"{name}.html", page.content())
    try:
        save(f"{name}.txt", page.inner_text("body"))
    except Exception:                             # noqa: BLE001
        pass


def find_forms(page) -> list:
    """Describe every input on the page, so the submitter can be written."""
    return page.evaluate("""() => {
      const out = [];
      for (const el of document.querySelectorAll('input,select,button,textarea')) {
        out.push({
          tag: el.tagName.toLowerCase(),
          type: el.getAttribute('type'),
          name: el.getAttribute('name'),
          id: el.getAttribute('id'),
          cls: el.getAttribute('class'),
          value: el.getAttribute('value'),
          text: (el.innerText || '').trim().slice(0, 60),
        });
      }
      return out;
    }""")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", help="path to a signed-in browser profile")
    ap.add_argument("--manual", action="store_true",
                    help="open a visible browser and wait for you to sign in")
    ap.add_argument("--headless", action="store_true", default=None)
    args = ap.parse_args()

    if not need_playwright():
        return 2

    from playwright.sync_api import sync_playwright

    email = os.environ.get("FSG_EMAIL")
    password = os.environ.get("FSG_PASSWORD")
    headless = args.headless
    if headless is None:
        headless = not (args.manual or args.profile)

    with sync_playwright() as pw:
        if args.profile:
            ctx = pw.chromium.launch_persistent_context(
                args.profile, headless=headless)
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
        else:
            browser = pw.chromium.launch(headless=headless)
            ctx = browser.new_context()
            page = ctx.new_page()

        print("reading public pages")
        for name in ("home", "rules", "faq"):
            dump(page, name, PAGES[name])

        if args.manual:
            page.goto(BASE, wait_until="domcontentloaded")
            input("\nSign in in the browser window, then press Enter here: ")
        elif email and password and not args.profile:
            print("signing in with FSG_EMAIL / FSG_PASSWORD")
            page.goto(BASE, wait_until="domcontentloaded")
            # The real field names are unknown until this script has run
            # once. Try the ordinary ones, then fall through and report.
            for sel in ("input[type=email]", "input[name=email]",
                        "input[name=username]"):
                if page.locator(sel).count():
                    page.fill(sel, email)
                    break
            for sel in ("input[type=password]", "input[name=password]"):
                if page.locator(sel).count():
                    page.fill(sel, password)
                    break
            try:
                page.click("button[type=submit], input[type=submit]",
                           timeout=8000)
                page.wait_for_timeout(3000)
            except Exception:                      # noqa: BLE001
                print("  could not find the sign-in button; "
                      "run again with --manual")

        print("reading the league pages")
        dump(page, "group", PAGES["group"])
        save("group_forms.json",
             json.dumps(find_forms(page), indent=2))
        try:
            page.screenshot(path=str(OUT / "group.png"), full_page=True)
            print(f"  saved {(OUT / 'group.png').relative_to(ROOT)}")
        except Exception:                          # noqa: BLE001
            pass

        ctx.close()

    print("\nDone. Next:")
    print("  1. Commit data/site/ (it holds no password).")
    print("  2. Open a Claude Code session and say: 'read data/site/ and")
    print("     correct data/scoring.json, then write tools/submit.py'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
