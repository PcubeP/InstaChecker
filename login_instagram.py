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
        "https://www.instagram.com/",
        wait_until="domcontentloaded",
        timeout=60000
    )

    print("Chrome is open. Log in to Instagram manually.")

    input(
        "Once you're logged in and can see your Instagram feed, "
        "press Enter here..."
    )

    print("Current page:", page.url)
    print("Browser session is saved locally.")

    context.close()