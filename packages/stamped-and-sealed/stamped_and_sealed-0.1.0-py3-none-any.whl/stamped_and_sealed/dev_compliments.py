import random

def dev_compliment(category: str) -> None:
    # Different compliments per category ("debugging", "coding", "motivation")
    compliments = {
        "debugging": [
            "You're a debugging pro!",
            "Your problem-solving skills are off the charts!",
            "Bugs fear you!",
            "You squash bugs like a pro!"
        ],
        "coding": [
            "Your code is so clean, even linting tools take the day off!",
            "You optimize like a Big O genius!",
            "Every line of your code radiates brilliance!",
            "Your code is a masterpiece in the making!"
        ],
        "motivation": [
            "What you're coding is legendary!",
            "Keep going! You're bringing your ideas to life!",
            "Every line of code is a step closer to greatness!",
            "You're turning ideas into reality!",
            "You always know how to git things done!",
            "You're building something amazing! Keep pushing forward!"
        ]
    }

    # Convert user input to lowercase and validate whether input is valid or not
    category = category.lower()
    if category in compliments:
        print(random.choice(compliments[category]))
    else:
        # If the category is invalid, it prompts the user with an error message
        print(f"Invalid category: '{category}'. Please choose from: {', '.join(compliments.keys())}")

