#!/usr/bin/env python3
"""Test DuckDuckGo rate limiting with multiple searches."""

import sys
import time
import random
sys.path.append('/Users/surabhi/Desktop/search bubble ')

from flask_app import fetch_google_results

def test_rate_limiting():
    """Test rate limiting with multiple searches."""
    print("[RATE TEST] Testing DuckDuckGo rate limiting...")
    
    # Test queries for rate limiting
    test_queries = [
        "artificial intelligence", "data science", "web development",
        "machine learning", "python tutorial", "javascript basics",
        "cloud computing", "cybersecurity", "mobile app development",
        "blockchain technology", "internet of things", "quantum computing",
        "virtual reality", "augmented reality", "robotics",
        "natural language processing", "computer vision", "deep learning",
        "neural networks", "data visualization", "software engineering",
        "database management", "network security", "algorithm design",
        "programming languages", "operating systems", "computer architecture"
    ]
    
    results = []
    errors = []
    
    for i, query in enumerate(test_queries[:25]):  # Test 25 searches
        print(f"\n[RATE TEST] Search {i+1}/25: '{query}'")
        
        try:
            start_time = time.time()
            search_results = fetch_google_results(query)
            end_time = time.time()
            
            results.append({
                'query': query,
                'result_count': len(search_results),
                'response_time': end_time - start_time,
                'success': True
            })
            
            print(f"[RATE TEST] ✓ Found {len(search_results)} results in {end_time - start_time:.2f}s")
            
            # Show first result as sample
            if search_results:
                print(f"[RATE TEST] Sample: {search_results[0]['title'][:60]}...")
            
        except Exception as e:
            errors.append({
                'query': query,
                'error': str(e),
                'attempt': i+1
            })
            print(f"[RATE TEST] ✗ Error: {e}")
        
        # Add delay between searches (2-5 seconds as recommended)
        if i < len(test_queries[:25]) - 1:  # Don't delay after last search
            delay = random.uniform(2.0, 5.0)
            print(f"[RATE TEST] Waiting {delay:.1f}s before next search...")
            time.sleep(delay)
    
    # Summary
    print(f"\n{'='*60}")
    print("[RATE TEST] SUMMARY")
    print(f"{'='*60}")
    print(f"Total searches: {len(results) + len(errors)}")
    print(f"Successful searches: {len(results)}")
    print(f"Failed searches: {len(errors)}")
    
    if results:
        avg_results = sum(r['result_count'] for r in results) / len(results)
        avg_response_time = sum(r['response_time'] for r in results) / len(results)
        print(f"Average results per search: {avg_results:.1f}")
        print(f"Average response time: {avg_response_time:.2f}s")
    
    if errors:
        print(f"\nErrors encountered:")
        for error in errors:
            print(f"  - Search {error['attempt']}: {error['error']}")
    
    print(f"\n[RATE TEST] Rate limiting test completed!")

if __name__ == "__main__":
    test_rate_limiting()