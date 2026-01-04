#!/usr/bin/env python3
"""Simple DuckDuckGo HTML scraper that actually works."""

import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

def scrape_ddg_html(query: str, max_results: int = 10):
    """
    Scrape DuckDuckGo HTML results directly.
    Uses the HTML endpoint that doesn't require JavaScript.
    """
    print(f"[DDG] Scraping HTML for: {query}")
    
    # Use the HTML endpoint
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    print(f"[DDG] Using URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save HTML for debugging
        with open('ddg_debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        results = []
        
        # Look for result containers - DuckDuckGo HTML uses specific structure
        result_containers = soup.find_all('div', class_='result') or soup.find_all('div', class_='web-result') or soup.find_all('div', class_='result results_links results_links_deep web-result')
        
        if not result_containers:
            # Try to find any div that contains results
            all_divs = soup.find_all('div')
            result_containers = []
            for div in all_divs:
                # Look for divs that contain links and look like results
                links = div.find_all('a', href=True)
                if len(links) > 0 and any('duckduckgo.com' not in link['href'] for link in links):
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
                    import urllib.parse
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
        
        print(f"[DDG] Successfully scraped {len(results)} results")
        return results
        
    except Exception as e:
        print(f"[DDG] Scraping failed: {e}")
        return []

if __name__ == "__main__":
    # Test the scraper
    test_queries = ["python programming", "artificial intelligence", "web development"]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Testing: {query}")
        print('='*50)
        
        results = scrape_ddg_html(query, max_results=3)
        
        if results:
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['title']}")
                print(f"   {result['url']}")
                if result['snippet']:
                    print(f"   {result['snippet'][:100]}...")
        else:
            print("No results found.")