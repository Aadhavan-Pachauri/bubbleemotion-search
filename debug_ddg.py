#!/usr/bin/env python3
"""Debug DuckDuckGo page structure."""

import sys
sys.path.append('/Users/surabhi/Desktop/search bubble ')

from playwright.sync_api import sync_playwright
import time
import random

def debug_ddg():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        # Navigate to DuckDuckGo and search
        page.goto("https://duckduckgo.com")
        time.sleep(2)
        
        # Type search query
        search_box = page.locator('input[name="q"]').first
        search_box.click()
        for char in "openai":
            search_box.type(char, delay=random.uniform(50, 200))
            time.sleep(random.uniform(0.05, 0.2))
        search_box.press("Enter")
        
        # Wait for results
        time.sleep(3)
        
        # Take screenshot
        page.screenshot(path="ddg_debug.png", full_page=True)
        print("Screenshot saved as ddg_debug.png")
        
        # Get page content
        content = page.content()
        print(f"Page URL: {page.url}")
        
        # Look for result containers
        selectors = [
            "[data-result='organic']",
            ".result", 
            ".nrn-react-div",
            "h2",
            "h3",
            "a[href^='http']",
            ".result__title",
            ".result__a",
            ".result__snippet"
        ]
        
        for selector in selectors:
            elements = page.locator(selector)
            count = elements.count()
            if count > 0:
                print(f"Found {count} elements with selector: {selector}")
                # Show first few elements
                for i in range(min(3, count)):
                    elem = elements.nth(i)
                    print(f"  {i+1}: {elem.text_content()[:100]}...")
        
        context.close()
        browser.close()

if __name__ == "__main__":
    debug_ddg()