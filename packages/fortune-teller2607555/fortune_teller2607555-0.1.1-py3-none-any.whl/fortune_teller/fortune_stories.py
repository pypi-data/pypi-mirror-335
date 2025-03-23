import random 
def fortune_story(name):

    if not name.strip():
        return "Oops: You must provide a valid name ( • ᴖ • ｡) It cannot be empty!"

    stories= [
        f"{name} will wake up one day to find out that their body was taken over by AI. When {name} thought of something, {name}'s body would code it in an instance, but no matter what {name} did, there were always bugs...",
        f"The universe will open and {name} will see the infinte possiblites of error in their code. After looking through millions of possiblites, {name} finally will find the one universe where they will fix their code! Yay!",
        f"While in the ancient Libary, {name} found the ancient text of auto debugger,they opened the book and it read one line: in order to not have bugs one must not code",
        f"{name} will search far and wide in order to find the Grand AI that would save the world. After finding it, the world will turn into binary 1s and 0s, and {name} will become the Grand AI...spooky.",
        f"{name} will travel through the broken world filled with AI and robots. {name} will be the last savior of the World while also being the last software engineer..kinda cool ngl.",
        f"{name} will spend many sleepless nights looking for bugs in their code until {name} will finally notice they were the bug in the code..kafkaesque? You bet!",
        f"{name} will fight against the robot empire and beat them by saying the forbidden digit '1'!",
        f"{name} will break their computer by jumoing inside of it to debug their code and will never be seen again..whaaaaaaaat" 
    ]
    return random.choice(stories)