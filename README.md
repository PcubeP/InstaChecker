
# InstaChecker

A lightweight, Python-based Instagram follow-back checker that compares your Followers and Following lists to identify accounts you follow that don't follow you back.

InstaChecker uses **Playwright and Google Chrome** to interact with Instagram's browser interface. It reuses a locally saved browser session, collects visible usernames from your Followers and Following lists, compares them, and generates a text report.

The project is intended for personal use and does not require downloading your Instagram data through Instagram's data export feature.

---

## Features

- **Browser-based automation:** Uses Playwright with your existing Google Chrome installation.
- **Manual authentication:** Log in to Instagram through the browser without entering credentials into the Python scripts.
- **Persistent session:** Reuses a locally stored Chrome profile to avoid logging in every time.
- **Followers collection:** Reads usernames visible in your Instagram Followers list while scrolling.
- **Following collection:** Reads usernames visible in your Instagram Following list while scrolling.
- **Follow-back comparison:** Identifies accounts you follow that are not present in your collected Followers list.
- **Text report:** Generates `follow_back_results.txt` with collected counts and the comparison results.
- **Automatic overwrite:** Replaces the previous report whenever the comparison script runs.
- **Progress reporting:** Displays collection progress and status in the terminal.
- **Interruption handling:** Attempts to detect common Instagram restrictions and verification challenges.
- **Local processing:** Processes collected usernames locally without automatically unfollowing, messaging or interacting with accounts.

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.13 |
| Browser automation | Playwright 1.63.0 |
| Browser | Google Chrome |
| Environment | Python virtual environment |
| Output | Plain text (`.txt`) |
| Platform | Windows |

---

## Project Structure

```text
InstaChecker/
│
├── .venv/                       # Python virtual environment
├── instagram_browser_profile/   # Persistent Chrome session (private)
│
├── login_instagram.py           # Manual Instagram login
├── verify_login.py              # Verify saved login session
├── test_instagram.py            # Initial public profile test
├── test_followers.py            # Test Followers dialog access
├── compare_followers.py         # Collect, compare and report
│
├── follow_back_results.txt      # Generated comparison report
├── requirements.txt             # Python dependencies
├── .gitignore                   # Files excluded from Git
└── README.md                    # Project documentation
```

Some files and folders are generated only after running the scripts. The `.venv`, browser profile and results report are local files and should not be committed to GitHub.

---

## Prerequisites

Before setting up InstaChecker, ensure you have:

- Windows 10 or Windows 11
- Python 3.13 or a compatible Python version
- Google Chrome installed
- Git (if cloning the repository)
- An Instagram account

The current implementation uses the locally installed Chrome browser through Playwright's `channel="chrome"` option.

---

## Installation

### 1. Clone the repository

```powershell
git clone <repository-url>
cd InstaChecker
```

Replace `<repository-url>` with the URL of your GitHub repository.

Alternatively, open the project folder directly in VS Code.

### 2. Create a virtual environment

```powershell
py -3.13 -m venv .venv
```

This creates an isolated Python environment for the project.

### 3. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

This installs the required version of Playwright.

### 4. Verify the installation

```powershell
.\.venv\Scripts\python.exe -m pip show playwright
```

The installed version should match the version specified in `requirements.txt`.

### 5. Browser setup

InstaChecker uses your installed Google Chrome browser.

The project does not require a separate Playwright-managed Chromium installation as long as Google Chrome is installed and available.

---

## Authentication and Session Setup

InstaChecker uses a persistent Chrome profile so that authentication can be performed manually.

### 1. Log in to Instagram

Run:

```powershell
.\.venv\Scripts\python.exe .\login_instagram.py
```

This opens Google Chrome and navigates to Instagram.

Log in manually through the browser. Complete any verification requested by Instagram.

Once logged in and your feed is visible, return to the terminal and press Enter.

### 2. Verify the session

Run:

```powershell
.\.venv\Scripts\python.exe .\verify_login.py
```

This reopens Chrome using the saved browser profile and navigates to your Instagram profile.

Verify that the browser is still logged in.

### Session storage

The persistent browser profile is stored locally in:

```text
instagram_browser_profile/
```

This directory contains authentication-related browser data, such as cookies and session information.

**Treat this folder as sensitive.** Do not share it, upload it to GitHub or commit it to any public repository.

If the session expires, repeat the manual login process.

---

## Usage

Once the browser session has been verified, run the comparison script:

```powershell
.\.venv\Scripts\python.exe .\compare_followers.py
```

The script performs the following operations:

1. Opens Instagram using the saved Chrome session.
2. Navigates to the configured Instagram profile.
3. Opens the Followers dialog.
4. Collects visible usernames and scrolls through the list.
5. Pauses before accessing the next list.
6. Opens the Following dialog.
7. Collects visible usernames and scrolls through the list.
8. Compares the collected usernames.
9. Generates a text report.

The script displays progress and collection counts in the PowerShell terminal.

The browser remains open until the user presses Enter at the end of the run.

