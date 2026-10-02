from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel="chrome",
        headless=False
    )
    page = browser.new_page()
    page.goto(
        "https://www.instagram.com/bingewithpopcorn/",
        wait_until="domcontentloaded",
        timeout=60000
    )
    page.wait_for_timeout(5000)

    print("Title:", page.title())
    print("URL:", page.url)

    for link in page.locator("a").all():
        text = link.inner_text().strip()
        href = link.get_attribute("href")
        if "follower" in text.lower() or "following" in text.lower():
            print(f"{text} -> {href}")

    input("Press Enter to close...")
    browser.close()
