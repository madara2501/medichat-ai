import re

# 🔴 Strong single triggers (Instant Critical)
CRITICAL_PATTERNS = [
    r"heart attack",
    r"cardiac arrest",
    r"stroke",
    r"not breathing",
    r"cannot breathe",
    r"can't breathe",
    r"unconscious",
    r"severe bleeding",
    r"vomiting blood",
    r"overdose",
    r"poisoning",
    r"anaphylaxis",
]

# ⚠ Moderate danger keywords
HIGH_RISK_WORDS = [
    "chest pain",
    "chest tightness",
    "pressure in chest",
    "shortness of breath",
    "difficulty breathing",
    "gasping",
    "face drooping",
    "slurred speech",
    "sudden weakness",
    "one side numb",
    "seizure",
    "convulsion",
    "worst headache",
    "unbearable pain",
]

# Bengali critical triggers
BENGALI_CRITICAL = [
    "অজ্ঞান",
    "শ্বাস বন্ধ",
    "শ্বাস নিচ্ছে না",
    "শ্বাস পাচ্ছে না",
    "বিষ খাওয়া",
    "বিষ খেয়েছি",
    "বমিতে রক্ত",
    "রক্ত বমি",
    "অতিরিক্ত রক্তপাত",
    "রক্ত বন্ধ হচ্ছে না",
    "হার্ট অ্যাটাক",
    "স্ট্রোক",
    "হৃদযন্ত্র বন্ধ",
    "মৃত্যুর মতো অবস্থা",
    "দুর্ঘটনা গুরুতর",
    "গুরুতর মাথায় আঘাত",
    "বুক ধড়ফড় বন্ধ",
    "খুব তীব্র শ্বাসকষ্ট",
]

# Bengali high-risk words
BENGALI_HIGH = [
    "বুকে ব্যথা",
    "তীব্র বুকে ব্যথা",
    "বুক চাপ লাগছে",
    "শ্বাস নিতে কষ্ট",
    "হঠাৎ দুর্বলতা",
    "এক পাশ অবশ",
    "মুখ বেঁকে যাওয়া",
    "কথা জড়িয়ে যাওয়া",
    "হঠাৎ কথা বন্ধ",
    "খিঁচুনি",
    "মাথা ফেটে যাচ্ছে",
    "সবচেয়ে খারাপ মাথা ব্যথা",
    "অসহ্য ব্যথা",
    "পেটের তীব্র ব্যথা",
    "বারবার অজ্ঞান হওয়া",
    "হঠাৎ চোখে দেখতে না পাওয়া",
    "হাত-পা অবশ",
    "অতিরিক্ত ঘাম ও বুক ব্যথা",
]


def check_emergency(user_input):
    text = user_input.lower()
    score = 0

    # 🔴 Instant Critical Check
    for pattern in CRITICAL_PATTERNS:
        if re.search(pattern, text):
            return "Critical", 10

    for word in BENGALI_CRITICAL:
        if word in text:
            return "Critical", 10

    # ⚠ Base scoring
    for word in HIGH_RISK_WORDS:
        if word in text:
            score += 3

    for word in BENGALI_HIGH:
        if word in text:
            score += 3

    # Combination logic (English)
    if "chest" in text and "breath" in text:
        score += 4

    if "weakness" in text and "speech" in text:
        score += 4

    if ("chest pain" in text or "chest tightness" in text) and \
       ("sweating" in text or "nausea" in text or "vomiting" in text):
        score += 5

    if "chest pain" in text and "left arm" in text:
        score += 5

    if "chest pain" in text and "dizzy" in text:
        score += 4

    if ("face drooping" in text or "face numb" in text) and \
       ("slurred speech" in text or "cannot speak" in text):
        score += 6

    if "one side" in text and ("weakness" in text or "numb" in text):
        score += 5

    if "sudden vision loss" in text and "severe headache" in text:
        score += 5

    if "asthma" in text and ("cannot breathe" in text or "can't breathe" in text):
        score += 6

    if "blue lips" in text and "breathing" in text:
        score += 6

    if "difficulty breathing" in text and "unconscious" in text:
        score += 7

    if "deep cut" in text and "bleeding" in text:
        score += 5

    if "accident" in text and "bleeding" in text:
        score += 6

    if "high fever" in text and "confusion" in text:
        score += 5

    if "high fever" in text and "very weak" in text:
        score += 4

    if "fainted" in text and "chest pain" in text:
        score += 6

    if "fainted" in text and "palpitations" in text:
        score += 5

    # Bengali combination logic
    if "বুক" in text and "ব্যথা" in text and "ঘাম" in text:
        score += 5

    if "মুখ" in text and "বেঁকে" in text and "কথা" in text:
        score += 6

    if "শ্বাস" in text and "অজ্ঞান" in text:
        score += 7

    # Final score interpretation
    if score >= 7:
        return "Critical", score
    elif score >= 4:
        return "High Risk", score

    return None, 0