import random

def generate_emoji(keyword: str) -> str:
    """
    Returns an emoji based on the user's input keyword.

    :param keyword: A string describing the emotion (e.g., "laugh", "cry").
    :return: A string containing an emoji.
    """
    emoji_dict = {
        "laugh": ["😂", "🤣", "😆", "😁"],
        "cry": ["😢", "😭", "😿"],
        "love": ["❤️", "😍", "😘", "💖"],
        "angry": ["😡", "😠", "🤬"],
        "happy": ["😊", "😃", "😄", "😁"],
        "sad": ["😞", "😔", "😟", "😢"],
        "surprised": ["😲", "😱", "🤯"],
        "cool": ["😎", "🕶️", "😏"],
        "confused": ["😕", "🤨", "😵"],
        "sleepy": ["😴", "💤", "🥱"]
    }

    # Convert input to lowercase and strip leading/trailing spaces
    normalized_keyword = keyword.strip().lower()

    # Return a random emoji if keyword is valid, otherwise return default 🤔
    return random.choice(emoji_dict.get(normalized_keyword, ["🤔"]))
