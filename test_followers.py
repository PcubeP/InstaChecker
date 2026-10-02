from pathlib import Path
from playwright.sync_api import sync_playwright
import re

profile_dir = Path("instagram_browser_profile").resolve()

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(profile_dir),
        channel="chrome",
        headless=False
    )

    page = context.pages[0] if context.pages else context.new_page()

    page.goto(
        "https://www.instagram.com/bingewithpopcorn/",
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(5000)

    followers_link = page.get_by_text(
        re.compile(r"followers", re.IGNORECASE)
    ).first

    followers_link.click()
    page.wait_for_timeout(3000)

    dialogs = page.get_by_role("dialog")

    print("Followers dialog found:", dialogs.count() > 0)

    if dialogs.count() > 0:
        dialog = dialogs.first
        print("\nDialog text:")
        print(dialog.inner_text()[:3000])

        print("\nVisible profile links:")
        links = dialog.locator("a[href^='/']")
        for i in range(min(links.count(), 20)):
            link = links.nth(i)
            print(link.inner_text().strip(), "->", link.get_attribute("href"))

    input("\nInspect the Chrome window, then press Enter to close...")
    context.close()