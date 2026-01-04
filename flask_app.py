import random
import time
import atexit
import os
from urllib.parse import urlparse, parse_qs, quote_plus

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from playwright.sync_api import sync_playwright, Page


# Flask application setup
app = Flask(__name__)
CORS(app)

# Global browser instance management
_BROWSER = None
_PLAYWRIGHT = None

def get_browser():
    """Get or create the global browser instance."""
    global _BROWSER, _PLAYWRIGHT
    
    if _BROWSER is None or not _BROWSER.is_connected():
        print("[DEBUG] Creating new browser instance...")
        if _PLAYWRIGHT is None:
            _PLAYWRIGHT = sync_playwright().start()
        
        _BROWSER = _PLAYWRIGHT.chromium.launch(
            headless=True,  # CRITICAL: Stay headless for VPS
            args=['--no-sandbox']  # Minimal args to prevent crashes
        )
        print("[DEBUG] Browser instance created successfully")
    
    return _BROWSER


# In-memory cache: {query: (results_list, timestamp_seconds)}
CACHE = {}
CACHE_TTL_SECONDS = 10 * 60  # 10 minutes

# Enhanced viewport sizes for realism
VIEWPORT_SIZES = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1536, "height": 864},
    {"width": 1280, "height": 720},
]

# Timezones and locales for rotation
TIMEZONES = [
    "America/New_York", "America/Los_Angeles", "America/Chicago", "America/Denver",
    "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Rome",
    "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata", "Australia/Sydney"
]

LOCALES = ["en-US", "en-GB", "en-CA", "en-AU", "de-DE", "fr-FR", "ja-JP", "zh-CN"]


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


def _random_ua():
    return random.choice(USER_AGENTS)

def _random_viewport():
    return random.choice(VIEWPORT_SIZES)

def _random_timezone():
    return random.choice(TIMEZONES)

def _random_locale():
    return random.choice(LOCALES)




def _extract_target_url(href: str) -> str:
    """Extract the actual target URL from Google redirect links."""
    try:
        if not href:
            return ""
        if href.startswith("/url?") or href.startswith("https://www.google.com/url"):
            parsed = urlparse(href)
            qs = parse_qs(parsed.query)
            real = qs.get("q", [href])[0]
            return real
        return href
    except Exception:
        return href

def _humanize(page: Page, links):
    """Enhanced human behavior simulation with typing and realistic interactions."""
    try:
        vw = page.viewport_size or {"width": 1280, "height": 800}
        
        # Random mouse movements with varying speeds
        for _ in range(random.randint(3, 6)):
            x = random.randint(0, vw["width"])
            y = random.randint(0, vw["height"])
            page.mouse.move(x, y, steps=random.randint(2, 5))
            time.sleep(random.uniform(0.3, 1.2))
        
        # Randomized scroll behavior
        scroll_amount = random.randint(200, 600)
        page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        time.sleep(random.uniform(1.5, 3.0))
        
        # Hover over random elements (not just links)
        hover_candidates = links[:8]  # Increased pool
        random.shuffle(hover_candidates)
        
        for href in hover_candidates[:random.randint(2, 4)]:
            try:
                # More robust locator
                element = page.locator(f'a[href*="{urlparse(href).path}"], a[href="{href}"]').first
                if element.count() > 0:
                    element.hover()
                    time.sleep(random.uniform(0.8, 2.1))
            except Exception:
                continue
        
        # Click behavior with higher success rate
        if hover_candidates:
            target = random.choice(hover_candidates[:5])  # Top 5 only
            try:
                element = page.locator(f'a[href*="{urlparse(target).path}"], a[href="{target}"]').first
                if element.count() > 0:
                    element.click()
                    page.wait_for_load_state("domcontentloaded", timeout=10000)
                    time.sleep(random.uniform(3.0, 6.0))  # Longer reading time
                    
                    # Simulate reading behavior
                    page.evaluate(f"window.scrollBy(0, {random.randint(300, 800)})")
                    time.sleep(random.uniform(1.0, 2.5))
                    
                    page.go_back()
                    page.wait_for_load_state("domcontentloaded", timeout=10000)
                    time.sleep(random.uniform(1.0, 2.0))
            except Exception:
                pass
                
    except Exception as e:
        print(f"[DEBUG] Humanize error: {e}")
        pass




