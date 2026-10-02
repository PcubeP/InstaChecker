from pathlib import Path
from playwright.sync_api import sync_playwright

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

    print("Page title:", page.title())
    print("Current URL:", page.url)
    print("Login form visible:", page.locator('input[name="username"]').is_visible())

    input("Check the Chrome window, then press Enter to close...")
    context.close()