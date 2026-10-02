
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import re
import time
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================

PROFILE_DIR = Path("instagram_browser_profile").resolve()
PROFILE_URL = "https://www.instagram.com/bingewithpopcorn/"
OUTPUT_FILE = Path("follow_back_results.txt").resolve()

MAX_SCROLLS = 250
SCROLL_DELAY = 3.0
PAUSE_BETWEEN_LISTS = 15
STABLE_ROUNDS = 5

# ==========================================
# INSTAGRAM INTERRUPTION DETECTION
# ==========================================

INTERRUPTION_PHRASES = [
    "try again later",
    "we restrict certain activity",
    "please wait a few minutes",
    "your account has been temporarily blocked",
    "suspicious activity",
    "confirm it's you",
    "challenge_required",
    "checkpoint_required",
    "automated behavior"
]


def check_for_interruption(page):
    """Detect common Instagram restrictions or verification prompts."""
    current_url = page.url.lower()

    if any(term in current_url for term in [
        "/challenge/",
        "/checkpoint/"
    ]):
        raise RuntimeError(
            "Instagram has presented a verification or checkpoint page."
        )

    try:
        body_text = page.locator("body").inner_text(timeout=5000).lower()
    except PlaywrightTimeoutError:
        return

    for phrase in INTERRUPTION_PHRASES:
        if phrase in body_text:
            raise RuntimeError(
                f"Instagram restriction or verification detected: {phrase}"
            )


# ==========================================
# OPEN FOLLOWERS / FOLLOWING
# ==========================================

def open_list(page, list_name):
    """Open a Followers or Following dialog."""
    check_for_interruption(page)

    pattern = re.compile(
        rf"^\s*[\d,.]+\s+{list_name}\s*$",
        re.IGNORECASE
    )

    target = page.get_by_text(pattern).first
    target.click(timeout=15000)

    dialog = page.get_by_role("dialog").first
    dialog.wait_for(state="visible", timeout=15000)

    page.wait_for_timeout(1500)
    check_for_interruption(page)

    return dialog


# ==========================================
# USERNAME COLLECTION
# ==========================================

def collect_visible_usernames(dialog):
    """Collect usernames from profile links currently rendered in the dialog."""
    usernames = set()

    excluded = {
        "explore",
        "accounts",
        "direct",
        "reels",
        "stories",
        "about",
        "legal",
        "privacy",
        "developer"
    }

    links = dialog.locator("a[href^='/']")

    for i in range(links.count()):
        href = links.nth(i).get_attribute("href") or ""

        match = re.fullmatch(r"/([^/?#]+)/?", href)

        if match:
            username = match.group(1).strip().lower()

            if username and username not in excluded:
                usernames.add(username)

    return usernames


def scroll_dialog(dialog):
    """
    Scroll the dialog's most likely list container.
    Returns:
        "scrolled" if a scroll was attempted
        "bottom" if the container is at its bottom
        "not_found" if no scrollable container was found
    """
    return dialog.evaluate("""
        dialog => {
            const nodes = [
                dialog,
                ...dialog.querySelectorAll('*')
            ];

            const candidates = nodes.filter(node => {
                const style = getComputedStyle(node);

                return (
                    node.scrollHeight > node.clientHeight + 10 &&
                    ['auto', 'scroll'].includes(style.overflowY)
                );
            });

            if (!candidates.length) {
                return 'not_found';
            }

            // Choose the container with the greatest scrollable area.
            candidates.sort((a, b) => {
                const aRange = a.scrollHeight - a.clientHeight;
                const bRange = b.scrollHeight - b.clientHeight;
                return bRange - aRange;
            });

            const target = candidates[0];

            const atBottom =
                target.scrollTop + target.clientHeight >=
                target.scrollHeight - 5;

            if (atBottom) {
                return 'bottom';
            }

            const previousTop = target.scrollTop;

            target.scrollTop = Math.min(
                target.scrollTop + Math.max(
                    400,
                    target.clientHeight * 0.7
                ),
                target.scrollHeight
            );

            if (target.scrollTop <= previousTop) {
                return 'bottom';
            }

            return 'scrolled';
        }
    """)


