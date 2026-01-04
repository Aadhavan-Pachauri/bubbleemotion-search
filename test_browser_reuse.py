#!/usr/bin/env python3
"""Test the browser reuse pattern."""

import sys
sys.path.append('/Users/surabhi/Desktop/search bubble ')

from flask_app import get_browser, fetch_google_results

print("[TEST] Testing browser reuse pattern...")

# Test 1: Get browser instance
print("[TEST] Getting browser instance...")
browser = get_browser()
print(f"[TEST] Browser connected: {browser.is_connected()}")

# Test 2: First search
print("[TEST] Testing first search...")
try:
    results1 = fetch_google_results("openai")
    print(f"[TEST] First search completed: {len(results1)} results")
except Exception as e:
    print(f"[TEST] First search failed: {e}")

# Test 3: Second search (should reuse browser)
print("[TEST] Testing second search...")
try:
    results2 = fetch_google_results("chatgpt")
    print(f"[TEST] Second search completed: {len(results2)} results")
except Exception as e:
    print(f"[TEST] Second search failed: {e}")

# Test 4: Check browser still connected
print(f"[TEST] Browser still connected: {browser.is_connected()}")

print("[TEST] Browser reuse test completed!")