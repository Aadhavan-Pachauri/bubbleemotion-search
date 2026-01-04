#!/usr/bin/env python3
"""Search engine module with DuckDuckGo HTML scraper."""

import requests
import time
import random
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

def scrape_ddg_html(query: str, max_results: int = 10):
    """
    Scrape DuckDuckGo HTML results directly.
    Uses Googlebot user agents and sophisticated bypass techniques.
    """
    print(f"[DDG] Scraping HTML for: {query}")
    
    # Googlebot user agents that are widely whitelisted
    googlebot_agents = [
        'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/120.0.0.0 Safari/537.36',
        'Googlebot/2.1 (+http://www.google.com/bot.html)',
        'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    ]
    
    # Regular browser agents for fallback
    browser_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    # Try multiple endpoints with different approaches
    endpoints = [
        f"https://html.duckduckgo.com/html/?q={quote_plus(query)}",
        f"https://lite.duckduckgo.com/lite/?q={quote_plus(query)}",
        f"https://duckduckgo.com/?q={quote_plus(query)}&ia=web",
    ]
    
    # Create a session to maintain cookies and appear more human
    session = requests.Session()
    
    for endpoint_index, url in enumerate(endpoints):
        print(f"[DDG] Trying endpoint {endpoint_index + 1}: {url}")
        
        # Rotate between Googlebot and browser agents
        if endpoint_index < 2:  # First 2 attempts with Googlebot
            user_agent = random.choice(googlebot_agents)
        else:  # Fallback to browser agents
            user_agent = random.choice(browser_agents)
        
        # Enhanced headers that look more legitimate
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Add referrer to appear more legitimate (Googlebot typically doesn't send referrer)
        if 'Googlebot' not in user_agent:
            headers['Referer'] = 'https://www.google.com/'
        
        # Add more sophisticated headers for non-Googlebot agents
        if 'Googlebot' not in user_agent:
            headers.update({
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"' if 'Windows' in user_agent else '"macOS"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            })
        
        try:
            # Longer, more random delay to appear more human
            delay = random.uniform(2.0, 5.0)  # 2-5 seconds delay
            print(f"[DDG] Waiting {delay:.1f} seconds before request...")
            time.sleep(delay)
            
            # First attempt with current headers
            response = session.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            
            # Check if we got a bot detection page
            if 'bot' in response.text.lower() and ('challenge' in response.text.lower() or 'anomaly' in response.text.lower()):
                print(f"[DDG] Bot detection triggered with {user_agent}, trying alternative approach...")
                
                # Try with different user agent
                if 'Googlebot' in user_agent:
                    # Switch to browser agent
                    alt_user_agent = random.choice(browser_agents)
                else:
                    # Switch to Googlebot
                    alt_user_agent = random.choice(googlebot_agents)
                
                alt_headers = headers.copy()
                alt_headers['User-Agent'] = alt_user_agent
                
                # Longer delay before retry
                time.sleep(random.uniform(3.0, 6.0))
                response = session.get(url, headers=alt_headers, timeout=20)
                response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Save HTML for debugging
            with open('ddg_debug.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Check if we got actual results or just a bot challenge
            if 'bot' in response.text.lower() and ('challenge' in response.text.lower() or 'anomaly' in response.text.lower()):
                print("[DDG] Still getting bot detection, trying next endpoint...")
                continue
            
            results = []
            
            # Look for result containers - DuckDuckGo HTML uses specific structure
            result_containers = soup.find_all('div', class_='result') or soup.find_all('div', class_='web-result') or soup.find_all('div', class_='result results_links results_links_deep web-result')
            
            if not result_containers:
                # Try alternative selectors that might work
                result_containers = soup.find_all('div', {'class': lambda x: x and 'result' in x})
            
            if not result_containers:
                # Try to find any div that contains results
                all_divs = soup.find_all('div')
                result_containers = []
                for div in all_divs:
                    # Look for divs that contain links and look like results
                    links = div.find_all('a', href=True)
                    if len(links) > 0 and any('duckduckgo.com' not in link['href'] and link['href'].startswith('http') for link in links):
                        result_containers.append(div)
            
            print(f"[DDG] Found {len(result_containers)} result containers")
            
            for container in result_containers[:max_results]:
                try:
                    # Find the main link
                    main_link = None
                    links = container.find_all('a', href=True)
                    
                    for link in links:
                        href = link['href']
                        # Skip DuckDuckGo internal links
                        if 'duckduckgo.com' not in href and href.startswith('http'):
                            main_link = link
                            break
                    
                    if not main_link:
                        continue
                    
                    # Extract title
                    title = main_link.get_text(strip=True)
                    if not title or len(title) < 5:  # Skip very short titles
                        continue
                    
                    # Extract URL
                    url = main_link['href']
                    
                    # Handle DuckDuckGo redirect URLs
                    if '/l/?uddg=' in url:
                        # Extract the actual URL from the redirect
                        parsed = urllib.parse.urlparse(url)
                        params = urllib.parse.parse_qs(parsed.query)
                        if 'uddg' in params:
                            url = urllib.parse.unquote(params['uddg'][0])
                    
                    # Extract snippet/description
                    snippet = ''
                    # Look for any text element that might be a snippet
                    snippet_candidates = container.find_all(['div', 'span', 'p'])
                    for candidate in snippet_candidates:
                        text = candidate.get_text(strip=True)
                        if len(text) > 50 and text != title:  # Reasonable length, not the title
                            snippet = text
                            break
                    
                    if title and url:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
                        
                except Exception as e:
                    print(f"[DDG] Error parsing result: {e}")
                    continue
            
            if len(results) > 0:
                print(f"[DDG] Successfully scraped {len(results)} results using {user_agent}")
                return results
            else:
                print(f"[DDG] No results found with {user_agent}, trying next approach...")
                continue
            
        except Exception as e:
            print(f"[DDG] Endpoint {endpoint_index + 1} failed with {user_agent}: {e}")
            continue
    
    print("[DDG] All endpoints failed, returning empty results")
    return []