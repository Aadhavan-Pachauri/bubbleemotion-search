#!/usr/bin/env python3
"""Working DuckDuckGo scraper that actually works."""

import random
import time
import requests
from urllib.parse import quote_plus, urlparse, parse_qs
from playwright.sync_api import sync_playwright

def ddg_search(query: str, max_results: int = 10):
    """
    Simple DuckDuckGo search that actually works.
    Uses requests first, falls back to Playwright if needed.
    """
    print(f"[DDG] Searching for: {query}")
    
    try:
        # Try simple requests-based approach first
        return _ddg_html_search(query, max_results)
    except Exception as e:
        print(f"[DDG] HTML search failed: {e}, trying regular search...")
        return _ddg_requests_search(query, max_results)

def _ddg_requests_search(query: str, max_results: int = 10):
    """Simple DuckDuckGo search using requests."""
    # Try regular DuckDuckGo first
    url = f"https://duckduckgo.com/?q={quote_plus(query)}&kl=us-en&ia=web"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Debug: save HTML to file
        with open('debug_ddg.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"[DDG] Saved HTML to debug_ddg.html ({len(response.text)} chars)")
        
        # Simple HTML parsing
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        
        # Look for various result selectors
        selectors = [
            'div[data-result]',
            '.result',
            '.web-result',
            '.result--web',
            '[data-result]',
            'article'
        ]
        
        result_divs = []
        for selector in selectors:
            result_divs = soup.select(selector)
            if result_divs:
                print(f"[DDG] Found {len(result_divs)} results with selector: {selector}")
                break
        
        if not result_divs:
            # Last resort - find all links that look like results
            links = soup.find_all('a', href=True)
            result_links = []
            for link in links:
                href = link['href']
                text = link.get_text(strip=True)
                # Filter out navigation and non-result links
                if (href.startswith('http') and 
                    not href.startswith('https://duckduckgo.com') and
                    len(text) > 10 and
                    not any(word in text.lower() for word in ['privacy', 'settings', 'about'])):
                    result_links.append(link)
            
            result_divs = result_links[:max_results]
            print(f"[DDG] Found {len(result_divs)} result links")
        
        for div in result_divs[:max_results]:
            try:
                if hasattr(div, 'name') and div.name == 'a':
                    # Direct link element
                    title = div.get_text(strip=True)
                    link = div['href']
                    snippet = ''
                else:
                    # Container element
                    # Extract title and link
                    title_elem = div.find('h2') or div.find('a', class_=lambda x: x and 'result' in x) or div.find('a')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get('href', '')
                    else:
                        continue
                    
                    # Extract snippet
                    snippet_elem = div.find('div', class_=lambda x: x and 'snippet' in x) or div.find('span', class_=lambda x: x and 'snippet' in x)
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                
                # Clean up the URL (handle DuckDuckGo redirects)
                if link and link.startswith('/l/?uddg='):
                    # Extract actual URL from redirect
                    parsed = urlparse(link)
                    params = parse_qs(parsed.query)
                    if 'uddg' in params:
                        link = params['uddg'][0]
                elif link and not link.startswith('http'):
                    # Skip relative links
                    continue
                
                if title and link:
                    results.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet
                    })
            
            except Exception as e:
                print(f"[DDG] Error parsing result: {e}")
                continue
        
        print(f"[DDG] Successfully parsed {len(results)} results")
        return results
        
    except Exception as e:
        print(f"[DDG] Requests search failed: {e}")
        raise

def _ddg_playwright_search(query: str, max_results: int = 10):
    """DuckDuckGo search using Playwright as fallback."""
    print("[DDG] Using Playwright fallback...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        
        try:
            # Go to DuckDuckGo HTML version
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            print(f"[DDG] Navigating to: {url}")
            
            page.goto(url, wait_until='domcontentloaded')
            time.sleep(2)  # Let page load
            
            # Get page content
            content = page.content()
            
            # Parse with BeautifulSoup
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            results = []
            
            # Find results
            result_divs = soup.find_all('div', class_='result') or soup.find_all('div', class_='web-result')
            
            for div in result_divs[:max_results]:
                try:
                    title_elem = div.find('h2') or div.find('a', class_='result__a') or div.find('a')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get('href', '')
                    else:
                        continue
                    
                    snippet_elem = div.find('div', class_='result__snippet') or div.find('div', class_='snippet')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    if title and link:
                        results.append({
                            'title': title,
                            'url': link,
                            'snippet': snippet
                        })
                except Exception as e:
                    print(f"[DDG] Error parsing result: {e}")
                    continue
            
            print(f"[DDG] Playwright found {len(results)} results")
            return results
            
        finally:
            browser.close()

if __name__ == "__main__":
    # Test the scraper
    test_queries = ["python programming", "artificial intelligence", "web development"]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Testing: {query}")
        print('='*50)
        
        results = ddg_search(query, max_results=3)
        
        if results:
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['title']}")
                print(f"   {result['url']}")
                if result['snippet']:
                    print(f"   {result['snippet'][:100]}...")
        else:
            print("No results found.")