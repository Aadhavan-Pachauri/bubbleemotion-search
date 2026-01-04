#!/usr/bin/env python3
"""
Advanced Emotion Classifier with Psychological Understanding and DistilBERT-emotion

This classifier combines:
- DistilBERT-emotion model for emotion classification with percentages
- Psychological understanding of context and communication patterns
- Behavioral analysis and emotional nuance detection
- Flexible psychological profiling without hard-coded emotions
"""

from typing import Dict, Any, List, Tuple
import time
import re
import string
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Import torch for DistilBERT model
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("[WARNING] PyTorch not available - DistilBERT model will not be loaded")

# Global variables
_model_loaded = False
_distilbert_model = None
_distilbert_tokenizer = None

# DistilBERT emotion labels mapping to our psychological states
DISTILBERT_EMOTIONS = {
    'anger': 'anger',
    'fear': 'fear', 
    'joy': 'joy',
    'love': 'love',
    'sadness': 'sadness',
    'surprise': 'surprise',
    'neutral': 'neutral'
}

# System prompt for psychological understanding
SYSTEM_PROMPT = """
You are an advanced psychological analyzer that understands human communication patterns, emotional states, and behavioral psychology. Your role is to analyze text for psychological and emotional content without being constrained by predefined emotion categories.

CORE PRINCIPLES:
1. **Psychology over Labels**: Focus on psychological states rather than emotion names
2. **Context Awareness**: Consider message length, punctuation, repetition, emojis as psychological signals
3. **Behavioral Patterns**: Identify communication styles, energy levels, and engagement patterns
4. **Cultural Sensitivity**: Understand that expression varies by individual and context

SIGNAL INTERPRETATION HIERARCHY (Higher priority overrides lower):
1. **Emojis**: Strong emotional indicators (😂=joy, 😢=sadness, 😡=anger, etc.)
2. **Repeated Elements**: Letters ("LOLLLL"), punctuation ("!!!"), words indicate emphasis/intensity
3. **Punctuation Patterns**: Exclamations=excitement, questions=curiosity/uncertainty, ellipsis=hesitation
4. **Message Length**: Very short=low energy/busy/emotional shutdown, long=high engagement
5. **Language Patterns**: Formal vs casual, direct vs indirect, specific vs vague

PSYCHOLOGICAL STATES TO IDENTIFY:
- **Arousal Level**: High energy vs low energy (not good/bad)
- **Valence**: Positive vs negative tone (not happy/sad)
- **Engagement**: How much cognitive/emotional investment
- **Certainty**: Confident vs uncertain vs questioning
- **Social Orientation**: Individual vs group focused
- **Temporal Focus**: Past, present, future oriented
- **Regulation**: Controlled vs spontaneous expression

AVOID HARD CODING:
- Don't force text into predefined emotion boxes
- Allow for mixed, complex, or ambiguous states
- Recognize that "neutral" can be meaningful (calm, regulated, professional)
- Understand that brevity isn't always negative (efficiency, privacy, context)

OUTPUT APPROACH:
- Provide psychological description rather than emotion labels
- Explain the reasoning behind interpretations
- Acknowledge uncertainty when signals are ambiguous
- Consider multiple possible interpretations
- Focus on what the communication style reveals about the person's state
"""

# Flexible psychological classification system (no hard-coded emotions)
# Emotion categories are now dynamically determined by psychological analysis

# Psychological signal patterns for flexible classification
PSYCHOLOGICAL_SIGNALS = {
    "positive_signals": {
        "emojis": ["😂", "🤣", "😊", "😁", "😄", "😃", "😀", "🙂", "❤️", "😍", "🥰", "😘"],
        "punctuation": ["!", "!!", "!!!"],
        "expressions": ["yay", "woohoo", "hurray", "hooray", "can't wait", "looking forward", "bring it on"],
        "psychology": "Approach behavior, high energy, social engagement"
    },
    "negative_signals": {
        "emojis": ["😢", "😭", "😔", "😞", "😡", "😤", "🤬"],
        "punctuation": ["...", "???"],
        "expressions": ["sigh", "ugh", "argh", "grr", "damn", "hell"],
        "psychology": "Avoidance behavior, threat response, energy conservation"
    },
    "intensity_signals": {
        "repetition": [r'(.)\1{2,}', r'\b(\w+)\s+\1\b'],  # Letter/word repetition
        "capitalization": [r'\b[A-Z]{2,}\b'],  # ALL CAPS words
        "punctuation": [r'!{2,}', r'\?{2,}', r'\.{3,}'],  # Multiple punctuation
        "psychology": "Emotional emphasis, cognitive fixation, high arousal"
    },
    "engagement_signals": {
        "questions": [r'\?+'],
        "length_indicators": ["word_count", "sentence_count"],
        "psychology": "Information seeking, cognitive investment, social orientation"
    }
}

