import random

def dev_fortune_cookie(category: str = "general") -> str:
    """
    Returns a random 'fortune' for the developer.

    :param category: Type of fortune ('general', 'bug', 'debug', 'success').
    :return: A string containing the fortune message.
    """
    fortunes = {
        "general": [
            "🚀 Today, your code will run on the first try! (Maybe.)",
            "🐛 A mysterious bug will appear... and then disappear by itself.",
            "💾 Commit often. Debug once. Relax always.",
        ],
        "bug": [
            "🔥 Today's stack overflow question count: HIGH!",
            "🦠 That one bug you ignored? It's back. And it brought friends.",
            "📌 If it compiles, it doesn't mean it works.",
        ],
        "debug": [
            "🔄 Have you tried turning it off and on again?",
            "🐍 Your Python code is so good, even Guido would approve.",
            "🛠 Debugging is like being the detective in a crime movie where YOU are the murderer.",
        ],
        "success": [
            "🎉 Congratulations! Today is a bug-free day... hopefully.",
            "🚀 Your last refactor made the code 10x cleaner!",
            "🌟 You are officially a 'Senior Debugger' now!",
        ]
    }

    return "\n🔮 Developer Fortune: " + random.choice(fortunes.get(category, fortunes["general"])) + "\n"
