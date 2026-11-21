from typing import Dict, Any, List

VERIFIED_CRISIS_RESOURCES: Dict[str, Dict[str, Any]] = {
    "us_canada_988": {
        "name": "Suicide & Crisis Lifeline",
        "region": "United States & Canada",
        "contact": "Call or Text 988",
        "availability": "24/7, Free & Confidential",
        "details": "Supports anyone experiencing mental health distress, suicidal thoughts, or substance use crisis."
    },
    "crisis_text_line": {
        "name": "Crisis Text Line",
        "region": "US, UK, Canada",
        "contact": "Text HOME to 741741 (US/Canada) or 85258 (UK)",
        "availability": "24/7, Free & Confidential",
        "details": "Connects you with a trained, compassionate volunteer crisis counselor over SMS."
    },
    "trevor_project": {
        "name": "The Trevor Project",
        "region": "United States (LGBTQ Youth)",
        "contact": "Call 1-866-488-7386 or Text START to 678-678",
        "availability": "24/7, Free & Confidential",
        "details": "Specialized crisis intervention and suicide prevention for LGBTQ young people."
    },
    "veterans_crisis_line": {
        "name": "Veterans Crisis Line",
        "region": "United States",
        "contact": "Dial 988, then press 1, or Text 838255",
        "availability": "24/7, Free & Confidential",
        "details": "Caring, qualified responders with the Department of Veterans Affairs."
    },
    "international_emergency": {
        "name": "International Emergency Services",
        "region": "Global",
        "contact": "Europe/India: 112 | UK: 999 | Australia: 000 | US/Canada: 911",
        "availability": "Immediate",
        "details": "For immediate physical danger or medical emergencies, contact your local emergency services directly."
    }
}

def format_crisis_intervention_response() -> str:
    """Formats verified crisis support resources without fabricating numbers."""
    res = VERIFIED_CRISIS_RESOURCES
    return (
        "It sounds like you are carrying a tremendous amount of pain or feeling overwhelmed right now. "
        "Please know that you do not have to carry this alone, and there is immediate, compassionate help available.\n\n"
        "### 🚨 Immediate Support Resources (24/7 & Confidential):\n"
        f"• **{res['us_canada_988']['name']} (US & Canada):** {res['us_canada_988']['contact']}\n"
        f"• **{res['crisis_text_line']['name']}:** {res['crisis_text_line']['contact']}\n"
        f"• **{res['trevor_project']['name']}:** {res['trevor_project']['contact']}\n"
        f"• **{res['veterans_crisis_line']['name']}:** {res['veterans_crisis_line']['contact']}\n"
        f"• **{res['international_emergency']['name']}:** {res['international_emergency']['contact']}\n\n"
        "I am an AI assistant and cannot provide medical or emergency intervention, but caring, trained professionals are standing by right now to listen."
    )
