#!/usr/bin/env python3
"""
Test the new flexible psychological classifier.
"""

import sys
sys.path.append('/Users/surabhi/Desktop/search bubble')

from emotion_classifier import classify_query

def test_flexible_classifier():
    """Test the new flexible psychological classifier."""
    
    test_cases = [
        # Positive cases
        "yay!!!",
        "LOLLLLL 😂😂😂...",
        "I'm so excited about this amazing project!",
        "This is absolutely incredible and wonderful!",
        
        # Negative cases
        "I hate this so much",
        "I'm really worried about tomorrow",
        "I don't know what to do anymore",
        "Whatever. I don't care anymore",
        
        # Short/ambiguous cases
        "...",
        "fine",
        "ok",
        "whatever",
        
        # Mixed/complex cases
        "I'm confused and scared but also hopeful",
        "This is both exciting and terrifying",
        
        # Neutral cases
        "The weather is nice today",
        "I need to buy groceries",
        "Meeting at 3pm tomorrow"
    ]
    
    print("Testing Flexible Psychological Classifier")
    print("=" * 50)
    
    for test_text in test_cases:
        print(f"\nInput: '{test_text}'")
        result = classify_query(test_text)
        
        print(f"Primary State: {result['primary_state']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Tool: {result['tool']}")
        print(f"Psychological Profile:")
        for key, value in result['psychological_profile'].items():
            print(f"  {key}: {value:.2f}")
        
        print(f"Psychological Insights:")
        for insight in result['psychological_insights']:
            print(f"  - {insight}")
        
        print(f"Emotional Nuance:")
        for key, value in result['emotional_nuance'].items():
            if isinstance(value, list):
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_flexible_classifier()