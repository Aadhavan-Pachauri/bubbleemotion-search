#!/usr/bin/env python3
"""Test the advanced psychological emotion classifier."""

import sys
sys.path.append('.')
from emotion_classifier import classify_query

def test_advanced_classifier():
    """Test the classifier with various psychological scenarios."""
    
    print("🧠 Advanced Psychological Emotion Classifier Test")
    print("=" * 60)
    
    test_cases = [
        # Your specific examples
        ("yay!!!", "Simple excitement with punctuation"),
        ("fine", "Short response - potential hidden emotions"),
        ("...", "Minimal response - psychological shutdown?"),
        ("I love this amazing project!", "Positive with intensity"),
        ("Whatever. I don't care anymore", "Dismissive - possible hurt"),
        
        # Additional psychological test cases
        ("I'm so excited about this!!!", "High intensity positive"),
        ("I'm confused and scared", "Mixed negative emotions"),
        ("I don't know what to do anymore", "Despair/helplessness"),
        ("This is absolutely incredible and wonderful!", "Extreme positive"),
        ("I'm really worried about tomorrow", "Anxiety about future"),
        ("Whatever you say", "Passive resistance"),
        ("I'm fine. Really.", "Defensive - possibly not fine"),
        ("I can't believe this happened!", "Shock/surprise"),
        ("Why would you even ask that?", "Defensive/questioning"),
        ("I'm so tired of everything", "Exhaustion/despair"),
        ("This is amazing but also terrifying", "Mixed emotions"),
        ("I guess that's okay", "Reluctant acceptance"),
        ("I'm not angry, just disappointed", "Complex negative"),
        ("Thank you so much! This means everything", "Gratitude with intensity"),
        ("I don't understand what's happening", "Confusion/fear"),
        ("This is the best day ever!", "Extreme joy"),
        ("I'm feeling really overwhelmed right now", "Stress/overwhelm"),
        ("Can we talk about something else?", "Avoidance/discomfort"),
        ("I suppose it doesn't matter anyway", "Resignation/defeat"),
        ("I'm actually really excited about this!", "Genuine enthusiasm"),
        ("I'm not sure how I feel about that", "Uncertainty/ambivalence")
    ]
    
    for text, description in test_cases:
        print(f"\n📋 Test Case: {description}")
        print(f"📝 Text: \"{text}\"")
        
        result = classify_query(text)
        
        print(f"🎭 Primary Emotion: {result['emotion'].upper()} ({result['confidence']:.1%})")
        print(f"🔧 Recommended Tool: {result['tool']}")
        
        if result.get('psychological_insights'):
            print(f"🧠 Psychology: {result['psychological_insights'][0]}")
        
        if result.get('emotional_nuance', {}).get('mixed_emotions'):
            print("⚡ Mixed emotions detected!")
        
        if result.get('emotional_nuance', {}).get('emotional_intensity', 0) > 0.5:
            intensity = result['emotional_nuance']['emotional_intensity']
            print(f"💥 High emotional intensity: {intensity:.1%}")
        
        # Show top 3 emotions
        percentages = result.get('percentages', {})
        if len(percentages) > 1:
            sorted_emotions = sorted(percentages.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"📊 Top emotions: {', '.join([f'{emotion}: {pct:.1%}' for emotion, pct in sorted_emotions])}")
        
        print("-" * 60)

def test_psychological_patterns():
    """Test specific psychological patterns."""
    
    print("\n\n🔍 Psychological Pattern Analysis")
    print("=" * 60)
    
    pattern_tests = [
        ("Short responses", ["ok", "fine", "whatever", "sure", "yes", "no"]),
        ("Very short", ["...", "k", ".", "?", "!", "hm"]),
        ("High intensity", ["absolutely amazing!!!", "TOTALLY INCREDIBLE", "so so happy"]),
        ("Mixed case", ["WhAt Is ThIs", "oKaY tHeN", "SuRe WhY nOt"]),
        ("Repetitive", ["no no no", "why why why", "please please please"]),
        ("Question patterns", ["what do you mean?", "why would you say that?", "how could this happen?"]),
        ("Temporal focus", ["I remember when...", "I can't wait for...", "Right now I feel..."]),
        ("Self-reference", ["I think I might be...", "I'm feeling...", "I don't know if I can..."])
    ]
    
    for pattern_name, texts in pattern_tests:
        print(f"\n🎯 Testing: {pattern_name}")
        for text in texts:
            result = classify_query(text)
            print(f"  '{text}' → {result['emotion']} ({result['confidence']:.0%})")
            if result.get('psychological_insights'):
                print(f"    💡 {result['psychological_insights'][0]}")

if __name__ == "__main__":
    test_advanced_classifier()
    test_psychological_patterns()
    
    print("\n✅ Advanced classifier testing complete!")
    print("The classifier now understands:")
    print("  • Psychological context and message length")
    print("  • Mixed emotions and emotional complexity") 
    print("  • Behavioral patterns and communication styles")
    print("  • Emotional subtext and hidden meanings")
    print("  • Intensity levels and genuine vs. surface emotions")