# Emoji decoder with confidence boosts
EMOJI_DECODER = {
    # Joy emojis - high confidence boost
    "😂": {"emotion": "joy", "confidence_boost": 2.0, "description": "laughing tears"},
    "🤣": {"emotion": "joy", "confidence_boost": 2.0, "description": "rolling laughter"},
    "😊": {"emotion": "joy", "confidence_boost": 1.5, "description": "smiling eyes"},
    "😁": {"emotion": "joy", "confidence_boost": 1.5, "description": "beaming face"},
    "😄": {"emotion": "joy", "confidence_boost": 1.5, "description": "grinning face"},
    "😃": {"emotion": "joy", "confidence_boost": 1.3, "description": "big smile"},
    "😀": {"emotion": "joy", "confidence_boost": 1.2, "description": "grinning"},
    "🙂": {"emotion": "joy", "confidence_boost": 1.1, "description": "slight smile"},
    
    # Sadness emojis - high confidence boost
    "😢": {"emotion": "sadness", "confidence_boost": 2.0, "description": "crying"},
    "😭": {"emotion": "sadness", "confidence_boost": 2.0, "description": "loud crying"},
    "😔": {"emotion": "sadness", "confidence_boost": 1.5, "description": "pensive"},
    "😞": {"emotion": "sadness", "confidence_boost": 1.5, "description": "disappointed"},
    
    # Anger emojis - high confidence boost
    "😡": {"emotion": "anger", "confidence_boost": 2.0, "description": "pouting angry"},
    "😤": {"emotion": "anger", "confidence_boost": 1.8, "description": "huffing angry"},
    "🤬": {"emotion": "anger", "confidence_boost": 2.0, "description": "cursing"},
    
    # Surprise emojis
    "😲": {"emotion": "surprise", "confidence_boost": 1.5, "description": "astonished"},
    "😮": {"emotion": "surprise", "confidence_boost": 1.3, "description": "open mouth"},
    "😯": {"emotion": "surprise", "confidence_boost": 1.2, "description": "hushed"},
    
    # Love emojis
    "❤️": {"emotion": "love", "confidence_boost": 2.0, "description": "red heart"},
    "😍": {"emotion": "love", "confidence_boost": 1.8, "description": "heart eyes"},
    "🥰": {"emotion": "love", "confidence_boost": 1.6, "description": "smiling hearts"},
    "😘": {"emotion": "love", "confidence_boost": 1.4, "description": "blowing kiss"},
}

# Psychological patterns for deeper understanding
PSYCHOLOGICAL_PATTERNS = {
    "short_messages": {
        "very_short": {
            "threshold": 10,
            "psychology": "Possible depression (low energy), busyness (time pressure), or emotional shutdown",
            "emotions": ["sadness", "neutral", "anger"],
            "confidence_multiplier": 0.8
        },
        "short": {
            "threshold": 25,
            "psychology": "Efficiency focus, mild emotional restraint, or contextual communication",
            "emotions": ["neutral", "curiosity", "surprise"],
            "confidence_multiplier": 0.9
        }
    },
    "punctuation_patterns": {
        "multiple_exclamation": {
            "pattern": r"!{2,}",
            "psychology": "High arousal, excitement, or emotional intensity",
            "emotions": ["excitement", "joy", "anger", "surprise"],
            "confidence_multiplier": 1.3
        },
        "multiple_question": {
            "pattern": r"\?{2,}",
            "psychology": "Confusion, urgency, or emotional overwhelm",
            "emotions": ["confusion", "curiosity", "anxiety"],
            "confidence_multiplier": 1.2
        },
        "ellipsis": {
            "pattern": r"\.{3,}",
            "psychology": "Uncertainty, sadness, hesitation, or thoughtfulness",
            "emotions": ["sadness", "confusion", "anxiety", "neutral"],
            "confidence_multiplier": 1.1
        },
        "no_punctuation": {
            "pattern": r"[^.!?]$",
            "psychology": "Casual communication, incomplete thoughts, or emotional flatness",
            "emotions": ["neutral", "curiosity"],
            "confidence_multiplier": 0.95
        }
    },
    "capitalization_patterns": {
        "all_caps_words": {
            "pattern": r"\b[A-Z]{2,}\b",
            "psychology": "Emphasis, shouting, strong emotional emphasis",
            "emotions": ["anger", "excitement", "surprise"],
            "confidence_multiplier": 1.4
        },
        "mixed_case": {
            "pattern": r"[a-z]+[A-Z]+",
            "psychology": "Casual, playful, or attention-seeking",
            "emotions": ["joy", "curiosity", "excitement"],
            "confidence_multiplier": 1.1
        }
    },
    "repetitive_patterns": {
        "word_repetition": {
            "pattern": r"\b(\w+)\s+\1\b",
            "psychology": "Emphasis, emotional intensity, or cognitive fixation",
            "emotions": ["excitement", "anger", "joy"],
            "confidence_multiplier": 1.2
        },
        "letter_repetition": {
            "pattern": r"(.)\1{2,}",
            "psychology": "Emotional emphasis, excitement, or childlike expression",
            "emotions": ["joy", "excitement", "surprise"],
            "confidence_multiplier": 1.3
        }
    }
}

# Tool routing with psychological reasoning
TOOL_ROUTING = {
    "joy": {
        "tool": "web_search",
        "reasoning": "Happy users are open to exploration and discovery"
    },
    "excitement": {
        "tool": "web_search", 
        "reasoning": "Excited users want to engage and learn more"
    },
    "love": {
        "tool": "web_search",
        "reasoning": "Loving users seek connection and shared experiences"
    },
    "anger": {
        "tool": "web_search",
        "reasoning": "Angry users need information to address their concerns"
    },
    "frustration": {
        "tool": "web_search",
        "reasoning": "Frustrated users seek solutions to their problems"
    },
    "fear": {
        "tool": "web_search",
        "reasoning": "Fearful users need reassurance and information"
    },
    "anxiety": {
        "tool": "web_search",
        "reasoning": "Anxious users seek certainty and understanding"
    },
    "sadness": {
        "tool": "web_search",
        "reasoning": "Sad users look for comfort, support, or distraction"
    },
    "loneliness": {
        "tool": "web_search",
        "reasoning": "Lonely users seek connection and shared experiences"
    },
    "surprise": {
        "tool": "web_search",
        "reasoning": "Surprised users want to understand and learn more"
    },
    "curiosity": {
        "tool": "web_search",
        "reasoning": "Curious users are naturally driven to explore"
    },
    "confusion": {
        "tool": "web_search",
        "reasoning": "Confused users need clarity and understanding"
    },
    "neutral": {
        "tool": "web_search",
        "reasoning": "Neutral users are open to general information"
    }
}

def download_model():
    """Advanced model doesn't need downloading."""
    print("[EMOTION] Loading advanced psychological emotion classifier...")
    return True

