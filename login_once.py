# login_once.py
from playwright.sync_api import sync_playwright

"""
Run this LOCALLY:
1) python -m pip install playwright
2) python -m playwright install chromium
3) python login_once.py
4) In the opened browser, sign into Microsoft/Watson fully (approve MFA)
5) Return to terminal and press Enter to save auth.json
"""

TARGET_URL = "https://watson.soletanchefreyssinet.com/rules"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # show the browser to complete login
    context = browser.new_context()  # fresh context
    page = context.new_page()
    page.goto(TARGET_URL)
    print("\n>>> In the browser, complete Microsoft sign-in (MFA if prompted).")
    print(">>> Make sure you can see the Rules page / tree.")
    input("When you are fully signed in and the page is loaded, press Enter here to save session... ")

    context.storage_state(path="auth.json")
    print("Saved storage state to auth.json")
    browser.close()
