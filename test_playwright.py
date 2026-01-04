#!/usr/bin/env python3
"""Test Playwright navigation in isolation."""

import time
import random
from playwright.sync_api import sync_playwright

def test_simple_navigation():
    """Test basic Playwright navigation."""
    try:
        print("[TEST] Starting Playwright test...")
        
        playwright = sync_playwright().start()
        print("[TEST] Playwright started")
        
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-setuid-sandbox'
            ]
        )
        print("[TEST] Browser launched")
        
        context = browser.new_context()
        print("[TEST] Context created")
        
        page = context.new_page()
        page.set_default_timeout(20000)
        print("[TEST] Page created")
        
        # Test 1: Simple navigation
        print("[TEST] Testing simple navigation to httpbin.org...")
        try:
            result = page.goto("https://httpbin.org/html", wait_until="domcontentloaded")
            print(f"[TEST] Navigation successful: {result.status}")
            print(f"[TEST] Page URL: {page.url}")
        except Exception as e:
            print(f"[TEST] Simple navigation failed: {e}")
        
        # Test 2: Google navigation
        print("[TEST] Testing Google navigation...")
        try:
            result = page.goto("https://www.google.com", wait_until="domcontentloaded")
            print(f"[TEST] Google navigation successful: {result.status}")
            print(f"[TEST] Google page URL: {page.url}")
            
            # Get page content
            content = page.content()
            print(f"[TEST] Page content length: {len(content)}")
            if "google" in content.lower():
                print("[TEST] Google content verified")
            else:
                print("[TEST] Warning: Google content not verified")
                
        except Exception as e:
            print(f"[TEST] Google navigation failed: {e}")
            print(f"[TEST] Exception type: {type(e).__name__}")
        
        # Cleanup
        print("[TEST] Starting cleanup...")
        print(f"[TEST] Browser connected: {browser.is_connected()}")
        print(f"[TEST] Context pages: {len(context.pages)}")
        print(f"[TEST] Page closed: {page.is_closed()}")
        
        try:
            context.close()
            print("[TEST] Context closed successfully")
        except Exception as e:
            print(f"[TEST] Context close error: {e}")
        
        try:
            browser.close()
            print("[TEST] Browser closed successfully")
        except Exception as e:
            print(f"[TEST] Browser close error: {e}")
        
        try:
            playwright.stop()
            print("[TEST] Playwright stopped successfully")
        except Exception as e:
            print(f"[TEST] Playwright stop error: {e}")
        
        print("[TEST] Cleanup completed")
        
    except Exception as e:
        print(f"[TEST] Critical error: {e}")
        print(f"[TEST] Exception type: {type(e).__name__}")

if __name__ == "__main__":
    test_simple_navigation()