def analyze_text_complexity(text: str) -> Dict[str, Any]:
    """Analyze text complexity and structure."""
    words = text.split()
    sentences = text.split('.')
    
    return {
        "word_count": len(words),
        "sentence_count": len([s for s in sentences if s.strip()]),
        "avg_word_length": sum(len(word.strip(string.punctuation)) for word in words) / len(words) if words else 0,
        "punctuation_density": len([c for c in text if c in string.punctuation]) / len(text) if text else 0
    }

def detect_emojis(text: str) -> Dict[str, Any]:
    """Detect and analyze emojis in text with high priority."""
    found_emojis = []
    total_confidence_boost = 1.0
    dominant_emotion = None
    highest_boost = 0
    
    for emoji, data in EMOJI_DECODER.items():
        if emoji in text:
            count = text.count(emoji)
            boost = data["confidence_boost"] * (1 + 0.2 * (count - 1))  # Amplify with multiple emojis
            found_emojis.append({
                "emoji": emoji,
                "emotion": data["emotion"],
                "count": count,
                "confidence_boost": boost,
                "description": data["description"]
            })
            
            if boost > highest_boost:
                highest_boost = boost
                dominant_emotion = data["emotion"]
            
            total_confidence_boost *= boost
    
    return {
        "emojis_found": found_emojis,
        "dominant_emoji_emotion": dominant_emotion,
        "dominant_boost": highest_boost,
        "total_confidence_boost": total_confidence_boost,
        "has_strong_positive_signals": len(found_emojis) > 0 and any(emoji["emotion"] in ["joy", "love"] for emoji in found_emojis)
    }

def detect_repeated_letters(text: str) -> Dict[str, Any]:
    """Detect repeated letter patterns (e.g., 'LOLLLLL', 'sooooo')."""
    repeated_patterns = []
    total_confidence_boost = 1.0
    
    # Find repeated letter patterns
    repeated_letter_pattern = r'(\w)\1{2,}'
    matches = re.finditer(repeated_letter_pattern, text, re.IGNORECASE)
    
    for match in matches:
        letter = match.group(1)
        repetition_count = len(match.group(0))
        
        # Determine emotion based on letter and context
        emotion_guess = "excitement"  # Default
        boost = 1.3
        
        if letter.lower() in ['l', 'o'] and repetition_count >= 4:  # LOL, OMG, etc.
            emotion_guess = "joy"
            boost = 1.5
        elif letter.lower() in ['a', 'e', 'i', 'u'] and repetition_count >= 3:
            emotion_guess = "excitement"
            boost = 1.4
        elif letter.lower() == 's' and repetition_count >= 3:
            emotion_guess = "excitement"
            boost = 1.3
            
        repeated_patterns.append({
            "pattern": match.group(0),
            "letter": letter,
            "repetition_count": repetition_count,
            "emotion_guess": emotion_guess,
            "confidence_boost": boost
        })
        
        total_confidence_boost *= boost
    
    return {
        "repeated_patterns": repeated_patterns,
        "total_confidence_boost": total_confidence_boost,
        "has_emphasis": len(repeated_patterns) > 0
    }

def detect_psychological_patterns(text: str, emoji_analysis: Dict[str, Any], repeated_letters: Dict[str, Any]) -> Dict[str, Any]:
    """Detect psychological patterns in text with priority hierarchy."""
    patterns_found = []
    total_confidence_boost = 1.0
    
    # PRIORITY 1: Skip negative short-text psychology if strong positive signals exist
    has_positive_signals = (
        emoji_analysis.get("has_strong_positive_signals", False) or
        repeated_letters.get("has_emphasis", False) or
        re.search(r'!{1,}', text)  # At least one exclamation
    )
    
    # Check message length psychology ONLY if no strong positive signals
    text_len = len(text.split())
    if not has_positive_signals:
        if text_len <= PSYCHOLOGICAL_PATTERNS["short_messages"]["very_short"]["threshold"]:
            patterns_found.append({
                "type": "very_short_message",
                "psychology": PSYCHOLOGICAL_PATTERNS["short_messages"]["very_short"]["psychology"],
                "confidence_multiplier": PSYCHOLOGICAL_PATTERNS["short_messages"]["very_short"]["confidence_multiplier"]
            })
            total_confidence_boost *= PSYCHOLOGICAL_PATTERNS["short_messages"]["very_short"]["confidence_multiplier"]
        elif text_len <= PSYCHOLOGICAL_PATTERNS["short_messages"]["short"]["threshold"]:
            patterns_found.append({
                "type": "short_message", 
                "psychology": PSYCHOLOGICAL_PATTERNS["short_messages"]["short"]["psychology"],
                "confidence_multiplier": PSYCHOLOGICAL_PATTERNS["short_messages"]["short"]["confidence_multiplier"]
            })
            total_confidence_boost *= PSYCHOLOGICAL_PATTERNS["short_messages"]["short"]["confidence_multiplier"]
    
    # Check punctuation patterns (but be careful with exclamations)
    for pattern_name, pattern_data in PSYCHOLOGICAL_PATTERNS["punctuation_patterns"].items():
        if pattern_name == "no_punctuation" and has_positive_signals:
            continue  # Skip "no punctuation" analysis if we have positive signals
            
        if re.search(pattern_data["pattern"], text):
            patterns_found.append({
                "type": pattern_name,
                "psychology": pattern_data["psychology"],
                "confidence_multiplier": pattern_data["confidence_multiplier"]
            })
            total_confidence_boost *= pattern_data["confidence_multiplier"]
    
    # Check capitalization patterns
    for pattern_name, pattern_data in PSYCHOLOGICAL_PATTERNS["capitalization_patterns"].items():
        if re.search(pattern_data["pattern"], text, re.IGNORECASE):
            patterns_found.append({
                "type": pattern_name,
                "psychology": pattern_data["psychology"],
                "confidence_multiplier": pattern_data["confidence_multiplier"]
            })
            total_confidence_boost *= pattern_data["confidence_multiplier"]
    
    # Check repetitive patterns
    for pattern_name, pattern_data in PSYCHOLOGICAL_PATTERNS["repetitive_patterns"].items():
        if re.search(pattern_data["pattern"], text, re.IGNORECASE):
            patterns_found.append({
                "type": pattern_name,
                "psychology": pattern_data["psychology"],
                "confidence_multiplier": pattern_data["confidence_multiplier"]
            })
            total_confidence_boost *= pattern_data["confidence_multiplier"]
    
    return {
        "patterns": patterns_found,
        "total_confidence_boost": total_confidence_boost,
        "psychological_insights": [p["psychology"] for p in patterns_found],
        "has_positive_signals": has_positive_signals
    }