def fetch_google_results(query: str):
    """Enhanced DuckDuckGo search with typing simulation and rotating identities."""
    try:
        print(f"[DEBUG] Enhanced fetch for query='{query}'")
        
        # Use context manager to avoid threading issues
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,  # CRITICAL: Stay headless for VPS
                args=['--no-sandbox']  # Minimal args to prevent crashes
            )
            
            # Generate random identity for this session
            ua = _random_ua()
            viewport = _random_viewport()
            timezone = _random_timezone()
            locale = _random_locale()
            
            print("[DEBUG] Creating isolated context for this search...")
            # Create isolated context for this search
            storage_state = None
            if random.random() > 0.3:  # 70% try to reuse cookies
                try:
                    if os.path.exists("auth.json"):
                        storage_state = "auth.json"
                except:
                    pass
            
            context = browser.new_context(
                user_agent=ua,
                viewport=viewport,
                locale=locale,
                timezone_id=timezone,
                storage_state=storage_state,
                permissions=["geolocation"],
                geolocation={"latitude": random.uniform(-90, 90), "longitude": random.uniform(-180, 180)}
            )
            
            page = context.new_page()
            page.set_default_timeout(20000)  # 20 second timeout
            
            print(f"[DEBUG] Browser state: connected={browser.is_connected()}")
            print(f"[DEBUG] Context state: pages={len(context.pages)}")
            print(f"[DEBUG] Page state: url={page.url}, is_closed={page.is_closed()}")
            
            # Navigate directly to DuckDuckGo HTML version (simpler and more reliable)
            encoded = quote_plus(query)
            search_url = f"https://duckduckgo.com/html/?q={encoded}"
            print(f"[DEBUG] Navigating to DuckDuckGo HTML search: {search_url}")
            try:
                result = page.goto(search_url, wait_until="domcontentloaded")
                print(f"[DEBUG] Navigation result: {result}")
                print(f"[DEBUG] Final URL after navigation: {page.url}")
                
                # Wait for page to load
                time.sleep(random.uniform(2.0, 3.0))
                
                print("[DEBUG] DuckDuckGo HTML page loaded successfully")
            except Exception as e:
                print(f"[ERROR] Failed to load DuckDuckGo HTML page: {e}")
                print(f"[ERROR] Exception type: {type(e).__name__}")
                print(f"[ERROR] Browser connected: {browser.is_connected()}")
                print(f"[ERROR] Context pages: {len(context.pages)}")
                print(f"[ERROR] Page closed: {page.is_closed()}")
                return []
            
            # Handle consent page if present
            try:
                consent_button = page.locator('button:has-text("I agree"), button:has-text("Accept all")').first
                if consent_button.count() > 0 and consent_button.is_visible():
                    consent_button.click()
                    time.sleep(random.uniform(1.5, 2.5))
                    print("[DEBUG] Clicked consent button")
            except:
                pass
            
            # Check for blocks (DuckDuckGo block detection)
            blocks = [
                "Sorry, we are rate limiting requests",
                "Please prove you're not a robot",
                "We have detected unusual traffic",
                "CAPTCHA",
                "rate limit",
                "too many requests"
            ]
            html = page.content()
            if any(b in html.lower() for b in blocks):
                print(f"[WARN] Block page detected by DuckDuckGo - content preview: {html[:500]}...")
                return []
            
            # Wait for search results to appear (DuckDuckGo HTML version)
            print("[DEBUG] Waiting for search results...")
            try:
                page.wait_for_selector(".result, .web-result, .result__body", timeout=15000)
                time.sleep(random.uniform(1.5, 2.5))
                print("[DEBUG] Search results appeared")
            except Exception as e:
                print(f"[ERROR] Search results did not appear: {e}")
                # Debug: show what's actually on the page
                try:
                    page_content = page.content()
                    print(f"[DEBUG] Page content preview: {page_content[:500]}...")
                    print(f"[DEBUG] Current URL: {page.url}")
                except Exception as debug_e:
                    print(f"[DEBUG] Could not get page content: {debug_e}")
                pass
            
            items = []
            links_for_human = []
            
            # Parse DuckDuckGo HTML results
            # Try multiple selectors to find all results - look for organic results, not ads
            containers = page.locator(".result, .web-result").all()
            count = len(containers)
            
            print(f"[DEBUG] Found {count} result containers")
            
            # Process each result container
            for idx, container in enumerate(containers):
                try:
                    # Extract title
                    title_elem = container.locator("h2 a, .result__title, .result__a").first
                    title = title_elem.text_content().strip() if title_elem.count() > 0 else None
                    
                    # Extract link
                    link_elem = container.locator("h2 a, .result__title, .result__a").first
                    link = link_elem.get_attribute("href") if link_elem.count() > 0 else None
                    
                    # Extract snippet
                    snippet_elem = container.locator(".result__snippet, .result__body").first
                    snippet = snippet_elem.text_content().strip() if snippet_elem.count() > 0 else None
                    
                    if title and link:
                        # Extract actual URL from DuckDuckGo redirect URL
                        if link.startswith('//duckduckgo.com/l/?uddg='):
                            # Extract the URL from the uddg parameter
                            import urllib.parse
                            parsed_url = urllib.parse.urlparse(link)
                            query_params = urllib.parse.parse_qs(parsed_url.query)
                            if 'uddg' in query_params:
                                url = urllib.parse.unquote(query_params['uddg'][0])
                            else:
                                url = link
                        else:
                            url = _extract_target_url(link)
                        
                        # Clean up title - remove excessive whitespace and ad text
                        title = ' '.join(title.split()) if title else None
                        # Remove ad-related text from title
                        if 'Ad Viewing ads is privacy protected by DuckDuckGo' in title:
                            # Extract just the main title part (before the ad text)
                            title = title.split('Ad Viewing ads is privacy protected by DuckDuckGo')[0].strip()
                        
                        items.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet
                        })
                        
                        links_for_human.append(url)
                        
                except Exception as e:
                    print(f"[WARN] Failed to parse result {idx}: {e}")
                    continue
            
            print(f"[DEBUG] Successfully parsed {len(items)} results")
            
            # Save cookies for future use
            try:
                context.storage_state(path="auth.json")
                print("[DEBUG] Saved cookies to auth.json")
            except Exception as e:
                print(f"[DEBUG] Could not save cookies: {e}")
            
            return items
            
    except Exception as e:
        print(f"[ERROR] Enhanced scrape error: {e}")
        return []


