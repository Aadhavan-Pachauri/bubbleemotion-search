#!/usr/bin/env python3
"""
Quick test of the new flexible psychological classifier.
"""

import sys
import os
sys.path.append('/Users/surabhi/Desktop/search bubble')

from emotion_classifier import classify_query

def test_classifier():
    """Test the classifier with key examples."""
    
    test_cases = [
        "yay!!!",
        "LOLLLLL 😂😂😂...",
        "...",
        "fine",
        "I'm so excited about this amazing project!",
        "I hate this so much",
        "I'm really worried about tomorrow"
    ]
    
    print("Testing Flexible Psychological Classifier")
    print("=" * 60)
    
    for text in test_cases:
        print(f"\nInput: '{text}'")
        try:
            result = classify_query(text)
            
            print(f"Primary State: {result['primary_state']}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Tool: {result['tool']}")
            
            # Show psychological profile
            profile = result['psychological_profile']
            print(f"Psychological Profile:")
            print(f"  Valence: {profile['valence']:.2f} (-1=negative, +1=positive)")
            print(f"  Arousal: {profile['arousal']:.2f} (0=calm, 1=intense)")
            print(f"  Engagement: {profile['engagement']:.2f} (-1=disengaged, +1=highly engaged)")
            print(f"  Regulation: {profile['regulation']:.2f} (0=active, 1=neutral)")
            
            print(f"Key Insights:")
            for insight in result['psychological_insights'][:2]:  # Show top 2
                print(f"  - {insight}")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 40)

if __name__ == "__main__":
    test_classifier()