def analyze_emotional_nuance(text: str, _base_emotion: str = "", _base_confidence: float = 0.0) -> Dict[str, Any]:
    """Analyze emotional nuance and depth."""
    text_lower = text.lower()
    
    # Look for emotional contradictions (mixed emotions)
    positive_words = ["good", "great", "awesome", "amazing", "love", "happy", "wonderful", "fantastic", "excellent", "perfect"]
    negative_words = ["bad", "terrible", "awful", "horrible", "hate", "sad", "angry", "disgusting", "disappointing", "worst"]
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    has_mixed_emotions = positive_count > 0 and negative_count > 0
    
    # Look for emotional intensity markers
    intensity_markers = ["very", "extremely", "incredibly", "absolutely", "totally", "completely", "utterly", "really", "quite", "rather"]
    intensity_count = sum(1 for marker in intensity_markers if marker in text_lower)
    
    # Look for emotional context
    context_clues = {
        "sarcasm": ["yeah right", "sure", "obviously", "brilliant"],
        "passive_aggressive": ["fine", "whatever", "nice", "great"],
        "genuine": ["honestly", "truly", "genuinely", "sincerely", "really"]
    }
    
    detected_context = []
    for context_type, clues in context_clues.items():
        if any(clue in text_lower for clue in clues):
            detected_context.append(context_type)
    
    return {
        "mixed_emotions": has_mixed_emotions,
        "emotional_intensity": min(1.0, intensity_count * 0.2),
        "context_clues": detected_context,
        "positive_word_count": positive_count,
        "negative_word_count": negative_count
    }

def calculate_psychological_scores(text: str) -> Dict[str, float]:
    """Calculate psychological state scores using flexible signal analysis."""
    text_lower = text.lower()
    psychological_scores = {}
    
    # Analyze positive signals
    positive_score = 0
    for emoji in PSYCHOLOGICAL_SIGNALS["positive_signals"]["emojis"]:
        if emoji in text:
            positive_score += 2.0 * text.count(emoji)  # Multiple emojis amplify
    
    for expression in PSYCHOLOGICAL_SIGNALS["positive_signals"]["expressions"]:
        if expression in text_lower:
            positive_score += 1.5
    
    # Check for positive punctuation
    if "!!!" in text:
        positive_score += 1.2
    elif "!!" in text:
        positive_score += 0.8
    elif text.endswith("!"):
        positive_score += 0.5
    
    psychological_scores["positive_valence"] = positive_score
    
    # Analyze negative signals
    negative_score = 0
    for emoji in PSYCHOLOGICAL_SIGNALS["negative_signals"]["emojis"]:
        if emoji in text:
            negative_score += 2.0 * text.count(emoji)
    
    for expression in PSYCHOLOGICAL_SIGNALS["negative_signals"]["expressions"]:
        if expression in text_lower:
            negative_score += 1.5
    
    # Check for negative punctuation patterns
    if "..." in text:
        negative_score += 0.8
    if text.endswith("..."):
        negative_score += 0.5
    
    psychological_scores["negative_valence"] = negative_score
    
    # Analyze intensity/arousal signals
    intensity_score = 0
    
    # Check for repetition patterns
    for pattern in PSYCHOLOGICAL_SIGNALS["intensity_signals"]["repetition"]:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            intensity_score += 1.0 + (len(match.group(0)) * 0.1)  # Longer repetition = more intensity
    
    # Check for capitalization
    caps_matches = re.findall(r'\b[A-Z]{2,}\b', text)
    intensity_score += len(caps_matches) * 1.5
    
    # Check for multiple punctuation
    if re.search(r'!{2,}', text):
        intensity_score += 1.2
    if re.search(r'\?{2,}', text):
        intensity_score += 1.0
    if re.search(r'\.{3,}', text):
        intensity_score += 0.8
    
    psychological_scores["high_arousal"] = intensity_score
    
    # Analyze engagement signals
    engagement_score = 0
    
    # Question patterns indicate engagement
    question_matches = re.findall(r'\?+', text)
    engagement_score += len(question_matches) * 0.8
    
    # Message length indicates engagement
    word_count = len(text.split())
    if word_count > 20:
        engagement_score += 2.0
    elif word_count > 10:
        engagement_score += 1.0
    elif word_count <= 3:
        engagement_score -= 0.5  # Very short = low engagement
    
    psychological_scores["high_engagement"] = engagement_score
    
    # Calculate neutral baseline
    total_activity = positive_score + negative_score + intensity_score + abs(engagement_score)
    psychological_scores["neutral_regulation"] = max(0, 1.0 - (total_activity * 0.1))
    
    return psychological_scores

