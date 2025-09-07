import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.google.com/?zx=1757088878981&no_sw_cr=1")
    page.get_by_role("button", name="Not interested").click()
    page.get_by_role("combobox", name="Search").click()
    page.get_by_role("combobox", name="Search").fill("what are you doing?")
    page.locator("iframe[name=\"a-rlxp8v35ueqp\"]").content_frame.get_by_role("checkbox", name="I'm not a robot").click()
    page.locator("iframe[name=\"c-rlxp8v35ueqp\"]").content_frame.locator("[id=\"5\"]").click()
    page.locator("iframe[name=\"c-rlxp8v35ueqp\"]").content_frame.locator("[id=\"3\"]").click()
    page.locator("iframe[name=\"c-rlxp8v35ueqp\"]").content_frame.locator("[id=\"7\"]").click()
    page.locator("iframe[name=\"c-rlxp8v35ueqp\"]").content_frame.get_by_role("button", name="Verify").click()
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
