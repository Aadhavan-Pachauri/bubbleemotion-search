#!/usr/bin/env python3
"""Simple search interface for testing DuckDuckGo scraping directly."""

from simple_ddg_scraper import scrape_ddg_html

def search_api(query):
    """Search using DuckDuckGo scraper directly."""
    try:
        print(f"[SEARCH] Querying DuckDuckGo: {query}")
        results = scrape_ddg_html(query, max_results=10)
        return results
            
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        return []

def main():
    """Main search interface."""
    print("=== Simple Search Interface ===")
    print("Connected to DuckDuckGo scraper directly")
    print("Type 'quit' or 'exit' to stop")
    print("-" * 40)
    
    while True:
        try:
            query = input("\nSearch: ").strip()
            
            if not query:
                continue
                
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
                
            results = search_api(query)
            
            if not results:
                print("No results found.")
                continue
                
            print(f"\nFound {len(results)} results:")
            print("-" * 40)
            
            for i, result in enumerate(results[:5], 1):  # Show top 5 results
                title = result.get('title', 'No title')
                url = result.get('url', 'No URL')
                snippet = result.get('snippet', '')[:150]
                
                print(f"{i}. {title}")
                print(f"   {url}")
                if snippet:
                    print(f"   {snippet}...")
                print()
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()