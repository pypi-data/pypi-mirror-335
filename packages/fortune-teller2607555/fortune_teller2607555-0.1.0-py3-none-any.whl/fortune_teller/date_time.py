import random

def rand_date_time(fortune):
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    
    random_day = random.choice(days_of_week)
    random_month = random.choice(months)
    random_year = random.randint(2025, 2060)
    
    return f"📅 On {random_day}, {random_month} {random.randint(1, 28)}, {random_year} — {fortune}"

fortunes = [
    "You will finally fix that bug you've been struggling with! 🐛",
    "A mysterious error message will lead you to a breakthrough. 💡",
    "Your code will run perfectly... on the first try! 🎉",
    "You will receive an unexpected but exciting coding challenge. 🚀",
    "Someone will compliment your Git commit messages. 📝"
]

print(rand_date_time(random.choice(fortunes)))