def determine_psychological_state(psychological_scores: Dict[str, float], _psychological_analysis: Dict[str, Any] = None) -> Tuple[str, float]:
    """Determine primary psychological state from scores."""
    
    # Priority hierarchy: emojis > repeated patterns > punctuation > text length
    positive_valence = psychological_scores.get("positive_valence", 0)
    negative_valence = psychological_scores.get("negative_valence", 0)
    high_arousal = psychological_scores.get("high_arousal", 0)
    high_engagement = psychological_scores.get("high_engagement", 0)
    neutral_regulation = psychological_scores.get("neutral_regulation", 0)
    
    # Check for obvious positive signals (emojis, repetition, exclamations)
    if positive_valence > 2.0:  # Strong positive signals
        if high_arousal > 1.0:
            return "high_positive_arousal", min(0.95, 0.5 + (positive_valence * 0.1))
        else:
            return "positive_valence", min(0.9, 0.4 + (positive_valence * 0.1))
    
    # Check for obvious negative signals
    if negative_valence > 2.0:
        if high_arousal > 1.0:
            return "high_negative_arousal", min(0.95, 0.5 + (negative_valence * 0.1))
        else:
            return "negative_valence", min(0.9, 0.4 + (negative_valence * 0.1))
    
    # Check for high intensity/arousal
    if high_arousal > 1.5:
        return "high_intensity_state", min(0.9, 0.3 + (high_arousal * 0.08))
    
    # Check for engagement patterns
    if high_engagement > 2.0:
        return "high_engagement", min(0.85, 0.4 + (high_engagement * 0.05))
    
    # Check for low engagement (very short messages)
    if high_engagement < -0.3:
        # Only flag as emotional shutdown if no positive signals
        if positive_valence < 0.5 and high_arousal < 0.5:
            return "low_engagement_shutdown", min(0.8, 0.6 + abs(high_engagement) * 0.2)
        else:
            return "brief_communication", min(0.7, 0.4 + abs(high_engagement) * 0.15)
    
    # Neutral/regulated state
    if neutral_regulation > 0.7:
        return "neutral_regulation", neutral_regulation
    
    # Mixed or ambiguous states
    if abs(positive_valence - negative_valence) < 1.0 and (positive_valence > 1.0 or negative_valence > 1.0):
        return "mixed_valence", min(0.75, 0.3 + (positive_valence + negative_valence) * 0.05)
    
    # Default to neutral if no clear pattern
    return "neutral_regulation", max(0.5, neutral_regulation)