def cleanup_browser():
    """Clean up the global browser instance on app shutdown."""
    global _BROWSER, _PLAYWRIGHT
    print("[DEBUG] Cleaning up browser instance...")
    try:
        if _BROWSER:
            _BROWSER.close()
            _BROWSER = None
    except Exception as e:
        print(f"[DEBUG] Browser cleanup error (ignored): {e}")
    
    try:
        if _PLAYWRIGHT:
            _PLAYWRIGHT.stop()
            _PLAYWRIGHT = None
    except Exception as e:
        print(f"[DEBUG] Playwright cleanup error (ignored): {e}")


def get_cached(query: str):
    """Return cached results if not expired, else None."""
    entry = CACHE.get(query)
    if not entry:
        return None
    results, ts = entry
    age = time.time() - ts
    if age <= CACHE_TTL_SECONDS:
        print(f"[DEBUG] Cache hit for query='{query}' (age={int(age)}s)")
        return results
    # Expired
    print(f"[DEBUG] Cache expired for query='{query}'")
    CACHE.pop(query, None)
    return None


def set_cache(query: str, results):
    """Store results in cache with current timestamp (skip empty results)."""
    try:
        if not results:
            print(f"[DEBUG] Skip caching empty results for query='{query}'")
            return
        CACHE[query] = (results, time.time())
        print(f"[DEBUG] Cache set for query='{query}' with {len(results)} items")
    except Exception as e:
        print(f"[ERROR] Cache set error: {e}")


@app.route("/")
def index():
    """Serve the test UI."""
    return render_template("index.html")


@app.route("/search", methods=["GET"])
def search():
    """Return JSON array of Google search results for the given query."""
    query = request.args.get("q", "").strip()
    print(f"[DEBUG] Search request received: query='{query}'")
    
    if not query:
        print("[WARN] Empty query received")
        return jsonify([])

    cached = get_cached(query)
    if cached is not None:
        print(f"[DEBUG] Returning cached results for query='{query}'")
        return jsonify(cached)

    print(f"[DEBUG] Fetching fresh results for query='{query}'")
    results = fetch_google_results(query)
    set_cache(query, results)
    print(f"[DEBUG] Returning {len(results)} results for query='{query}'")
    return jsonify(results)




# Register cleanup function for app shutdown
atexit.register(cleanup_browser)

if __name__ == "__main__":
    # Run local development server
    print("[INFO] Starting Flask server with browser reuse...")
    app.run(host="127.0.0.1", port=5000, debug=False)  # Disable debug for production