### Collection settings

The current script uses the following settings:

| Setting | Value |
|---|---:|
| Maximum scrolls per list | 250 |
| Delay between scrolls | 3 seconds |
| Pause between lists | 15 seconds |
| Stable rounds before stopping | 5 |

These are conservative interaction settings, not guaranteed safe limits. Instagram may restrict automated browsing even when these delays are used.

---

## How the Comparison Works

The script collects usernames from two lists:

- **Followers:** Accounts that follow your profile.
- **Following:** Accounts that your profile follows.

It then performs a set difference:

```python
not_following_back = sorted(following - followers)
```

The result contains usernames that appeared in the collected Following list but not in the collected Followers list.

For example:

```text
Following:
alice
bob
charlie
david

Followers:
alice
charlie
```

The resulting comparison is:

```text
Accounts not following back:
bob
david
```

The comparison is performed locally using Python sets, which also remove duplicate usernames.

---

## Output

The script generates:

```text
follow_back_results.txt
```

This file is created in the project directory and overwritten on each run.

An example report:

```text
INSTAGRAM FOLLOW-BACK REPORT
=============================================
Profile: https://www.instagram.com/bingewithpopcorn/
Generated: YYYY-MM-DD HH:MM:SS

Collection status: Scroll completed for both lists; verify counts
Followers collected: 998
Following collected: 1008
Accounts not following you back: 10

ACCOUNTS YOU FOLLOW THAT DON'T FOLLOW YOU BACK
=============================================
@example_user_1
@example_user_2
@example_user_3

=============================================
COLLECTION NOTES
=============================================
This report is based only on usernames collected from
Instagram's visible interface during this run.
```

The example usernames and counts are illustrative only.

The report also includes collection status and notes about completeness.

A completed scroll does not necessarily mean every account was collected. Always compare the collected counts with the counts displayed on Instagram.

---

## Limitations

InstaChecker relies on Instagram's browser interface rather than an official API.

As a result:

- Instagram may change its interface, breaking existing selectors or scrolling logic.
- Some accounts or list entries may not be visible to the automation.
- Instagram may virtualize list entries, loading and unloading them as the user scrolls.
- Instagram may impose rate limits, verification challenges or other access restrictions.
- A list may stop loading before every account has been collected.
- Followers and Following are collected at different times, so changes to either list during collection may affect the comparison.
- A completed scroll does not guarantee a complete dataset.

The comparison is only as accurate as the usernames collected during the run.

If Instagram displays a rate-limit warning, CAPTCHA, login challenge or other restriction, stop the process. Do not repeatedly retry or attempt to bypass the restriction.

---

## Privacy and Security

InstaChecker is designed for local personal use.

- Instagram credentials are entered manually in Chrome, not hardcoded in Python.
- The persistent browser profile is stored locally.
- The comparison is performed locally.
- The generated report is stored locally.
- The script does not automatically unfollow accounts, send messages or perform other account actions.

### Files that must remain private

The following files and directories should not be uploaded to GitHub:

```text
.venv/
instagram_browser_profile/
follow_back_results.txt
.env
```

These are excluded by the project's `.gitignore`.

Never share the persistent browser profile, as it may contain authentication cookies that provide access to your Instagram session.

---

## Troubleshooting

### Chrome does not open

Ensure Google Chrome is installed and available on your system.

Check that Playwright is installed in the project's virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip show playwright
```

### Instagram asks you to log in again

Run:

```powershell
.\.venv\Scripts\python.exe .\login_instagram.py
```

Complete the login manually and verify the session again.

### Followers or Following dialog does not open

Instagram's interface may have changed, or the relevant list may not be available through the current page.

Inspect the browser manually and check for verification prompts or other restrictions.

### Collection stops early

Compare the collected totals in the report with Instagram's displayed counts.

An incomplete collection can result in missing accounts or inaccurate comparison results. Do not treat the report as complete unless the collection totals and list contents have been adequately verified.

### Instagram displays a restriction or verification prompt

Stop the script and follow Instagram's normal instructions in the browser. Avoid repeatedly running the automation while access is restricted.

---

## Disclaimer

InstaChecker is an unofficial, independently developed project and is not affiliated with, endorsed by or associated with Instagram or Meta.

It is intended for personal experimentation and account-list comparison. Users are responsible for complying with Instagram's applicable terms, policies and restrictions.

Use the tool responsibly and respect platform-imposed limitations.

---

## Future Improvements

Potential future enhancements include:

- A graphical dashboard using Streamlit
- More robust collection completeness checks
- Separate Followers and Following exports for local analysis
- Historical comparison between runs
- Better reporting of collection interruptions
- Filtering and searching within comparison results

These features are ideas for future development and are not necessarily implemented in the current version.

---

## License

This project is licensed under the MIT License.

You are free to use, copy, modify, distribute, sublicense and sell copies of this software, subject to the conditions of the MIT License.

See the [LICENSE](LICENSE) file for the full license text.