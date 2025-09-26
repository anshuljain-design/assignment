import re
from fastapi import HTTPException

# Emoji regex (same as Flutter)
emoji_regex = re.compile(
    r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|'
    r'[\U0001F1E0-\U0001F1FF]|[\u2600-\u26FF]|[\u2700-\u27BF]|[\U0001F900-\U0001F9FF]|'
    r'[\U0001F018-\U0001F0F5]|[\U0001F200-\U0001F2FF]|[\U0001F170-\U0001F251]|'
    r'[\U0001F004]|\U0001F0CF|[\U0001F700-\U0001F77F]|[\U0001F780-\U0001F7FF]|'
    r'[\U0001F800-\U0001F8FF]|[\U0001FA00-\U0001FA6F]|[\U0001FA70-\U0001FAFF]|'
    r'[\U0001FB00-\U0001FBFF]'
)


def contains_emoji(text: str) -> bool:
    return bool(emoji_regex.search(text))


def validate_email(email: str):
    if not email:
        raise HTTPException(400, detail="Please enter your email")
    if contains_emoji(email):
        raise HTTPException(400, detail="Email cannot contain emojis")
    if " " in email or ":" in email or ";" in email or "@" not in email or "." not in email:
        raise HTTPException(400, detail="Please enter a valid email")


def validate_name(name: str):
    if not name:
        raise HTTPException(400, detail="This field is required")
    if contains_emoji(name):
        raise HTTPException(400, detail="Name cannot contain emojis")
    if re.search(r"[0-9\s:;!?.,'\"()\[\]{}|\\/*+\-_=<>]", name):
        raise HTTPException(400, detail="Name cannot contain spaces, numbers, or special characters")
    if len(name) < 3 or len(name) > 20:
        raise HTTPException(400, detail="Name must be 3 to 20 characters long")


def validate_password(password: str):
    if not password:
        raise HTTPException(400, detail="Please enter your password")
    if contains_emoji(password):
        raise HTTPException(400, detail="Password cannot contain emojis")
    if len(password) < 6 or " " in password:
        raise HTTPException(400, detail="Password must be at least 6 characters without spaces")
    if len(password) > 20:
        raise HTTPException(400, detail="Password must be less than 20 characters")
    if not re.search(r"[0-9]", password):
        raise HTTPException(400, detail="Password must contain a number")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(400, detail="Password must contain a capital letter")
    if not re.search(r"[@#%&]", password):
        raise HTTPException(400, detail="Password must contain a special character (@#%&)")