def collect_usernames(dialog, page, list_name):
    """Collect visible usernames gradually while scrolling."""
    usernames = set()
    stable_rounds = 0
    completed = False

    print(f"\nStarting {list_name} collection...")

    for scroll_number in range(1, MAX_SCROLLS + 1):
        check_for_interruption(page)

        # Capture currently rendered profile links.
        usernames.update(collect_visible_usernames(dialog))
        previous_count = len(usernames)

        scroll_result = scroll_dialog(dialog)

        if scroll_result == "not_found":
            print(
                f"Could not identify a scrollable container "
                f"for {list_name}."
            )
            break

        if scroll_result == "bottom":
            # Capture any remaining currently rendered entries.
            page.wait_for_timeout(1000)
            check_for_interruption(page)
            usernames.update(collect_visible_usernames(dialog))
            completed = True
            print(f"{list_name}: reached the bottom of the list.")
            break

        # Wait between scrolls to avoid rapid repeated interaction.
        time.sleep(SCROLL_DELAY)
        check_for_interruption(page)

        # Capture usernames newly loaded after scrolling.
        usernames.update(collect_visible_usernames(dialog))

        current_count = len(usernames)

        if current_count == previous_count:
            stable_rounds += 1
        else:
            stable_rounds = 0

        print(
            f"{list_name}: {current_count} usernames collected "
            f"(scroll {scroll_number}/{MAX_SCROLLS})"
        )

        if stable_rounds >= STABLE_ROUNDS:
            print(
                f"{list_name}: no new usernames detected for "
                f"{STABLE_ROUNDS} consecutive scrolls."
            )
            break

    else:
        print(
            f"{list_name}: maximum scroll limit of "
            f"{MAX_SCROLLS} reached."
        )

    # Final capture of whatever is currently rendered.
    usernames.update(collect_visible_usernames(dialog))

    return usernames, completed


# ==========================================
# REPORT GENERATION
# ==========================================

def save_report(followers, following, status, error_message=None):
    """Overwrite the report with current results."""
    not_following_back = sorted(following - followers)

    results = [
        "INSTAGRAM FOLLOW-BACK REPORT",
        "=" * 45,
        f"Profile: {PROFILE_URL}",
        f"Generated: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "",
        f"Collection status: {status}",
        f"Followers collected: {len(followers)}",
        f"Following collected: {len(following)}",
        f"Accounts not following you back: {len(not_following_back)}",
        "",
        "ACCOUNTS YOU FOLLOW THAT DON'T FOLLOW YOU BACK",
        "=" * 45,
    ]

    if not_following_back:
        results.extend(f"@{username}" for username in not_following_back)
    else:
        results.append(
            "No accounts identified in the collected lists."
        )

    results.extend([
        "",
        "=" * 45,
        "COLLECTION NOTES",
        "=" * 45,
        "This report is based only on usernames collected from",
        "Instagram's visible interface during this run.",
        "",
        "A completed scroll does not guarantee that Instagram",
        "displayed every account or that the lists were unchanged",
        "while they were being collected.",
        "",
        "Compare collected totals with Instagram's displayed",
        "counts before treating this report as complete.",
        "",
        "No accounts were unfollowed or messaged."
    ])

    if error_message:
        results.extend([
            "",
            "INTERRUPTION DETAILS",
            "=" * 45,
            error_message
        ])

    OUTPUT_FILE.write_text(
        "\n".join(results),
        encoding="utf-8"
    )

    return not_following_back


# ==========================================
# MAIN
# ==========================================

def main():
    followers = set()
    following = set()

    followers_completed = False
    following_completed = False
    status = "Incomplete"
    error_message = None

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="chrome",
            headless=False
        )

        page = (
            context.pages[0]
            if context.pages
            else context.new_page()
        )

        try:
            print("Opening Instagram profile...")

            page.goto(
                PROFILE_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )
            page.wait_for_timeout(5000)

            check_for_interruption(page)

            print("Profile loaded:", page.url)

            # Collect Followers.
            print("\nOpening Followers...")
            followers_dialog = open_list(page, "followers")

            followers, followers_completed = collect_usernames(
                followers_dialog,
                page,
                "Followers"
            )

            # Pause before interacting with the next list.
            print(
                f"\nPausing for {PAUSE_BETWEEN_LISTS} seconds "
                "before collecting Following..."
            )
            time.sleep(PAUSE_BETWEEN_LISTS)

            check_for_interruption(page)

            # Close Followers dialog.
            page.keyboard.press("Escape")
            page.wait_for_timeout(1500)

            check_for_interruption(page)

            # Collect Following.
            print("\nOpening Following...")
            following_dialog = open_list(page, "following")

            following, following_completed = collect_usernames(
                following_dialog,
                page,
                "Following"
            )

            if followers_completed and following_completed:
                status = "Scroll completed for both lists; verify counts"
            else:
                status = "Potentially incomplete"

        except KeyboardInterrupt:
            status = "Interrupted manually"
            error_message = "The process was stopped by the user."

        except Exception as error:
            status = "Interrupted or incomplete"
            error_message = str(error)

            print("\nCollection stopped:")
            print(error_message)

        finally:
            not_following_back = save_report(
                followers,
                following,
                status,
                error_message
            )

            print("\n" + "=" * 45)
            print("FOLLOW-BACK REPORT")
            print("=" * 45)
            print(f"Collection status: {status}")
            print(f"Followers collected: {len(followers)}")
            print(f"Following collected: {len(following)}")
            print(
                f"Not following you back: "
                f"{len(not_following_back)}"
            )
            print(f"\nReport saved to:\n{OUTPUT_FILE}")

            if status != "Scroll completed for both lists; verify counts":
                print(
                    "\nWarning: collection may be incomplete. "
                    "Review the report before relying on the results."
                )

            try:
                input("\nPress Enter to close the browser...")
            except EOFError:
                pass

            context.close()


if __name__ == "__main__":
    main()