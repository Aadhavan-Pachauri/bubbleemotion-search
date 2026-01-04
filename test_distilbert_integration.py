#!/usr/bin/env python3
"""
Test script to verify DistilBERT-emotion integration
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, '/Users/surabhi/Desktop/search bubble ')

try:
    from emotion_classifier import classify_query, load_model
    
    print("Testing DistilBERT-emotion integration...")
    
    # Test cases for different emotions
    test_cases = [
        "I'm so happy today! Everything is going great! 😊",
        "I'm really sad about what happened... 😢",
        "This makes me so angry! I can't believe it! 😡",
        "I'm scared and worried about the future...",
        "What a surprise! I didn't expect this at all!",
        "I love this so much! It's amazing! ❤️",
        "Everything is fine, just normal day."
    ]
    
    # Load the model first
    print("Loading model...")
    load_model()
    
    # Test each case
    for i, text in enumerate(test_cases):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Input: {text}")
        
        result = classify_query(text)
        
        print(f"Primary State: {result['primary_state']}")
        print(f"Confidence: {result['confidence']:.2f}")
        
        if 'emotion_percentages' in result and result['emotion_percentages']:
            print("Emotion Percentages (DistilBERT):")
            for emotion, percentage in sorted(result['emotion_percentages'].items(), key=lambda x: x[1], reverse=True):
                if percentage > 5:  # Only show emotions > 5%
                    print(f"  {emotion}: {percentage:.1f}%")
        else:
            print("No DistilBERT emotions available (using rule-based only)")
        
        if result['psychological_insights']:
            print(f"Insights: {result['psychological_insights'][0]}")
    
    print("\n✅ Test completed!")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()