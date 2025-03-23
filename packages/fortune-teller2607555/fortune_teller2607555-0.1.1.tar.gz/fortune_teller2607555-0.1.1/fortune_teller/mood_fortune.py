import random

def mood_fortune(mood: str = "positive") -> str:
    fortunes = {
        "positive": [
            "Your next 🏗️ `build` will succeed on the first try. 🚀",
            "You will finally master `regex` and feel like a 🧙‍♂️.",
            "Your next `git pull` will not cause a 🔥 merge conflict. Rejoice!",
            "A PR review will leave a 🌟 `LGTM` instead of nitpicks.",
            "Your bug 🐛 will fix itself while you’re making ☕.",
            "You will find an obscure `CLI` command that saves you ⏳.",
            "Your next `Docker` container will work… without 😱 debugging.",
        ],
        "funny": [
            "You will find a `fix` for your bug… in a 2008 Stack Overflow post. 🕰️",
            "Your code will work on your machine… and nowhere else. 🏠💻",
            "Your next `npm install` will require a fresh OS install. 😭💾",
            "Your `print(debug)` statement will fix everything… until you remove it. 🧐",
            "You’ll spend 3 hours debugging… and it was just `cAsE sEnSiTiViTy`. 🤦‍♂️",
            "Your next feature request will be 'Just add AI'. 🤖✨",
            "Your `README.md` will be out of date before you hit save. 📜🔥",
        ],
        "cursed": [
            "You will find a `TODO` in the code… last updated in 2015. ☠️",
            "Your PR will break everything… and the only test that fails is ✅ `test_example.py`.",
            "Your `git rebase` will go horribly wrong… but you’ll pretend it didn’t. 😅",
            "Your `database migration` will fail… and no one knows why. 🕵️‍♂️🗄️",
            "Your `deploy` will work fine… until 🌙 when it mysteriously crashes.",
            "Your next `hotfix` will become a permanent feature. 👀",
            "A manager will say 'This will be a small change'. 🚨",
        ],
        "motivational": [
            "You are not an 'imposter' — you are a developer. Believe in yourself. 💪🚀",
            "Every great coder was once a beginner. Keep pushing! 🔥💡",
            "Your past mistakes do not define your future commits. 🌱✨",
            "You are one Google search away from solving your problem. 🔍💡",
            "Debugging is just another word for learning. Stay curious! 🧠💻",
            "The best way to write better code is to keep writing code. 🏗️📜",
            "You got this! One line at a time, one function at a time. Keep building. 💪💻",
        ]
    }

    if mood in fortunes:
        return random.choice(fortunes[mood])
    else:
        return (f"Oops: '{mood}' is not from our list ( • ᴖ • ｡)"
            f"Please pick from this list of moods next time you decide to choose this function: positive, funny, cursed, motivational.")