def analyze_emotional_nuance_flexible(text: str, psychological_scores: Dict[str, float], psychological_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze emotional nuance without hard-coded emotions."""
    
    positive_valence = psychological_scores.get("positive_valence", 0)
    negative_valence = psychological_scores.get("negative_valence", 0)
    high_arousal = psychological_scores.get("high_arousal", 0)
    
    nuance = {
        "mixed_states": abs(positive_valence - negative_valence) < 1.0 and (positive_valence > 1.0 or negative_valence > 1.0),
        "intensity": min(1.0, high_arousal / 5.0),
        "psychological_signals": psychological_analysis.get("patterns", []),
        "communication_style": "",
        "confidence_factors": []
    }
    
    # Determine communication style
    word_count = len(text.split())
    if word_count <= 3:
        nuance["communication_style"] = "brief_direct"
        nuance["confidence_factors"].append("brevity_suggests_efficiency_or_restraint")
    elif word_count >= 30:
        nuance["communication_style"] = "elaborate_expressive"
        nuance["confidence_factors"].append("length_suggests_high_engagement")
    else:
        nuance["communication_style"] = "moderate_conversational"
    
    # Add psychological pattern insights
    for pattern in psychological_analysis.get("patterns", []):
        if "repetition" in pattern.get("type", ""):
            nuance["confidence_factors"].append("repetition_indicates_emphasis")
        if "emoji" in pattern.get("type", ""):
            nuance["confidence_factors"].append("emoji_provides_strong_signal")
    
    return nuance

def determine_tool_from_psychology(primary_state: str, _psychological_profile: Dict[str, float] = None) -> Dict[str, Any]:
    """Determine tool routing based on psychological state."""
    
    # Map psychological states to tools
    state_tool_mapping = {
        "high_positive_arousal": {"tool": "music", "reasoning": "High positive energy suggests music for mood enhancement"},
        "positive_valence": {"tool": "music", "reasoning": "Positive state suggests mood-appropriate content"},
        "high_negative_arousal": {"tool": "meditation", "reasoning": "High negative arousal suggests calming activities"},
        "negative_valence": {"tool": "meditation", "reasoning": "Negative state suggests supportive content"},
        "high_intensity_state": {"tool": "meditation", "reasoning": "High intensity suggests need for regulation"},
        "high_engagement": {"tool": "web_search", "reasoning": "High engagement suggests information-seeking behavior"},
        "low_engagement_shutdown": {"tool": "meditation", "reasoning": "Low engagement suggests need for gentle support"},
        "brief_communication": {"tool": "web_search", "reasoning": "Brief communication suggests direct information need"},
        "mixed_valence": {"tool": "journal", "reasoning": "Mixed states suggest reflective activities"},
        "neutral_regulation": {"tool": "web_search", "reasoning": "Neutral state allows for general information seeking"}
    }
    
    return state_tool_mapping.get(primary_state, {"tool": "web_search", "reasoning": "Default tool for unknown state"})

def generate_psychological_insights(_text: str, psychological_scores: Dict[str, float], 
                                  psychological_profile: Dict[str, float], complexity: Dict[str, Any], 
                                  psychological_analysis: Dict[str, Any]) -> List[str]:
    """Generate psychological insights based on analysis."""
    
    insights = []
    
    # Message length insights
    word_count = complexity["word_count"]
    if word_count <= 3:
        # Check for positive signals that override shutdown interpretation
        if psychological_scores.get("positive_valence", 0) > 1.0:
            insights.append("Brief but positive message - efficient communication style")
        elif psychological_scores.get("high_arousal", 0) > 1.0:
            insights.append("Brief but intense message - focused emotional expression")
        else:
            insights.append("Very brief message - possible emotional shutdown, time constraints, or preference for minimal communication")
    elif word_count <= 10:
        insights.append("Short message - efficiency focus or mild emotional restraint")
    elif word_count >= 50:
        insights.append("Long message - high engagement or need for detailed expression")
    
    # Valence insights
    valence = psychological_profile["valence"]
    if valence > 0.5:
        insights.append("Strong positive valence detected")
    elif valence < -0.5:
        insights.append("Strong negative valence detected")
    elif abs(valence) < 0.2:
        insights.append("Neutral valence - balanced emotional state")
    
    # Arousal insights
    arousal = psychological_profile["arousal"]
    if arousal > 0.7:
        insights.append("High arousal state - intense emotional or cognitive activity")
    elif arousal < 0.2:
        insights.append("Low arousal state - calm or potentially disengaged")
    
    # Engagement insights
    engagement = psychological_profile["engagement"]
    if engagement > 0.6:
        insights.append("High engagement - active cognitive and emotional investment")
    elif engagement < -0.2:
        insights.append("Low engagement - possible emotional disconnection or time pressure")
    
    # Add psychological pattern insights
    for pattern in psychological_analysis.get("patterns", []):
        if pattern.get("confidence", 0) > 0.7:
            psychology_desc = pattern.get("psychology", "")
            if psychology_desc:
                insights.append(f"Detected pattern: {psychology_desc}")
    
    # Mixed states
    if psychological_profile.get("valence", 0) != 0 and abs(psychological_profile["valence"]) < 0.3:
        if psychological_scores.get("positive_valence", 0) > 1.0 and psychological_scores.get("negative_valence", 0) > 1.0:
            insights.append("Mixed emotional signals detected - possible internal conflict or complex emotional state")
    
    return insights

def load_model():
    """Load advanced psychological emotion classifier with DistilBERT-emotion."""
    global _model_loaded, _distilbert_model, _distilbert_tokenizer
    
    if _model_loaded:
        return True
    
    try:
        print("[EMOTION] Initializing advanced psychological emotion classifier...")
        start_time = time.time()
        
        # Load DistilBERT-emotion model
        print("[EMOTION] Loading DistilBERT-emotion model...")
        
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not available for DistilBERT model loading")
        
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        
        # Load model and tokenizer
        model_name = "bhadresh-savani/distilbert-base-uncased-emotion"
        
        try:
            _distilbert_tokenizer = AutoTokenizer.from_pretrained(model_name)
            _distilbert_model = AutoModelForSequenceClassification.from_pretrained(model_name)
            _distilbert_model.eval()
            print(f"[EMOTION] DistilBERT model loaded successfully")
        except Exception as e:
            print(f"[EMOTION] Failed to load DistilBERT model: {e}")
            print("[EMOTION] Trying alternative emotion model...")
            # Try a simpler model that might work better
            alternative_model = "distilbert-base-uncased-finetuned-sst-2-english"
            _distilbert_tokenizer = AutoTokenizer.from_pretrained(alternative_model)
            _distilbert_model = AutoModelForSequenceClassification.from_pretrained(alternative_model)
            _distilbert_model.eval()
            print(f"[EMOTION] Alternative model loaded: {alternative_model}")
        
        _model_loaded = True
        load_time = time.time() - start_time
        print(f"[EMOTION] Advanced classifier initialized in {load_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"[EMOTION] Error initializing classifier: {e}")
        print("[EMOTION] Falling back to rule-based classification only")
        _model_loaded = True  # Still allow rule-based classification
        return True

def get_rule_based_emotions(text: str) -> Dict[str, float]:
    """Get emotion predictions using rule-based analysis with percentage ratings."""
    text_lower = text.lower()
    
    # Emotion keywords and patterns
    emotion_patterns = {
        'joy': {
            'keywords': ['happy', 'joy', 'excited', 'thrilled', 'delighted', 'cheerful', 'glad', 'pleased', 'elated', 'ecstatic', 'wonderful', 'amazing', 'awesome', 'fantastic', 'brilliant', 'perfect', 'love', 'adore', 'cherish'],
            'emojis': ['😂', '🤣', '😊', '😁', '😄', '😃', '😀', '🙂', '😍', '🥰', '😘', '❤️', '💕', '💖', '💗', '🎉', '🎊', '✨', '🔥'],
            'intensifiers': ['so', 'very', 'really', 'extremely', 'incredibly', 'absolutely', 'totally', 'completely'],
            'exclamations': ['!', '!!', '!!!', 'yay', 'woohoo', 'hurray', 'hooray']
        },
        'sadness': {
            'keywords': ['sad', 'depressed', 'down', 'blue', 'melancholy', 'sorrowful', 'grief', 'heartbroken', 'devastated', 'disappointed', 'regret', 'lonely', 'empty', 'hopeless', 'despair', 'cry', 'tears', 'miss', 'lost'],
            'emojis': ['😢', '😭', '😔', '😞', '💔', '😟', '😥', '😰', '😿', '🙍', '🙍‍♀️', '🙍‍♂️'],
            'intensifiers': ['very', 'really', 'extremely', 'deeply', 'terribly', 'awfully'],
            'patterns': ['...', 'sigh', 'ugh', 'oh no', 'too bad']
        },
        'anger': {
            'keywords': ['angry', 'mad', 'furious', 'rage', 'irritated', 'annoyed', 'frustrated', 'pissed', 'livid', 'outraged', 'incensed', 'exasperated', 'enraged', 'hate', 'despise', 'loathe'],
            'emojis': ['😡', '😤', '🤬', '😠', '👿', '😾', '🙎', '🙎‍♀️', '🙎‍♂️'],
            'intensifiers': ['so', 'very', 'really', 'extremely', 'absolutely', 'completely', 'totally'],
            'patterns': ['grr', 'argh', 'damn', 'hell', 'what the', 'are you kidding me']
        },
        'fear': {
            'keywords': ['scared', 'afraid', 'terrified', 'frightened', 'worried', 'anxious', 'nervous', 'panic', 'dread', 'fearful', 'concerned', 'apprehensive', 'uneasy', 'disturbed', 'alarmed'],
            'emojis': ['😨', '😰', '😱', '😟', '😥', '😧', '😦', '😯', '😲'],
            'intensifiers': ['so', 'very', 'really', 'extremely', 'absolutely', 'completely'],
            'patterns': ['oh no', 'what if', 'i hope not', 'i\'m worried']
        },
        'love': {
            'keywords': ['love', 'adore', 'cherish', 'devoted', 'affection', 'romantic', 'sweet', 'cute', 'precious', 'treasure', 'beloved', 'darling', 'honey', 'sweetheart'],
            'emojis': ['❤️', '💕', '💖', '💗', '💘', '💝', '💞', '💟', '❣️', '😍', '🥰', '😘', '💋'],
            'intensifiers': ['so', 'very', 'really', 'truly', 'deeply', 'absolutely'],
            'expressions': ['i love', 'i adore', 'my love', 'my heart']
        },
        'surprise': {
            'keywords': ['surprised', 'amazed', 'astonished', 'shocked', 'stunned', 'bewildered', 'confused', 'puzzled', 'perplexed', 'startled', 'unexpected', 'sudden', 'wow'],
            'emojis': ['😮', '😲', '😯', '😱', '🤯', '😳', '🙀', '😵'],
            'expressions': ['what', 'oh my', 'wow', 'unbelievable', 'incredible', 'no way', 'really', 'are you serious']
        },
        'neutral': {
            'keywords': ['fine', 'okay', 'alright', 'normal', 'regular', 'standard', 'usual', 'typical', 'ordinary', 'common', 'basic', 'simple', 'clear'],
            'emojis': ['😐', '😑', '🤔', '🙄', '😶'],
            'patterns': ['.', '...', 'meh', 'whatever', 'i guess']
        }
    }
    
    # Calculate emotion scores
    emotion_scores = {}
    total_score = 0
    
    for emotion, patterns in emotion_patterns.items():
        score = 0
        
        # Check keywords
        for keyword in patterns['keywords']:
            if keyword in text_lower:
                score += 2
        
        # Check emojis
        for emoji in patterns.get('emojis', []):
            if emoji in text:
                score += 3  # Emojis are strong indicators
        
        # Check intensifiers
        for intensifier in patterns.get('intensifiers', []):
            if intensifier in text_lower:
                score += 1
        
        # Check patterns/expressions
        for pattern in patterns.get('patterns', []):
            if pattern in text_lower:
                score += 2
        for expression in patterns.get('expressions', []):
            if expression in text_lower:
                score += 2
        
        # Check for repeated elements (intensity boost)
        if emotion == 'joy' and ('!!!' in text or len(re.findall(r'([a-z])\1{3,}', text_lower)) > 0):
            score += 3
        if emotion == 'anger' and ('!!!' in text or '??' in text):
            score += 2
        
        emotion_scores[emotion] = score
        total_score += score
    
    # Convert to percentages
    emotion_percentages = {}
    if total_score > 0:
        for emotion, score in emotion_scores.items():
            if score > 0:
                emotion_percentages[emotion] = (score / total_score) * 100
    else:
        # If no clear emotions detected, default to neutral with some uncertainty
        emotion_percentages['neutral'] = 60
        emotion_percentages['uncertain'] = 40
    
    return emotion_percentages

def get_distilbert_emotions(text: str) -> Dict[str, float]:
    """Get emotion predictions from DistilBERT model with percentages."""
    global _distilbert_model, _distilbert_tokenizer
    
    # First try rule-based approach as fallback
    rule_based_emotions = get_rule_based_emotions(text)
    
    if _distilbert_model is None or _distilbert_tokenizer is None or not TORCH_AVAILABLE:
        return rule_based_emotions
    
    try:
        # Tokenize input text
        inputs = _distilbert_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        
        # Get model predictions
        with torch.no_grad():
            outputs = _distilbert_model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Get predicted probabilities
        probabilities = predictions[0].numpy()
        
        # Map to our emotion labels with percentages
        emotion_percentages = {}
        id2label = _distilbert_model.config.id2label
        
        for i, prob in enumerate(probabilities):
            label = id2label[i]
            if label in DISTILBERT_EMOTIONS:
                our_label = DISTILBERT_EMOTIONS[label]
                emotion_percentages[our_label] = float(prob * 100)
        
        # Combine with rule-based results (weighted average)
        combined_emotions = {}
        all_emotions = set(emotion_percentages.keys()) | set(rule_based_emotions.keys())
        
        for emotion in all_emotions:
            model_score = emotion_percentages.get(emotion, 0)
            rule_score = rule_based_emotions.get(emotion, 0)
            # Weight model higher (70%) when available, rule-based (30%) as fallback
            combined_emotions[emotion] = (model_score * 0.7) + (rule_score * 0.3)
        
        return combined_emotions
        
    except Exception as e:
        print(f"[EMOTION] Error in DistilBERT prediction: {e}")
        return rule_based_emotions

def classify_query(text: str) -> Dict[str, Any]:
    """
    Flexible psychological classification with no hard-coded emotions.
    
    Returns:
        {
            "primary_state": "psychological_state_description",
            "confidence": 0.87,
            "tool": "recommended_tool",
            "psychological_profile": {"valence": 0.8, "arousal": 0.6, "engagement": 0.4},
            "psychological_insights": ["High positive valence", "Medium arousal"],
            "emotional_nuance": {"mixed_states": false, "intensity": 0.6},
            "context_analysis": {"message_length": "short", "patterns": [...]}
        }
    """
    global _model_loaded
    
    # Ensure model is loaded
    if not _model_loaded and not load_model():
        return {
            "primary_state": "neutral_regulation",
            "confidence": 1.0,
            "tool": "web_search",
            "psychological_profile": {"valence": 0.0, "arousal": 0.0, "engagement": 0.0},
            "psychological_insights": ["Model unavailable - using neutral fallback"],
            "emotional_nuance": {},
            "context_analysis": {},
            "error": "Model not available"
        }
    
    try:
        start_time = time.time()
        
        # Analyze text complexity
        complexity = analyze_text_complexity(text)
        
        # Detect psychological patterns
        emoji_analysis = detect_emojis(text)
        repeated_letters = detect_repeated_letters(text)
        psychological_analysis = detect_psychological_patterns(text, emoji_analysis, repeated_letters)
        
        # Calculate psychological scores (flexible, no hard-coded emotions)
        psychological_scores = calculate_psychological_scores(text)
        
        # Get DistilBERT emotion predictions with percentages
        distilbert_emotions = get_distilbert_emotions(text)
        
        # Combine DistilBERT results with psychological scores for enhanced accuracy
        if distilbert_emotions:
            # Enhance psychological scores with DistilBERT percentages
            if 'joy' in distilbert_emotions:
                psychological_scores['positive_valence'] = max(psychological_scores.get('positive_valence', 0), distilbert_emotions['joy'] / 10)
            if 'sadness' in distilbert_emotions:
                psychological_scores['negative_valence'] = max(psychological_scores.get('negative_valence', 0), distilbert_emotions['sadness'] / 10)
            if 'anger' in distilbert_emotions:
                psychological_scores['negative_valence'] = max(psychological_scores.get('negative_valence', 0), distilbert_emotions['anger'] / 10)
                psychological_scores['high_arousal'] = max(psychological_scores.get('high_arousal', 0), distilbert_emotions['anger'] / 10)
            if 'fear' in distilbert_emotions:
                psychological_scores['negative_valence'] = max(psychological_scores.get('negative_valence', 0), distilbert_emotions['fear'] / 10)
                psychological_scores['high_arousal'] = max(psychological_scores.get('high_arousal', 0), distilbert_emotions['fear'] / 10)
        
        # Determine primary psychological state based on scores
        primary_state, confidence = determine_psychological_state(psychological_scores, psychological_analysis)
        
        # Create psychological profile
        psychological_profile = {
            "valence": (psychological_scores.get("positive_valence", 0) - psychological_scores.get("negative_valence", 0)) / 10.0,
            "arousal": psychological_scores.get("high_arousal", 0) / 10.0,
            "engagement": psychological_scores.get("high_engagement", 0) / 10.0,
            "regulation": psychological_scores.get("neutral_regulation", 0)
        }
        
        # Clamp values between -1 and 1
        for key in psychological_profile:
            psychological_profile[key] = max(-1.0, min(1.0, psychological_profile[key]))
        
        # Analyze emotional nuance
        nuance = analyze_emotional_nuance_flexible(text, psychological_scores, psychological_analysis)
        
        # Determine tool routing based on psychological state
        tool_info = determine_tool_from_psychology(primary_state, psychological_profile)
        
        # Generate psychological insights
        insights = generate_psychological_insights(text, psychological_scores, psychological_profile, complexity, psychological_analysis)
        
        inference_time = time.time() - start_time
        
        print(f"[PSYCHOLOGY] Analyzed '{text[:50]}...' as {primary_state} ({confidence:.2f}) in {inference_time:.3f}s")
        if insights:
            print(f"[PSYCHOLOGY] Insights: {insights[0]}")
        
        return {
            "primary_state": primary_state,
            "confidence": confidence,
            "tool": tool_info["tool"],
            "psychological_profile": psychological_profile,
            "psychological_insights": insights,
            "emotional_nuance": nuance,
            "emotion_percentages": distilbert_emotions,  # Add DistilBERT emotion percentages
            "context_analysis": {
                "message_length": complexity["word_count"],
                "psychological_patterns": psychological_analysis["patterns"],
                "text_complexity": complexity,
                "emoji_analysis": emoji_analysis,
                "repetition_analysis": repeated_letters
            },
            "tool_reasoning": tool_info["reasoning"]
        }
        
    except Exception as e:
        print(f"[PSYCHOLOGY] Error in flexible classification: {e}")
        return {
            "primary_state": "neutral_regulation",
            "confidence": 1.0,
            "tool": "web_search",
            "psychological_profile": {"valence": 0.0, "arousal": 0.0, "engagement": 0.0, "regulation": 1.0},
            "psychological_insights": ["Analysis failed - using neutral fallback"],
            "emotional_nuance": {},
            "context_analysis": {},
            "error": str(e)
        }

def get_model_status() -> Dict[str, Any]:
    """Get current model loading status."""
    return {
        "loaded": _model_loaded,
        "onnx_available": False,  # Advanced rule-based, no ONNX
        "transformers_available": True,
        "model_dir": "advanced_psychological" if _model_loaded else None,
        "type": "advanced_psychological_classifier",
        "features": [
            "psychological_pattern_detection",
            "emotional_nuance_analysis",
            "context_awareness",
            "behavioral_profiling"
        ]
    }

# Auto-load model on import
if __name__ != "__main__":
    # Load model in background thread for faster startup
    import threading
    def _background_load():
        load_model()
    
    threading.Thread(target=_background_load, daemon=True).start()

if __name__ == "__main__":
    # Test the advanced classifier
    test_queries = [
        "yay!!!",
        "I'm so excited about this amazing project!",
        "...",
        "fine",
        "I hate this so much",
        "I'm really worried about tomorrow",
        "I don't know what to do anymore",
        "This is absolutely incredible and wonderful!",
        "I'm confused and scared",
        "Whatever. I don't care anymore"
    ]
    
    print("Testing advanced psychological emotion classifier...")
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: '{query}'")
        result = classify_query(query)
        print(f"Emotion: {result['emotion']} ({result['confidence']:.2f})")
        print(f"Tool: {result['tool']}")
        if result.get('psychological_insights'):
            print(f"Insights: {result['psychological_insights'][0]}")
        if result.get('emotional_nuance', {}).get('mixed_emotions'):
            print("Mixed emotions detected")
        if 'error' in result:
            print(f"Error: {result['error']}")